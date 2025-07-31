import os
import shutil
from pathlib import Path

def extract_address_images():
    """
    Extract address_first_cropped_img.png files from folders inside uploads
    and save them in a root directory folder called 'address images'
    """
    
    # Define paths
    uploads_dir = Path("uploads")
    output_dir = Path("address images")
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(exist_ok=True)
    
    # Check if uploads directory exists
    if not uploads_dir.exists():
        print(f"Error: {uploads_dir} directory not found!")
        return
    
    # Counter for processed images
    processed_count = 0
    missing_count = 0
    
    # Iterate through all subdirectories in uploads
    for folder in uploads_dir.iterdir():
        if folder.is_dir():
            # Look for the target image file
            target_image = folder / "address_first_cropped_img.png"
            
            if target_image.exists():
                # Create destination filename using folder name
                folder_name = folder.name
                destination = output_dir / f"{folder_name}.png"
                
                try:
                    # Copy the image to the destination
                    shutil.copy2(target_image, destination)
                    print(f"✓ Copied: {folder_name}")
                    processed_count += 1
                except Exception as e:
                    print(f"✗ Error copying {folder_name}: {e}")
            else:
                print(f"✗ Missing address_first_cropped_img.png in: {folder.name}")
                missing_count += 1
    
    # Print summary
    print(f"\n--- Summary ---")
    print(f"Successfully processed: {processed_count} images")
    print(f"Missing images: {missing_count}")
    print(f"Images saved to: {output_dir.absolute()}")

if __name__ == "__main__":
    extract_address_images()