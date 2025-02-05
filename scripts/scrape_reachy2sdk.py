#!/usr/bin/env python
import sys, os, subprocess, shutil
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# URL of the Reachy2 SDK repository
GIT_URL = "https://github.com/pollen-robotics/reachy2-sdk.git"

# Directory where the repository will be cloned
REPO_DIR = os.path.join("external_docs", "reachy2_sdk_repo")

# Source directory: In reachy2-sdk, look in src/examples (which may contain .py and .ipynb files)
SOURCE_DIR = os.path.join(REPO_DIR, "src", "examples")

# Destination directory for raw files
RAW_DIR = os.path.join("raw_docs", "reachy2_sdk")


def clone_or_update_repo():
    """Clone the repository if it doesn't exist, or pull the latest changes."""
    if not os.path.exists(REPO_DIR):
        print(f"Cloning repository: {GIT_URL} into {REPO_DIR}...")
        subprocess.run(["git", "clone", GIT_URL, REPO_DIR], check=True)
    else:
        print("Repository already cloned. Pulling latest changes...")
        subprocess.run(["git", "-C", REPO_DIR, "pull"], check=True)


def copy_raw_files():
    """Copy all raw .py and .ipynb files from SOURCE_DIR to RAW_DIR."""
    if not os.path.exists(SOURCE_DIR):
        print(f"Source directory not found: {SOURCE_DIR}")
        sys.exit(1)
    os.makedirs(RAW_DIR, exist_ok=True)
    for file in os.listdir(SOURCE_DIR):
        if file.endswith(".py") or file.endswith(".ipynb"):
            src = os.path.join(SOURCE_DIR, file)
            dst = os.path.join(RAW_DIR, file)
            shutil.copy2(src, dst)
            print(f"Copied {file} to {RAW_DIR}")


def main():
    clone_or_update_repo()
    copy_raw_files()


if __name__ == "__main__":
    main()