import os
import shutil

# Create the images directory if it doesn't exist
os.makedirs('static/images', exist_ok=True)

# Move the file
source = "Screenshot 2024-10-15 at 9.33.12 PM.png"
destination = "static/images/budgy-logo.png"

if os.path.exists(source):
    shutil.move(source, destination)
    print(f"File moved successfully to {destination}")
else:
    print(f"Source file {source} does not exist")

# List the contents of the static/images directory
print("Contents of static/images:")
print(os.listdir('static/images'))
