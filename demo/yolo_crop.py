import argparse
from pathlib import Path

import cv2

from yolo.staff_detector import StaffDetector


def crop_and_save_staves(image, staff_boxes, output_dir: Path):
    crops_dir = output_dir / "cropped_staves"
    crops_dir.mkdir(parents=True, exist_ok=True)
    cropped_paths = []

    for i, staff in enumerate(staff_boxes, 1):
        x1, y1, x2, y2 = map(int, staff["bbox"])
        padding = 10
        y1 = max(0, y1 - padding)
        y2 = min(image.shape[0], y2 + padding)
        x1 = max(0, x1 - padding)
        x2 = min(image.shape[1], x2 + padding)

        cropped_staff = image[y1:y2, x1:x2]
        crop_path = crops_dir / f"staff_{i:02d}.jpg"
        if not cv2.imwrite(str(crop_path), cropped_staff):
            raise RuntimeError(f"Failed to write crop: {crop_path}")
        cropped_paths.append(crop_path)

    return cropped_paths


def detect_and_crop(image_path: str, model_path: str, output_dir: str, conf: float = 0.55):
    image_file = Path(image_path)
    if not image_file.is_file():
        raise FileNotFoundError(f"Input image not found: {image_file}")

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    image = cv2.imread(str(image_file))
    if image is None:
        raise ValueError(f"Could not read image: {image_file}")

    detector = StaffDetector(model_path)
    staff_boxes = detector.detect(image, conf=conf)
    if not staff_boxes:
        raise RuntimeError(
            "No staff regions were detected. Check the trained YOLO weight or lower --conf."
        )

    annotated = image.copy()
    for staff in staff_boxes:
        x1, y1, x2, y2 = map(int, staff["bbox"])
        confidence = staff["confidence"]
        cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(
            annotated,
            f"{confidence:.2f}",
            (x1, max(15, y1 - 8)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 0),
            2,
        )

    annotated_path = output / f"{image_file.stem}_detected.jpg"
    cv2.imwrite(str(annotated_path), annotated)
    crops = crop_and_save_staves(image, staff_boxes, output)

    print(f"Staff regions detected: {len(crops)}")
    print(f"Detection preview: {annotated_path}")
    print(f"Staff crops: {output / 'cropped_staves'}")
    return crops


def main():
    parser = argparse.ArgumentParser(description="Detect staff regions and save individual staff crops.")
    parser.add_argument("--image", required=True, help="Input score image")
    parser.add_argument("--model", required=True, help="Trained YOLO staff-detector weight (.pt)")
    parser.add_argument("--output", default="demo_output/detection", help="Output directory")
    parser.add_argument("--conf", type=float, default=0.55, help="Detection confidence threshold")
    args = parser.parse_args()

    detect_and_crop(args.image, args.model, args.output, args.conf)


if __name__ == "__main__":
    main()
