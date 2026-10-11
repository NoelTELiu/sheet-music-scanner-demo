import argparse

from yolo.staff_detector import train_staff_detector


def main():
    parser = argparse.ArgumentParser(description="Train YOLOv8 for musical staff-region detection.")
    parser.add_argument("--data", default="yolo/data.yaml", help="YOLO dataset YAML")
    parser.add_argument("--epochs", type=int, default=300)
    args = parser.parse_args()

    print(f"Starting training for {args.epochs} epochs using {args.data}")
    results = train_staff_detector(args.data, args.epochs)
    print("Training completed.")
    print(f"Best model: {results.best}")


if __name__ == "__main__":
    main()
