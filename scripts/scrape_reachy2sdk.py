#!/usr/bin/env python
import os
import sys
import subprocess
import shutil

# URL of the Reachy2 SDK repository
GIT_URL = "https://github.com/pollen-robotics/reachy2-sdk.git"

# Directory where the repository will be cloned
REPO_DIR = os.path.join("external_docs", "reachy2_sdk_repo")

# Source directory: In reachy2-sdk, look in src/examples (which contains both .py and .ipynb files)
SOURCE_DIR = os.path.join(REPO_DIR, "src", "examples")

# Destination directory: store Reachy2 SDK files in its own subfolder
DEST_DIR = os.path.join("external_docs", "Codebase", "reachy2-sdk")

def clone_or_update_repo():
    """
    Clone the repository if it doesn't exist, or pull the latest changes.
    """
    if not os.path.exists(REPO_DIR):
        print(f"Cloning repository: {GIT_URL} into {REPO_DIR}...")
        subprocess.run(["git", "clone", GIT_URL, REPO_DIR], check=True)
    else:
        print("Repository already cloned. Pulling latest changes...")
        subprocess.run(["git", "-C", REPO_DIR, "pull"], check=True)

def copy_code_files():
    """
    Copies all .py and .ipynb files from the SOURCE_DIR (src/examples)
    into DEST_DIR. Only the dedicated destination folder for this repo is removed.
    """
    if not os.path.exists(SOURCE_DIR):
        print(f"Source directory not found: {SOURCE_DIR}")
        sys.exit(1)
        
    if os.path.exists(DEST_DIR):
        shutil.rmtree(DEST_DIR)
        print(f"Removed old folder at {DEST_DIR}")
    os.makedirs(DEST_DIR, exist_ok=True)
    
    files = os.listdir(SOURCE_DIR)
    count = 0
    for file in files:
        if file.endswith(".py") or file.endswith(".ipynb"):
            src_path = os.path.join(SOURCE_DIR, file)
            dst_path = os.path.join(DEST_DIR, file)
            print(f"Copying {src_path} to {dst_path}")
            shutil.copy2(src_path, dst_path)
            count += 1

    if count == 0:
        print("No Python or Notebook files found in the source directory.")
    else:
        print(f"Copied {count} file(s).")

def main():
    clone_or_update_repo()
    copy_code_files()
    print("\nAll Reachy2 SDK code files have been successfully stored in external_docs/Codebase/reachy2-sdk.")

if __name__ == "__main__":
    main()