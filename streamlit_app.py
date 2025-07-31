import streamlit as st
import pandas as pd
import os
from PIL import Image
import numpy as np

# Set page config
st.set_page_config(
    page_title="NID Data Viewer",
    page_icon="📊",
    layout="wide"
)

def load_data():
    """Load the CSV data"""
    try:
        df = pd.read_csv("filtered_nid_data_with_images.csv")
        return df
    except FileNotFoundError:
        st.error("CSV file not found! Please make sure 'filtered_nid_data_with_images.csv' exists in the current directory.")
        return None

def display_image(image_path):
    """Display image if it exists"""
    if pd.isna(image_path) or image_path == "" or not image_path:
        return None
    
    if os.path.exists(image_path):
        try:
            image = Image.open(image_path)
            return image
        except Exception as e:
            st.error(f"Error loading image: {e}")
            return None
    else:
        st.warning(f"Image file not found: {image_path}")
        return None

def main():
    st.title("📊 NID Data Viewer with Address Images")
    st.markdown("---")
    
    # Load data
    df = load_data()
    if df is None:
        return
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    # Debug section
    with st.sidebar.expander("🔧 Debug Info"):
        st.write(f"Total rows in CSV: {len(df)}")
        st.write(f"Rows with non-empty image_path: {len(df[df['image_path'].notna() & (df['image_path'] != '')])}")
        if len(df) > 0:
            sample_path = df[df['image_path'].notna() & (df['image_path'] != '')].iloc[0]['image_path'] if len(df[df['image_path'].notna() & (df['image_path'] != '')]) > 0 else "No valid paths"
            st.write(f"Sample image path: {sample_path}")
            if sample_path != "No valid paths":
                st.write(f"File exists: {os.path.exists(sample_path)}")
    
    # Filter by accuracy range
    min_accuracy = st.sidebar.slider(
        "Minimum Address OCR Accuracy", 
        min_value=0.0, 
        max_value=1.0, 
        value=0.0, 
        step=0.1
    )
    
    # Filter by blur range
    max_blur = st.sidebar.slider(
        "Maximum Detected Blur", 
        min_value=float(df['detected_blur'].min()), 
        max_value=float(df['detected_blur'].max()), 
        value=float(df['detected_blur'].max()),
        step=100.0
    )
    
    # Filter data
    filtered_df = df[
        (df['address_ocr_v6_accuracy'] >= min_accuracy) & 
        (df['detected_blur'] <= max_blur)
    ]
    
    # Display statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Records", len(filtered_df))
    with col2:
        st.metric("With Images", len(filtered_df[filtered_df['image_path'] != ""]))
    with col3:
        st.metric("Avg Accuracy", f"{filtered_df['address_ocr_v6_accuracy'].mean():.3f}")
    with col4:
        st.metric("Avg Blur", f"{filtered_df['detected_blur'].mean():.1f}")
    
    st.markdown("---")
    
    # Display mode selection
    display_mode = st.radio(
        "Display Mode:",
        ["Table View", "Card View", "Image Gallery"]
    )
    
    if display_mode == "Table View":
        st.subheader("📋 Data Table")
        # Hide the image_path column from display, but keep address columns
        display_df = filtered_df.drop('image_path', axis=1)
        
        # Configure column display
        column_config = {
            "address": st.column_config.TextColumn(
                "Original Address",
                width="medium",
                help="Original address from the database"
            ),
            "address_ocr_v6": st.column_config.TextColumn(
                "Predicted Address (OCR)",
                width="medium", 
                help="Address extracted using OCR"
            ),
            "address_ocr_v6_accuracy": st.column_config.NumberColumn(
                "Address Accuracy",
                min_value=0.0,
                max_value=1.0,
                format="%.3f"
            )
        }
        
        st.dataframe(display_df, use_container_width=True, column_config=column_config)
        
    elif display_mode == "Card View":
        st.subheader("🗃️ Card View")
        
        # Pagination
        items_per_page = st.selectbox("Items per page:", [5, 10, 20, 50], index=1)
        total_pages = len(filtered_df) // items_per_page + (1 if len(filtered_df) % items_per_page > 0 else 0)
        
        if total_pages > 0:
            page = st.selectbox("Page:", range(1, total_pages + 1))
            start_idx = (page - 1) * items_per_page
            end_idx = start_idx + items_per_page
            page_df = filtered_df.iloc[start_idx:end_idx]
            
            for idx, row in page_df.iterrows():
                with st.container():
                    col1, col2 = st.columns([2, 3])  # Made image column larger
                    
                    with col1:
                        # Display image
                        if pd.notna(row['image_path']) and row['image_path'] != "":
                            image = display_image(row['image_path'])
                            if image:
                                st.image(image, caption=f"ID: {row['id']}", use_container_width=True, width=600)
                            else:
                                st.error("❌ Image failed to load")
                        else:
                            st.info("📷 No image available")
                    
                    with col2:
                        # Display data
                        st.write(f"**🆔 ID:** {row['id']}")
                        st.write(f"**📁 Upload ID:** {row['upload_id']}")
                        st.write(f"**🌫️ Detected Blur:** {row['detected_blur']:.2f}")
                        st.write(f"**📝 Address OCR Accuracy:** {row['address_ocr_v6_accuracy']:.3f}")
                        
                        # Progress bar for accuracy
                        accuracy_color = "green" if row['address_ocr_v6_accuracy'] > 0.7 else "orange" if row['address_ocr_v6_accuracy'] > 0.5 else "red"
                        st.progress(row['address_ocr_v6_accuracy'])
                        
                        # Address information
                        with st.expander("📍 Address Information"):
                            if pd.notna(row.get('address')) and row.get('address'):
                                st.write("**Original Address:**")
                                st.text_area("", value=row['address'], height=80, disabled=True, key=f"orig_addr_{idx}")
                            
                            if pd.notna(row.get('address_ocr_v6')) and row.get('address_ocr_v6'):
                                st.write("**Predicted Address (OCR):**")
                                st.text_area("", value=row['address_ocr_v6'], height=80, disabled=True, key=f"pred_addr_{idx}")
                        
                        # Quality indicators
                        quality_col1, quality_col2 = st.columns(2)
                        with quality_col1:
                            if row['address_ocr_v6_accuracy'] > 0.8:
                                st.success("🟢 High Accuracy")
                            elif row['address_ocr_v6_accuracy'] > 0.6:
                                st.warning("🟡 Medium Accuracy")
                            else:
                                st.error("🔴 Low Accuracy")
                        
                        with quality_col2:
                            if row['detected_blur'] < 500:
                                st.success("🟢 Low Blur")
                            elif row['detected_blur'] < 1500:
                                st.warning("🟡 Medium Blur")
                            else:
                                st.error("🔴 High Blur")
                    
                    st.markdown("---")
    
    elif display_mode == "Image Gallery":
        st.subheader("🖼️ Image Gallery")
        
        # Filter only rows with images
        image_df = filtered_df[filtered_df['image_path'] != ""]
        
        if len(image_df) == 0:
            st.warning("No images available for the current filters.")
            return
        
        # Grid layout
        cols_per_row = st.selectbox("Images per row:", [2, 3, 4, 5], index=1)  # Changed default to 3 (less columns = larger images)
        
        rows = len(image_df) // cols_per_row + (1 if len(image_df) % cols_per_row > 0 else 0)
        
        for row_idx in range(rows):
            cols = st.columns(cols_per_row)
            for col_idx in range(cols_per_row):
                img_idx = row_idx * cols_per_row + col_idx
                if img_idx < len(image_df):
                    row_data = image_df.iloc[img_idx]
                    with cols[col_idx]:
                        image = display_image(row_data['image_path'])
                        if image:
                            st.image(image, use_container_width=True, width=300)
                            st.caption(f"ID: {row_data['id']}")
                            st.caption(f"Accuracy: {row_data['address_ocr_v6_accuracy']:.3f}")
                            st.caption(f"Blur: {row_data['detected_blur']:.1f}")
                            
                            # Address preview in gallery
                            with st.expander(f"📍 Address - ID {row_data['id']}"):
                                if pd.notna(row_data.get('address_ocr_v6')) and row_data.get('address_ocr_v6'):
                                    st.text_area("Predicted Address:", value=row_data['address_ocr_v6'], height=60, disabled=True, key=f"gallery_addr_{img_idx}")
    
    # Download section
    st.markdown("---")
    st.subheader("💾 Download Filtered Data")
    
    if st.button("Download Filtered CSV"):
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"filtered_nid_data_{min_accuracy}_{max_blur}.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()
