#!/usr/bin/env python
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import subprocess
from utils.doc_utils import save_documents_to_json
from utils.code_utils import process_python_file
from utils.notebook_utils import process_notebook

# URL of the Reachy2 SDK repository
GIT_URL = "https://github.com/pollen-robotics/reachy2-sdk.git"

# Directory where the repository will be cloned
REPO_DIR = os.path.join("external_docs", "reachy2_sdk_repo")

# Source directory: In reachy2-sdk, look in src/examples (which contains both .py and .ipynb files)
SOURCE_DIR = os.path.join(REPO_DIR, "src", "examples")

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

def extract_code_documents():
    """
    Process all Python files and notebooks in the source directory into meaningful chunks.
    """
    if not os.path.exists(SOURCE_DIR):
        print(f"Source directory not found: {SOURCE_DIR}")
        sys.exit(1)
    
    all_docs = []
    files = os.listdir(SOURCE_DIR)
    
    for file in files:
        file_path = os.path.join(SOURCE_DIR, file)
        
        if file.endswith(".py"):
            print(f"Processing Python file {file}")
            docs = process_python_file(file_path, file)
            all_docs.extend(docs)
            print(f"Extracted {len(docs)} chunks from {file}")
            
        elif file.endswith(".ipynb"):
            print(f"Processing notebook {file}")
            docs = process_notebook(file_path, file)
            all_docs.extend(docs)
            print(f"Extracted {len(docs)} chunks from {file}")
    
    return all_docs

def main():
    clone_or_update_repo()
    docs = extract_code_documents()
    
    output_dir = os.path.join("external_docs", "Codebase")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "reachy2-sdk.json")
    
    save_documents_to_json(docs, output_file)
    print(f"Saved {len(docs)} code chunks to {output_file}")

if __name__ == "__main__":
    main()