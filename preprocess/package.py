import argparse
import shutil
from pathlib import Path


def package_dataset(labels_dir: str, images_dir: str, output_dir: str):
    labels = Path(labels_dir)
    images = Path(images_dir)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    image_map = {p.stem: p for p in images.glob("*.png")}
    matched = 0
    for semantic_file in sorted(labels.glob("*.semantic")):
        image_file = image_map.get(semantic_file.stem)
        if image_file is None:
            continue
        sample_dir = output / semantic_file.stem
        sample_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(semantic_file, sample_dir / semantic_file.name)
        shutil.copy2(image_file, sample_dir / image_file.name)
        matched += 1

    print(f"Packaged {matched} image/label pair(s) into {output}")


def main():
    parser = argparse.ArgumentParser(description="Package matching PNG and .semantic files into sample folders.")
    parser.add_argument("--labels", required=True, help="Directory containing .semantic files")
    parser.add_argument("--images", required=True, help="Directory containing matching .png files")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    package_dataset(args.labels, args.images, args.output)


if __name__ == "__main__":
    main()
