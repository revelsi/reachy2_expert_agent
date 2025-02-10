#!/usr/bin/env python

import os
import sys
import json
from pathlib import Path
import frontmatter
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.scrape_reachy2_docs import (
    clone_or_update_repo,
    process_markdown_file,
    extract_reachy2_documentation,
    load_cache,
    save_cache,
    should_update_repo,
    REPO_DIR,
    CACHE_FILE
)

def test_cache_operations():
    """Test cache loading, saving, and update checking."""
    print("\nTesting Cache Operations:")
    print("=" * 80)
    
    # Test cache saving
    test_cache = {
        'last_update': datetime.now().isoformat(),
        'repo_path': REPO_DIR
    }
    save_cache(test_cache)
    print("Cache saved successfully")
    
    # Test cache loading
    loaded_cache = load_cache()
    assert loaded_cache == test_cache, "Loaded cache doesn't match saved cache"
    print("Cache loaded successfully")
    
    # Test update checking with fresh cache
    assert not should_update_repo(), "Repository update requested despite fresh cache"
    print("Update check working with fresh cache")
    
    # Test update checking with expired cache
    old_time = (datetime.now() - timedelta(hours=25)).isoformat()
    save_cache({'last_update': old_time, 'repo_path': REPO_DIR})
    assert should_update_repo(), "Repository update not requested with expired cache"
    print("Update check working with expired cache")

def test_markdown_processing():
    """Test markdown file processing."""
    print("\nTesting Markdown Processing:")
    print("=" * 80)
    
    # Create a test markdown file
    test_content = """---
title: Test Document
description: A test markdown document
category: testing
weight: 1
---

# Test Header

This is a test markdown document.

## Code Example

```python
from reachy2_sdk import ReachySDK
robot = ReachySDK('localhost')
```

## Another Section

Some more content here.
"""
    
    test_file = "test_doc.md"
    with open(test_file, "w") as f:
        f.write(test_content)
    
    # Process the test file
    result = process_markdown_file(test_file)
    
    # Clean up
    os.remove(test_file)
    
    # Verify the result
    assert result is not None, "Failed to process markdown file"
    assert 'content' in result, "No content in processed result"
    assert 'metadata' in result, "No metadata in processed result"
    
    metadata = result['metadata']
    assert metadata['title'] == "Test Document", "Title not correctly extracted"
    assert metadata['description'] == "A test markdown document", "Description not correctly extracted"
    assert metadata['category'] == "testing", "Category not correctly extracted"
    assert metadata['weight'] == 1, "Weight not correctly extracted"
    
    print("Markdown processing successful")

def test_documentation_extraction():
    """Test the full documentation extraction process."""
    print("\nTesting Documentation Extraction:")
    print("=" * 80)
    
    # First ensure we have the repository
    success = clone_or_update_repo()
    assert success, "Failed to clone/update repository"
    print("Repository prepared successfully")
    
    # Extract documentation
    docs = extract_reachy2_documentation()
    assert docs, "No documents extracted"
    print(f"Successfully extracted {len(docs)} documents")
    
    # Analyze the extracted documents
    categories = {}
    for doc in docs:
        category = doc['metadata'].get('category', 'uncategorized')
        categories[category] = categories.get(category, 0) + 1
    
    print("\nDocument categories:")
    for category, count in categories.items():
        print(f"- {category}: {count} documents")
    
    # Check document structure
    for doc in docs[:3]:  # Check first 3 docs
        assert 'content' in doc, "Document missing content"
        assert 'metadata' in doc, "Document missing metadata"
        assert 'source' in doc['metadata'], "Document missing source in metadata"
        assert 'type' in doc['metadata'], "Document missing type in metadata"
        assert 'format' in doc['metadata'], "Document missing format in metadata"
    
    print("\nDocument structure verification successful")

def main():
    """Run all Reachy 2 documentation tests."""
    print("Running Reachy 2 Documentation Tests")
    print("=" * 80)
    
    test_cache_operations()
    test_markdown_processing()
    test_documentation_extraction()
    
    print("\nAll tests completed successfully!")

if __name__ == "__main__":
    main() 