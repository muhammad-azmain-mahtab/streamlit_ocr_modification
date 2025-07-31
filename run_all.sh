#!/bin/zsh
# Run all NID processing steps with a single click

# Step 1: Run image analysis (check.py)
echo "Running image analysis (check.py)..."
python3 check.py

# Step 2: Create filtered CSV (create_filtered_csv.py) with use_original_blur_angle=False
echo "Creating filtered CSV (create_filtered_csv.py) with use_original_blur_angle=False..."
python3 -c "import create_filtered_csv; create_filtered_csv.create_filtered_csv(use_original_blur_angle=False)"

# Step 3: Launch Streamlit app
# You can close the terminal after the app launches

echo "Launching Streamlit app..."
streamlit run streamlit_app.py
