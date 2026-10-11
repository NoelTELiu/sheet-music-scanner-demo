import cv2
import os
from datetime import datetime
from yolo.staff_detector import StaffDetector

def crop_and_save_staves(image, staff_boxes, output_dir):
    """
    Crop detected staff regions from the image and save them as individual files
    """
    cropped_paths = []
    
    # Create directory for cropped images if it doesn't exist
    crops_dir = os.path.join(output_dir, 'cropped_staves')
    os.makedirs(crops_dir, exist_ok=True)
    
    # Process each detected staff
    for i, staff in enumerate(staff_boxes, 1):
        bbox = staff['bbox']
        
        # Convert coordinates to integers
        x1, y1, x2, y2 = map(int, bbox)
        
        # Add small padding around the staff
        padding = 10
        y1 = max(0, y1 - padding)
        y2 = min(image.shape[0], y2 + padding)
        x1 = max(0, x1 - padding)
        x2 = min(image.shape[1], x2 + padding)
        
        # Crop the staff region
        cropped_staff = image[y1:y2, x1:x2]
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        crop_filename = f"staff_{i}_conf_{staff['confidence']:.2f}_{timestamp}.jpg"
        crop_path = os.path.join(crops_dir, crop_filename)
        
        # Save cropped image
        cv2.imwrite(crop_path, cropped_staff)
        cropped_paths.append(crop_path)
        
        print(f"Saved cropped staff {i} to: {crop_path}")
    
    return cropped_paths

def test_detector(detector, image_path, save_path=None):
    """
    Test detector on a single image, display and save results
    """
    # Read image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not read image at {image_path}")
        return
    
    # Get detections
    staff_boxes = detector.detect(image)
    
    # Create a copy for drawing
    annotated_image = image.copy()
    
    # Draw detections
    for staff in staff_boxes:
        bbox = staff['bbox']
        conf = staff['confidence']
        
        # Draw rectangle
        cv2.rectangle(
            annotated_image,
            (int(bbox[0]), int(bbox[1])),
            (int(bbox[2]), int(bbox[3])),
            (0, 255, 0),
            2
        )
        
        # Draw confidence score
        cv2.putText(
            annotated_image,
            f"{conf:.2f}",
            (int(bbox[0]), int(bbox[1] - 10)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 0),
            2
        )
    
    # Save the annotated image if save_path is provided
    if save_path:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # Save image
        cv2.imwrite(save_path, annotated_image)
        print(f"Saved annotated image to: {save_path}")
        
        # Crop and save individual staff images
        cropped_paths = crop_and_save_staves(image, staff_boxes, os.path.dirname(save_path))
    
    # Print detection results
    print(f"\nDetection Results for {os.path.basename(image_path)}:")
    print(f"Number of staff lines detected: {len(staff_boxes)}")
    for i, staff in enumerate(staff_boxes, 1):
        print(f"Staff {i}: Confidence = {staff['confidence']:.2f}")
    
    return staff_boxes

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Evaluate a trained YOLO staff detector on one image.")
    parser.add_argument("--image", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--output-dir", default="detection_results")
    args = parser.parse_args()

    detector = StaffDetector(args.model)
    os.makedirs(args.output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = os.path.splitext(os.path.basename(args.image))[0]
    save_path = os.path.join(args.output_dir, f"{base_name}_detected_{timestamp}.jpg")
    test_detector(detector, args.image, save_path)


if __name__ == "__main__":
    main()
