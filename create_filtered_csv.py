import pandas as pd
import os
from pathlib import Path

def create_filtered_csv():
    """
    Create a new CSV with only specified columns and add image paths
    Use blur and angle values from image_analysis_results.csv
    """
    
    # Read the original CSV
    csv_file = "nid_infos_compared_31-07-25_12-14.csv"
    df = pd.read_csv(csv_file)
    
    # Read the image analysis results CSV
    image_analysis_file = "image_analysis_results.csv"
    image_analysis_df = pd.read_csv(image_analysis_file)
    
    # Remove .png extension from image_name for matching
    image_analysis_df['upload_id_match'] = image_analysis_df['image_name'].str.replace('.png', '')
    
    # Select only the required columns from original CSV (excluding blur and angle)
    required_columns = ['id', 'upload_id', 'address_ocr_v6_accuracy', 'address_ocr_v6']
    
    # Filter the dataframe to keep only required columns
    filtered_df = df[required_columns].copy()
    
    # Merge with image analysis data to get blur and angle values
    merged_df = filtered_df.merge(
        image_analysis_df[['upload_id_match', 'detected_blur', 'detected_angle']], 
        left_on='upload_id', 
        right_on='upload_id_match', 
        how='left'
    )
    
    # Drop the temporary matching column
    merged_df = merged_df.drop('upload_id_match', axis=1)
    
    # Reorder columns to match the original order
    column_order = ['id', 'upload_id', 'detected_blur', 'detected_angle', 'address_ocr_v6_accuracy', 'address_ocr_v6']
    filtered_df = merged_df[column_order].copy()
    
def create_filtered_csv(use_original_blur_angle=False):
    """
    Create a new CSV with only specified columns and add image paths
    Use blur and angle values from image_analysis_results.csv (default)
    Or, if use_original_blur_angle=True, keep detected_blur and detected_angle from original csv_file.
    """
    # Read the original CSV
    csv_file = "nid_infos_compared_31-07-25_12-14.csv"
    df = pd.read_csv(csv_file)

    required_columns = ['id', 'upload_id', 'address_ocr_v6_accuracy', 'address_ocr_v6']

    if use_original_blur_angle:
        # If original CSV has detected_blur and detected_angle, keep them
        if 'detected_blur' in df.columns and 'detected_angle' in df.columns:
            filtered_df = df[required_columns + ['detected_blur', 'detected_angle']].copy()
            # Reorder columns
            column_order = ['id', 'upload_id', 'detected_blur', 'detected_angle', 'address_ocr_v6_accuracy', 'address_ocr_v6']
            filtered_df = filtered_df[column_order].copy()
        else:
            print("Original CSV does not contain 'detected_blur' and 'detected_angle'.")
            return
    else:
        # Read the image analysis results CSV
        image_analysis_file = "image_analysis_results.csv"
        image_analysis_df = pd.read_csv(image_analysis_file)
        # Remove .png extension from image_name for matching
        image_analysis_df['upload_id_match'] = image_analysis_df['image_name'].str.replace('.png', '')
        # Filter the dataframe to keep only required columns
        filtered_df = df[required_columns].copy()
        # Merge with image analysis data to get blur and angle values
        merged_df = filtered_df.merge(
            image_analysis_df[['upload_id_match', 'detected_blur', 'detected_angle']],
            left_on='upload_id',
            right_on='upload_id_match',
            how='left'
        )
        # Drop the temporary matching column
        merged_df = merged_df.drop('upload_id_match', axis=1)
        # Reorder columns to match the original order
        column_order = ['id', 'upload_id', 'detected_blur', 'detected_angle', 'address_ocr_v6_accuracy', 'address_ocr_v6']
        filtered_df = merged_df[column_order].copy()

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
    rows_with_blur_angle = len(filtered_df[filtered_df['detected_blur'].notna()])

    print(f"--- CSV Processing Complete ---")
    print(f"Original CSV: {csv_file}")
    if not use_original_blur_angle:
        print(f"Image Analysis CSV: image_analysis_results.csv")
    print(f"New CSV: {output_file}")
    print(f"Total rows: {total_rows}")
    print(f"Rows with images: {rows_with_images}")
    print(f"Rows without images: {rows_without_images}")
    print(f"Rows with blur/angle data: {rows_with_blur_angle}")
    print(f"Columns included: {', '.join(column_order + ['image_path'])}")

    # Show first few rows
    print(f"\nFirst 5 rows of the new CSV:")
    print(filtered_df.head().to_string(index=False))

if __name__ == "__main__":
    # Default: use merged blur/angle
    create_filtered_csv(use_original_blur_angle=True)
    # Uncomment below to use original blur/angle from csv_file
    # create_filtered_csv(use_original_blur_angle=True)
