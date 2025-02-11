#!/usr/bin/env python
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import nbformat

# Repository and directory configuration
GIT_URL = "https://github.com/pollen-robotics/reachy2-tutorials.git"

# Output directories
RAW_DOCS_DIR = "data/raw_docs"
EXTRACTED_DIR = os.path.join(RAW_DOCS_DIR, "extracted")
os.makedirs(EXTRACTED_DIR, exist_ok=True)

# Repository directories
REPO_DIR = os.path.join(RAW_DOCS_DIR, "reachy2_tutorials_repo")


def clone_or_update_repo():
    """Clone the repository if it doesn't exist, or pull the latest changes."""
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            if not os.path.exists(REPO_DIR):
                print(f"Cloning repository (attempt {retry_count + 1}/{max_retries}): {GIT_URL}")
                # Use shallow clone with depth=1 and single branch
                subprocess.run([
                    "git", "clone",
                    "--depth", "1",
                    "--single-branch",
                    "--branch", "main",
                    GIT_URL,
                    REPO_DIR
                ], check=True, timeout=60)
                print("Repository cloned successfully")
            else:
                print("Repository exists. Pulling latest changes...")
                # Fetch and reset instead of pull
                subprocess.run(["git", "fetch", "--depth=1"], cwd=REPO_DIR, check=True, timeout=30)
                subprocess.run(["git", "reset", "--hard", "origin/main"], cwd=REPO_DIR, check=True, timeout=30)
                print("Repository updated successfully")
            return True
        except subprocess.TimeoutExpired:
            print(f"Timeout during git operation (attempt {retry_count + 1}/{max_retries})")
            retry_count += 1
        except subprocess.CalledProcessError as e:
            print(f"Error during git operation (attempt {retry_count + 1}/{max_retries}): {e}")
            retry_count += 1
            # Clean up failed clone
            if os.path.exists(REPO_DIR):
                shutil.rmtree(REPO_DIR)
        except Exception as e:
            print(f"Unexpected error (attempt {retry_count + 1}/{max_retries}): {e}")
            retry_count += 1
        
        if retry_count < max_retries:
            print("Waiting 5 seconds before retrying...")
            time.sleep(5)
    
    print("Failed to clone/update repository after all retries")
    return False


def process_notebook_file(file_path: str) -> dict:
    """Process a Jupyter notebook into a document."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            nb = nbformat.read(f, as_version=4)

        # Extract markdown and code cells
        content = []
        for cell in nb.cells:
            if cell.cell_type == "markdown":
                content.append(f"### Tutorial Explanation:\n{cell.source}")
            elif cell.cell_type == "code":
                content.append(f"### Code Example:\n```python\n{cell.source}\n```")

        # Get relative path for source tracking
        rel_path = os.path.relpath(file_path, REPO_DIR)

        # Get notebook title from filename or first heading
        title = os.path.splitext(os.path.basename(file_path))[0]
        for cell in nb.cells:
            if cell.cell_type == "markdown" and cell.source.startswith("#"):
                title = cell.source.split("\n")[0].lstrip("#").strip()
                break

        return {
            "content": "\n\n".join(content),
            "metadata": {
                "source": rel_path,
                "type": "tutorial",
                "format": "notebook",
                "collection": "reachy2_tutorials",
                "title": title,
            },
        }
    except Exception as e:
        print(f"Error processing notebook {file_path}: {e}")
        return None


def collect_tutorials() -> list:
    """Collect tutorials from the repository."""
    print("\nCollecting tutorials...")
    tutorials = []

    if not os.path.exists(REPO_DIR):
        print(f"Warning: Tutorials directory not found at {REPO_DIR}")
        return tutorials

    # Walk through the repository
    for root, _, files in os.walk(REPO_DIR):
        for file in sorted(files):  # Sort files to process in a consistent order
            if not file.endswith(".ipynb"):
                continue

            file_path = os.path.join(root, file)
            print(f"Processing: {file}")

            doc = process_notebook_file(file_path)
            if doc:
                tutorials.append(doc)
                print(f"Added tutorial: {file}")

    print(f"Collected {len(tutorials)} tutorials")
    return tutorials


def save_tutorials(tutorials: list):
    """Save tutorials to the appropriate JSON file."""
    if not tutorials:
        print("No tutorials to save")
        return

    output_file = os.path.join(EXTRACTED_DIR, "raw_tutorials.json")
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(tutorials, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(tutorials)} tutorials to {output_file}")
    except Exception as e:
        print(f"Error saving tutorials to {output_file}: {e}")


def main():
    """Main function to scrape tutorials."""
    print("Starting tutorials scraping...")

    # Step 1: Clone/update the repository
    if not clone_or_update_repo():
        print("Failed to clone/update repository. Aborting.")
        return

    # Step 2: Collect tutorials
    tutorials = collect_tutorials()

    # Step 3: Save tutorials
    save_tutorials(tutorials)

    print("\nTutorials scraping complete!")


if __name__ == "__main__":
    main()
