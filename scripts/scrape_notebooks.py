#!/usr/bin/env python
import sys, os, shutil, subprocess
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# URL of the repository containing the notebooks
GIT_URL = "https://github.com/pollen-robotics/reachy2-tutorials.git"

# Directory where the repository will be cloned
REPO_DIR = os.path.join("external_docs", "reachy2_tutorials_repo")
RAW_DIR = os.path.join("raw_docs", "reachy2_tutorials")

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
    os.makedirs(RAW_DIR, exist_ok=True)
    for file in os.listdir(REPO_DIR):
        if file.endswith(".ipynb"):
            src = os.path.join(REPO_DIR, file)
            dst = os.path.join(RAW_DIR, file)
            shutil.copy2(src, dst)
            print(f"Copied {file} to {RAW_DIR}")

def main():
    clone_or_update_repo()
    copy_notebooks()

if __name__ == "__main__":
    main()