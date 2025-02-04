#!/usr/bin/env python
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import subprocess
from utils.doc_utils import save_documents_to_json
from utils.notebook_utils import process_notebook

# URL of the repository containing the notebooks
GIT_URL = "https://github.com/pollen-robotics/reachy2-tutorials.git"

# Directory where the repository will be cloned
REPO_DIR = os.path.join("external_docs", "reachy2_tutorials_repo")

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

def extract_notebook_documents():
    """
    Process all notebooks in the repository into meaningful chunks.
    """
    all_docs = []
    files = os.listdir(REPO_DIR)
    for file in files:
        if file.endswith(".ipynb"):
            print(f"Processing notebook {file}")
            notebook_path = os.path.join(REPO_DIR, file)
            docs = process_notebook(notebook_path, file)
            all_docs.extend(docs)
            print(f"Extracted {len(docs)} chunks from {file}")
    return all_docs

def main():
    clone_or_update_repo()
    docs = extract_notebook_documents()
    
    output_dir = os.path.join("external_docs", "Codebase")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "reachy2-tutorials.json")
    
    save_documents_to_json(docs, output_file)
    print(f"Saved {len(docs)} notebook chunks to {output_file}")

if __name__ == "__main__":
    main()