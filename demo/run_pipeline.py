import argparse
from pathlib import Path


def _asset_status(args):
    assets = {
        "YOLO staff-detector weight": Path(args.yolo_model),
        "CRNN checkpoint": Path(args.crnn_model),
        "CRNN tokenizer": Path(args.tokenizer),
    }
    if not args.skip_midi:
        assets["semantic converter JAR"] = Path(args.converter_jar)
    return assets


def check_assets(args) -> bool:
    assets = _asset_status(args)
    all_present = True
    print("OMR demo — asset check")
    print("=" * 60)
    for label, path in assets.items():
        exists = path.is_file()
        all_present &= exists
        state = "READY" if exists else "MISSING"
        print(f"{state:38} {label}: {path}")
    print("=" * 60)
    if not all_present:
        print("Add the missing files listed in models/README.md or assets/README.md before running the demo.")
    return all_present


def main():
    parser = argparse.ArgumentParser(description="Run the end-to-end sheet-music OMR pipeline.")
    parser.add_argument("--image", help="Input score image")
    parser.add_argument("--output", default="demo_output", help="Pipeline output directory")
    parser.add_argument("--yolo-model", default="models/yolo/best.pt")
    parser.add_argument("--crnn-model", default="models/crnn/best_model.pt")
    parser.add_argument("--tokenizer", default="models/crnn/tokenizer.json")
    parser.add_argument("--converter-jar", default="assets/omr-3.0-SNAPSHOT.jar")
    parser.add_argument("--conf", type=float, default=0.55)
    parser.add_argument("--bpm", type=float, default=120.0)
    parser.add_argument("--num-parts", type=int, default=1)
    parser.add_argument("--skip-midi", action="store_true", help="Run staff detection and CRNN recognition only")
    parser.add_argument("--check-only", action="store_true", help="Check required runtime files and exit")
    args = parser.parse_args()

    assets_ok = check_assets(args)
    if args.check_only:
        return
    if not args.image:
        parser.error("--image is required unless --check-only is used")
    if not assets_ok:
        raise SystemExit("Demo cannot start because one or more required runtime files are missing.")

    from demo.yolo_crop import detect_and_crop
    from demo.score_yolo_crnn import process_directory

    output = Path(args.output)
    detection_dir = output / "detection"
    semantic_dir = output / "semantic"
    midi_dir = output / "midi"

    print("\n[1/3] Detecting staff regions")
    detect_and_crop(args.image, args.yolo_model, str(detection_dir), args.conf)

    print("\n[2/3] Recognizing music symbols")
    process_directory(
        str(detection_dir / "cropped_staves"),
        str(semantic_dir),
        args.crnn_model,
        args.tokenizer,
    )

    if args.skip_midi:
        print(f"\nRecognition complete: {semantic_dir}")
        return

    print("\n[3/3] Converting recognition results to MIDI")
    from postprocess.semantic2midi import process_semantic_files

    final_midi = process_semantic_files(
        str(semantic_dir),
        str(midi_dir),
        args.converter_jar,
        args.bpm,
        args.num_parts,
    )
    print(f"\nDemo complete. MIDI output: {final_midi}")


if __name__ == "__main__":
    main()
