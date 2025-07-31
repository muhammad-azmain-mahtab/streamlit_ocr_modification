import cv2
import numpy as np
import os
import pandas as pd
from tqdm import tqdm
from math import degrees, atan2

def detect_blur_level(image_path):
    """
    Detect blur level using Laplacian variance and simple contour detection.
    Returns the blur score and a label ('blur' or 'clear').
    """
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Could not read image {image_path}")
        return None

    # Compute variance of Laplacian
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edge_var = cv2.Laplacian(gray, cv2.CV_64F).var()

    threshold_v = 300  # You can adjust this threshold
    if edge_var < threshold_v:
        return edge_var, "blur"

    # Simple detection: count contours as proxy for boxes
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    num_boxes = len(contours)

    if num_boxes <= 8:
        return edge_var, "blur"
    else:
        return edge_var, "clear"
    
def get_line_angle(x1, y1, x2, y2):
    angle = degrees(atan2(y2 - y1, x2 - x1))
    return angle % 180  # keep within [0, 180)

def detect_card_angle_fixed(image_path, output_dir=None):
    """
    Detect card angle using Hough Line Transform
    """
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Could not read image {image_path}")
        return None

    original_img = img.copy()
    height, width = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)

    # Probabilistic Hough Transform — gives endpoints
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=80, minLineLength=50, maxLineGap=10)

    if lines is None or len(lines) == 0:
        return 0

    # Calculate angles for each line
    angles = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        angle = get_line_angle(x1, y1, x2, y2)
        # Only consider angles in a valid range, e.g., ignore near-horizontal lines
        if 10 < angle < 170:  # avoid noise
            angles.append(angle)

    if not angles:
        return 0

    # Get the dominant rotation angle (most common bin)
    hist = np.histogram(angles, bins=180, range=(0, 180))
    bin_centers = (hist[1][:-1] + hist[1][1:]) / 2
    dominant_angle = bin_centers[np.argmax(hist[0])]

    return dominant_angle

def process_images_and_create_csv():
    """
    Process all images in the address images folder and create CSV with results
    """
    # Define the image directory path
    image_dir = "address images"
    
    # Check if directory exists
    if not os.path.exists(image_dir):
        print(f"Error: Directory {image_dir} does not exist")
        return
    
    # Get all image files
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']
    image_files = []
    
    for file in os.listdir(image_dir):
        if any(file.lower().endswith(ext) for ext in image_extensions):
            image_files.append(file)
    
    if not image_files:
        print("No image files found in the directory")
        return
    
    print(f"Found {len(image_files)} images to process")
    
    # Process each image with progress bar
    results = []
    
    for image_file in tqdm(image_files, desc="Processing images", unit="image"):
        image_path = os.path.join(image_dir, image_file)
        
        # Detect blur level
        blur_score, blur_label = detect_blur_level(image_path)

        # Detect angle
        detected_angle = detect_card_angle_fixed(image_path)

        # Store results
        results.append({
            'image_name': image_file,
            'detected_blur': blur_score,
            'blur_label': blur_label,
            'detected_angle': detected_angle
        })
    
    # Create DataFrame and save to CSV
    df = pd.DataFrame(results)
    csv_path = "image_analysis_results.csv"
    df.to_csv(csv_path, index=False)
    
    print(f"\nProcessing complete! Results saved to: {csv_path}")
    print(f"Total images processed: {len(results)}")
    print("\nFirst few results:")
    print(df.head())

if __name__ == "__main__":
    process_images_and_create_csv()