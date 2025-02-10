#!/usr/bin/env python
import sys, os, subprocess, shutil
from pathlib import Path
import json
import frontmatter
import markdown
import time
from datetime import datetime, timedelta

# Repository and directory configuration
GIT_URL = "https://github.com/pollen-robotics/reachy2-docs.git"

# Output directories
RAW_DOCS_DIR = "raw_docs"
EXTRACTED_DIR = os.path.join(RAW_DOCS_DIR, "extracted")
CACHE_DIR = os.path.join(RAW_DOCS_DIR, "cache")
os.makedirs(EXTRACTED_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)

# Repository directories
REPO_DIR = os.path.join(RAW_DOCS_DIR, "reachy2_docs_repo")
DOCS_SOURCE_DIR = os.path.join(REPO_DIR, "content")

# Cache settings
CACHE_FILE = os.path.join(CACHE_DIR, "repo_cache.json")
CACHE_EXPIRY_HOURS = 24  # Update cache if older than 24 hours

def load_cache():
    """Load the cache file if it exists."""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading cache: {e}")
    return {}

def save_cache(cache_data):
    """Save the cache file."""
    try:
        with open(CACHE_FILE, 'w') as f:
            json.dump(cache_data, f)
    except Exception as e:
        print(f"Error saving cache: {e}")

def should_update_repo():
    """Check if the repository needs updating based on cache."""
    cache = load_cache()
    last_update = cache.get('last_update')
    
    if not last_update:
        return True
    
    # Check if cache has expired
    last_update_time = datetime.fromisoformat(last_update)
    if datetime.now() - last_update_time > timedelta(hours=CACHE_EXPIRY_HOURS):
        return True
    
    return False

def clone_or_update_repo():
    """Clone the repository if it doesn't exist, or pull the latest changes.
    Uses shallow clone and sparse checkout for efficiency."""
    try:
        # Check cache first
        if os.path.exists(REPO_DIR) and not should_update_repo():
            print("Using cached repository (last update within 24 hours)")
            return True
        
        if not os.path.exists(REPO_DIR):
            print(f"Cloning repository: {GIT_URL} into {REPO_DIR}...")
            
            # Create repo directory
            os.makedirs(REPO_DIR, exist_ok=True)
            
            # Initialize git repo
            subprocess.run(["git", "init"], cwd=REPO_DIR, check=True)
            
            # Add remote
            subprocess.run(["git", "remote", "add", "origin", GIT_URL], cwd=REPO_DIR, check=True)
            
            # Enable sparse checkout
            subprocess.run(["git", "config", "core.sparseCheckout", "true"], cwd=REPO_DIR, check=True)
            
            # Set sparse checkout paths
            sparse_checkout_path = os.path.join(REPO_DIR, ".git", "info", "sparse-checkout")
            with open(sparse_checkout_path, "w") as f:
                f.write("content/\n")  # Only checkout the content directory
            
            # Fetch with depth=1 (shallow clone)
            subprocess.run(["git", "fetch", "--depth=1", "origin", "main"], cwd=REPO_DIR, check=True)
            
            # Checkout main branch
            subprocess.run(["git", "checkout", "main"], cwd=REPO_DIR, check=True)
            
            print("Repository cloned successfully with optimizations")
        else:
            print("Repository exists. Pulling latest changes...")
            # For existing repos, just fetch the latest shallow copy
            subprocess.run(["git", "fetch", "--depth=1"], cwd=REPO_DIR, check=True)
            subprocess.run(["git", "reset", "--hard", "origin/main"], cwd=REPO_DIR, check=True)
            print("Repository updated successfully")
        
        # Update cache
        save_cache({
            'last_update': datetime.now().isoformat(),
            'repo_path': REPO_DIR
        })
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error during git operation: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

def process_markdown_file(file_path: str) -> dict:
    """Process a markdown file into a document."""
    try:
        # Parse frontmatter and content
        with open(file_path, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)
        
        # Get metadata from frontmatter
        metadata = dict(post.metadata)
        
        # Convert markdown to plain text while preserving code blocks
        content = post.content
        
        # Get relative path for source tracking
        rel_path = os.path.relpath(file_path, REPO_DIR)
        
        return {
            "content": content,
            "metadata": {
                "source": rel_path,
                "type": "documentation",
                "format": "markdown",
                "collection": "reachy2_docs",
                "title": metadata.get("title", ""),
                "description": metadata.get("description", ""),
                "category": metadata.get("category", ""),
                "weight": metadata.get("weight", 0)
            }
        }
    except Exception as e:
        print(f"Error processing markdown file {file_path}: {e}")
        return None

def extract_reachy2_documentation():
    """Extract documentation from Reachy 2 markdown files."""
    print("\nExtracting Reachy 2 documentation...")
    documents = []
    
    # First ensure we have the latest docs
    if not clone_or_update_repo():
        print("Failed to clone/update repository. Aborting documentation extraction.")
        return []
    
    # Walk through the documentation directory
    for root, _, files in os.walk(DOCS_SOURCE_DIR):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                doc = process_markdown_file(file_path)
                if doc:
                    documents.append(doc)
    
    print(f"Extracted {len(documents)} documents from Reachy 2 documentation")
    return documents

def save_documents():
    """Save extracted documents to JSON file."""
    documents = extract_reachy2_documentation()
    if documents:
        # Save raw documents first
        raw_output = os.path.join(EXTRACTED_DIR, "raw_reachy2_docs.json")
        with open(raw_output, 'w', encoding='utf-8') as f:
            json.dump(documents, f, indent=2, ensure_ascii=False)
        print(f"\nSaved {len(documents)} documents to {raw_output}")
    else:
        print("\nNo documents to save")

if __name__ == "__main__":
    save_documents() 