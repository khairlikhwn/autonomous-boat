import os
import glob

# Replace with your actual directory and file pattern
image_dir = "freedomtech/all"
file_pattern = "*.jpg"  # Replace with your actual file pattern

# Get a list of all image file paths
image_files = glob.glob(os.path.join(image_dir, file_pattern))

# Get a list of labels based on the file paths
# This assumes that the label for each image is its directory name
labels = [os.path.basename(os.path.dirname(f)) for f in image_files]

from sklearn.model_selection import train_test_split

# Split the data into training and validation sets
train_files, val_files, train_labels, val_labels = train_test_split(image_files, labels, test_size=0.2, random_state=42)

import shutil

# Define your output directories
train_dir = "freedomtech/train"
val_dir = "freedomtech/validate"

# Create the output directories if they don't exist
os.makedirs(train_dir, exist_ok=True)
os.makedirs(val_dir, exist_ok=True)

# Copy the training files to the training directory
for f in train_files:
    shutil.copy(f, train_dir)

# Copy the validation files to the validation directory
for f in val_files:
    shutil.copy(f, val_dir)