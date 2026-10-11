import argparse
import json
import logging
from pathlib import Path
from typing import Dict

import torch
import torchvision.transforms as transforms
from PIL import Image

from crnn.train_crnn_semantic import CRNN

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_tokenizer(tokenizer_path: str) -> Dict:
    path = Path(tokenizer_path)
    if not path.is_file():
        raise FileNotFoundError(f"Tokenizer not found: {path}")
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    required = {"symbol_to_id", "id_to_symbol"}
    missing = required.difference(data)
    if missing:
        raise ValueError(f"Tokenizer is missing keys: {sorted(missing)}")
    return data


def decode_prediction(output: torch.Tensor, tokenizer_data: Dict) -> str:
    best_path = torch.argmax(output, dim=2).squeeze(0)
    id_to_symbol = {int(k): v for k, v in tokenizer_data["id_to_symbol"].items()}

    previous = None
    decoded = []
    for idx in best_path:
        idx = idx.item()
        if idx != 0 and idx != previous:
            decoded.append(id_to_symbol[idx])
        previous = idx
    return "\t".join(decoded)


def predict_single_image(image_path: Path, model, tokenizer_data: Dict, device: str) -> str:
    transform = transforms.Compose([transforms.Grayscale(), transforms.ToTensor()])
    image = Image.open(image_path)
    target_height = 128
    aspect_ratio = image.size[0] / image.size[1]
    target_width = int(target_height * aspect_ratio)
    image = image.resize((target_width, target_height))
    tensor = transform(image).unsqueeze(0).to(device)

    model.eval()
    with torch.no_grad():
        output = model(tensor)
    return decode_prediction(output, tokenizer_data)


def load_model(model_path: str, tokenizer_data: Dict, device: str):
    path = Path(model_path)
    if not path.is_file():
        raise FileNotFoundError(f"CRNN checkpoint not found: {path}")

    checkpoint = torch.load(path, map_location=device, weights_only=False)
    vocab_size = len(tokenizer_data["symbol_to_id"])
    checkpoint_vocab = checkpoint.get("vocabulary_size") if isinstance(checkpoint, dict) else None
    if checkpoint_vocab is not None and checkpoint_vocab != vocab_size:
        raise ValueError(
            f"Checkpoint/tokenizer mismatch: checkpoint vocabulary={checkpoint_vocab}, "
            f"tokenizer vocabulary={vocab_size}."
        )

    dropout = checkpoint.get("dropout_rate", 0.5) if isinstance(checkpoint, dict) else 0.5
    model = CRNN(vocab_size, dropout_rate=dropout).to(device)
    state_dict = checkpoint["model_state_dict"] if isinstance(checkpoint, dict) else checkpoint
    model.load_state_dict(state_dict)
    model.eval()
    return model


def process_directory(input_dir: str, output_dir: str, model_path: str, tokenizer_path: str):
    input_path = Path(input_dir)
    if not input_path.is_dir():
        raise FileNotFoundError(f"Cropped-staff directory not found: {input_path}")

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    tokenizer_data = load_tokenizer(tokenizer_path)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info("Inference device: %s", device)
    model = load_model(model_path, tokenizer_data, device)

    image_files = sorted(
        path for path in input_path.iterdir()
        if path.suffix.lower() in {".jpg", ".jpeg", ".png"}
    )
    if not image_files:
        raise RuntimeError(f"No cropped staff images found in {input_path}")

    for idx, image_path in enumerate(image_files, 1):
        prediction = predict_single_image(image_path, model, tokenizer_data, device)
        semantic_path = output_path / f"{image_path.stem}.semantic"
        semantic_path.write_text(prediction, encoding="utf-8")
        logger.info("Recognized %s (%d/%d)", image_path.name, idx, len(image_files))

    return list(output_path.glob("*.semantic"))


def main():
    parser = argparse.ArgumentParser(description="Recognize semantic music-symbol sequences from staff crops.")
    parser.add_argument("--input-dir", default="demo_output/detection/cropped_staves")
    parser.add_argument("--output-dir", default="demo_output/semantic")
    parser.add_argument("--model", required=True, help="CRNN checkpoint (.pt)")
    parser.add_argument("--tokenizer", required=True, help="Tokenizer JSON from the same training run")
    args = parser.parse_args()

    process_directory(args.input_dir, args.output_dir, args.model, args.tokenizer)


if __name__ == "__main__":
    main()
