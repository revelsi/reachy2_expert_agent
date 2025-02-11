#!/usr/bin/env python

import os
import sys
import json
from pprint import pprint

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tools.chunk_documents import chunk_markdown_docs, extract_code_blocks

def test_header_hierarchy():
    """Test that header hierarchy is correctly preserved."""
    test_content = """# Main Header
Some content here

## Sub Header 1
Some sub content

### Sub Sub Header
Deep content

## Sub Header 2
More content
"""
    test_doc = {
        'content': test_content,
        'metadata': {'source': 'test.md'}
    }
    
    chunks = chunk_markdown_docs([test_doc])
    
    print("\nTesting Header Hierarchy:")
    print("=" * 80)
    for chunk in chunks:
        print("\nChunk metadata:")
        print(f"Section path: {chunk['metadata'].get('section_path', 'No path found')}")
        print(f"Content preview: {chunk['content'][:200]}...")

def test_code_block_preservation():
    """Test that code blocks are preserved with their context."""
    test_content = """# Using the SDK

First, import the SDK:

```python
from reachy2_sdk import ReachySDK
robot = ReachySDK('localhost')
```

Then initialize the robot:

```python
robot.turn_on()
robot.goto_posture('rest')
```
"""
    test_doc = {
        'content': test_content,
        'metadata': {'source': 'test.md'}
    }
    
    chunks = chunk_markdown_docs([test_doc])
    
    print("\nTesting Code Block Preservation:")
    print("=" * 80)
    for chunk in chunks:
        print("\nChunk content:")
        print(chunk['content'])
        print(f"\nHas code: {chunk['metadata'].get('has_code', False)}")

def test_overlap_preservation():
    """Test that context is preserved in overlapping chunks."""
    test_content = "# " + "Very long content " * 100 + """
## Section with code
```python
# Some code here
print("Hello")
```
"""
    test_doc = {
        'content': test_content,
        'metadata': {'source': 'test.md'}
    }
    
    chunks = chunk_markdown_docs([test_doc])
    
    print("\nTesting Overlap Preservation:")
    print("=" * 80)
    for i, chunk in enumerate(chunks):
        print(f"\nChunk {i+1}:")
        print(f"Size: {len(chunk['content'])} characters")
        if i > 0:  # Check overlap with previous chunk
            prev_end = chunks[i-1]['content'][-200:]
            curr_start = chunk['content'][:200]
            print("\nOverlap between chunks:")
            print(f"Previous chunk ends with: {prev_end}")
            print(f"Current chunk starts with: {curr_start}")

def test_real_docs():
    """Test chunking with actual Reachy 2 documentation."""
    print("\nTesting Real Documentation:")
    print("=" * 80)
    
    # Load the raw documentation
    raw_docs_path = os.path.join("raw_docs", "extracted", "raw_reachy2_docs.json")
    if not os.path.exists(raw_docs_path):
        print(f"No raw documentation found at {raw_docs_path}")
        print("Please run the scraper first: python scripts/scrape_reachy2_docs.py")
        return
    
    print("Loading raw documentation...")
    with open(raw_docs_path, 'r') as f:
        raw_docs = json.load(f)
    print(f"Loaded {len(raw_docs)} documents")
    
    # Process a sample of the chunks
    print("\nProcessing sample documents...")
    sample_size = min(5, len(raw_docs))
    sample_docs = raw_docs[:sample_size]
    chunks = chunk_markdown_docs(sample_docs)
    
    # Analyze the results
    print(f"\nProcessed {len(chunks)} chunks from {sample_size} sample documents")
    
    # Size analysis
    sizes = [len(chunk['content']) for chunk in chunks]
    avg_size = sum(sizes) / len(sizes) if sizes else 0
    print(f"Average chunk size: {avg_size:.2f} characters")
    print(f"Smallest chunk: {min(sizes)} characters")
    print(f"Largest chunk: {max(sizes)} characters")
    
    # Content analysis
    code_chunks = sum(1 for chunk in chunks if chunk['metadata'].get('has_code', False))
    print(f"\nChunks with code: {code_chunks} ({(code_chunks/len(chunks)*100):.1f}%)")
    
    # Section path analysis
    print("\nSection paths found:")
    paths = set(chunk['metadata'].get('section_path', '') for chunk in chunks)
    for path in sorted(paths)[:5]:  # Show first 5 paths
        print(f"- {path}")
    if len(paths) > 5:
        print(f"... and {len(paths)-5} more paths")
    
    print("\nSample document chunking successful")

def main():
    """Run all markdown chunking tests."""
    print("Running Markdown Chunking Tests")
    print("=" * 80)
    
    # Run synthetic tests
    test_header_hierarchy()
    test_code_block_preservation()
    test_overlap_preservation()
    
    # Test with real documentation
    test_real_docs()

if __name__ == "__main__":
    main() 