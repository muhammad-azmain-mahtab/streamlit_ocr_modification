import pandas as pd
import os
from pathlib import Path

def create_filtered_csv():
    """
    Create a new CSV with only specified columns and add image paths
    """
    
    # Read the original CSV
    csv_file = "nid_infos_compared_31-07-25_12-14.csv"
    df = pd.read_csv(csv_file)
    
    # Select only the required columns
    required_columns = ['id', 'upload_id', 'detected_blur', 'address_ocr_v6_accuracy', 'address_ocr_v6']
    
    # Filter the dataframe to keep only required columns
    filtered_df = df[required_columns].copy()
    
    # Define the address images folder
    address_images_folder = Path("address images")
    
    # Add image_path column
    def get_image_path(upload_id):
        """Get the image path for a given upload_id"""
        if pd.isna(upload_id):
            return ""
        
        image_file = address_images_folder / f"{upload_id}.png"
        if image_file.exists():
            return str(image_file)
        else:
            return ""
    
    # Apply the function to create the image_path column
    filtered_df['image_path'] = filtered_df['upload_id'].apply(get_image_path)
    
    # Save the new CSV
    output_file = "filtered_nid_data_with_images.csv"
    filtered_df.to_csv(output_file, index=False)
    
    # Print summary
    total_rows = len(filtered_df)
    rows_with_images = len(filtered_df[filtered_df['image_path'] != ""])
    rows_without_images = total_rows - rows_with_images
    
    print(f"--- CSV Processing Complete ---")
    print(f"Original CSV: {csv_file}")
    print(f"New CSV: {output_file}")
    print(f"Total rows: {total_rows}")
    print(f"Rows with images: {rows_with_images}")
    print(f"Rows without images: {rows_without_images}")
    print(f"Columns included: {', '.join(required_columns + ['image_path'])}")
    
    # Show first few rows
    print(f"\nFirst 5 rows of the new CSV:")
    print(filtered_df.head().to_string(index=False))

if __name__ == "__main__":
    create_filtered_csv()
