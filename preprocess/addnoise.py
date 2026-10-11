import argparse
from pathlib import Path

import numpy as np
from PIL import Image


def add_random_noise(image, noise_factor=0.3):
    img_array = np.array(image)
    noise = np.random.normal(0, 1, img_array.shape) * 255 * noise_factor
    noisy_img = np.clip(img_array + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(noisy_img)


def create_noisy_dataset(source_dir, target_dir, noise_factor=0.3):
    source = Path(source_dir)
    target = Path(target_dir)
    target.mkdir(parents=True, exist_ok=True)

    for folder in sorted(source.iterdir()):
        if not folder.is_dir():
            continue
        target_folder = target / folder.name
        target_folder.mkdir(parents=True, exist_ok=True)
        for image_path in folder.glob("*.png"):
            image = Image.open(image_path).convert("RGB")
            add_random_noise(image, noise_factor).save(target_folder / image_path.name)


def main():
    parser = argparse.ArgumentParser(description="Create a noisy copy of a packaged OMR image dataset.")
    parser.add_argument("--source", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--noise-factor", type=float, default=0.3)
    args = parser.parse_args()
    create_noisy_dataset(args.source, args.output, args.noise_factor)


if __name__ == "__main__":
    main()
