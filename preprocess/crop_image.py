import cv2
import numpy as np
from pathlib import Path
from pdf2image import convert_from_path
import os

def crop_music_score(input_path, output_dir, poppler_path=None, target_height=128, page_counter=1):
    """
    Convert PDF to images, crop each page to a specified height while preserving the musical content.
    """
    # Check if input file exists
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    # Convert PDF to images
    try:
        pages = convert_from_path(
            input_path, 
            dpi=80,  # Higher DPI for better quality
            poppler_path=poppler_path
        )
    except Exception as e:
        raise ValueError(f"Error converting PDF to images: {e}")

    for i, page in enumerate(pages):
        # Convert PIL Image to numpy array and BGR format
        image = cv2.cvtColor(np.array(page), cv2.COLOR_RGB2BGR)

        if image is None:
            print(f"Warning: Could not convert page {i+1}")
            continue

        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # Use adaptive thresholding for binarization
        adaptive_thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
        )

        # Find non-zero points (actual content)
        non_zero = cv2.findNonZero(adaptive_thresh)
        if non_zero is None:
            print(f"Warning: No content found in page {i+1}")
            continue

        # Get bounds of the content
        x, y, w, h = cv2.boundingRect(non_zero)

        # Add padding around the content
        padding = int(h * 0.2)  # 20% padding
        top = max(0, y - padding)
        bottom = min(image.shape[0], y + h + padding)

        # Crop the image
        cropped = image[top:bottom, :]

        # Resize to target height while maintaining aspect ratio
        aspect_ratio = (cropped.shape[1] / cropped.shape[0])
        new_width = int(target_height * aspect_ratio)
        resized = cv2.resize(cropped, (new_width, target_height), interpolation=cv2.INTER_CUBIC)

        # Save the result with a unique page number
        output_path = os.path.join(output_dir, f"page_{page_counter}.png")
        cv2.imwrite(output_path, resized)
        print(f"Processed page {i+1} from {input_path}, saved to {output_path}")

        # Increment the page counter
        page_counter += 1

    return page_counter



def main():
    import argparse

    parser = argparse.ArgumentParser(description="Rasterize and crop PDF music pages to a fixed image height.")
    parser.add_argument("--input-dir", required=True, help="Directory containing PDF files, recursively")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--poppler-path", default=None, help="Optional Poppler bin directory on Windows")
    parser.add_argument("--target-height", type=int, default=128)
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    pdf_files = sorted(input_dir.rglob("*.pdf"))
    if not pdf_files:
        raise SystemExit(f"No PDF files found under {input_dir}")

    page_counter = 1
    for pdf_file in pdf_files:
        page_counter = crop_music_score(
            str(pdf_file),
            str(output_dir),
            args.poppler_path,
            target_height=args.target_height,
            page_counter=page_counter,
        )

    print(f"Processing complete. Wrote {page_counter - 1} page image(s).")


if __name__ == "__main__":
    main()
