#!/usr/bin/env python
import os
import shutil
import subprocess

# URL of the repository containing the notebooks
GIT_URL = "https://github.com/pollen-robotics/reachy2-tutorials.git"

# Directory where the repository will be cloned
REPO_DIR = os.path.join("external_docs", "reachy2_tutorials_repo")

# Destination directory: store notebooks in a dedicated subfolder
DEST_DIR = os.path.join("external_docs", "Codebase", "reachy2-tutorials")

def clone_or_update_repo():
    """
    Clone the repository if it doesn't exist, or pull the latest changes.
    """
    if not os.path.exists(REPO_DIR):
        print("Cloning repository...")
        subprocess.run(["git", "clone", GIT_URL, REPO_DIR], check=True)
    else:
        print("Repository already cloned. Pulling latest changes...")
        subprocess.run(["git", "-C", REPO_DIR, "pull"], check=True)

def copy_notebooks():
    """
    Copies all .ipynb files from the main folder of the cloned repository into DEST_DIR.
    Any existing DEST_DIR content is removed first.
    """
    # Remove the destination folder to clear old results for this repo only.
    if os.path.exists(DEST_DIR):
        shutil.rmtree(DEST_DIR)
        print(f"Removed old folder at {DEST_DIR}")
    os.makedirs(DEST_DIR, exist_ok=True)
    
    files = os.listdir(REPO_DIR)
    notebook_count = 0
    for file in files:
        if file.endswith(".ipynb"):
            src_path = os.path.join(REPO_DIR, file)
            dst_path = os.path.join(DEST_DIR, file)
            print(f"Copying {src_path} to {dst_path}")
            shutil.copy2(src_path, dst_path)
            notebook_count += 1

    if notebook_count == 0:
        print("No notebook files found in the repository root.")
    else:
        print(f"Copied {notebook_count} notebook file(s).")

def main():
    clone_or_update_repo()
    copy_notebooks()
    print("\nAll notebooks have been successfully stored in external_docs/Codebase/reachy2-tutorials.")

if __name__ == "__main__":
    main()