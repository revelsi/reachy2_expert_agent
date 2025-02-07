#!/usr/bin/env python

import os
import sys
import json
from pprint import pprint

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def display_chunk(chunk, index: int):
    """Display a chunk with its metadata in a readable format."""
    print(f"\n{'='*80}")
    print(f"Chunk {index}:")
    print(f"{'='*80}")
    print("\nMetadata:")
    print('-' * 40)
    for key, value in chunk.get('metadata', {}).items():
        print(f"{key}: {value}")
    print("\nContent:")
    print('-' * 40)
    # Handle both formats
    content = chunk.get('page_content', chunk.get('content', 'No content available'))
    print(content)

def analyze_chunks(filepath: str, max_display: int = 3):
    """Analyze chunks from a JSON file."""
    print(f"\nAnalyzing chunks from: {filepath}")
    print("=" * 80)
    
    with open(filepath, 'r') as f:
        chunks = json.load(f)
    
    print(f"\nTotal chunks: {len(chunks)}")
    
    # Analyze chunk sizes (handle both formats)
    sizes = [len(chunk.get('page_content', chunk.get('content', ''))) for chunk in chunks]
    avg_size = sum(sizes) / len(sizes) if sizes else 0
    print(f"Average chunk size: {avg_size:.2f} characters")
    print(f"Smallest chunk: {min(sizes)} characters")
    print(f"Largest chunk: {max(sizes)} characters")
    
    # Display metadata keys
    if chunks:
        print("\nMetadata keys present:")
        print(set().union(*[set(chunk.get('metadata', {}).keys()) for chunk in chunks]))
    
    # Display sample chunks
    print(f"\nDisplaying first {max_display} chunks as samples:")
    for i, chunk in enumerate(chunks[:max_display]):
        display_chunk(chunk, i+1)

def main():
    """Test the API documentation chunking process."""
    # First, ensure we have fresh documentation
    print("Step 1: Scraping documentation...")
    os.system("python scripts/scrape_api_docs.py")
    
    # Then, process the chunks
    print("\nStep 2: Chunking documentation...")
    os.system("python scripts/chunk_documents.py")
    
    # Analyze the results
    print("\nStep 3: Analyzing chunks...")
    base_dir = "external_docs/documents"
    
    print("\nAnalyzing API Classes:")
    analyze_chunks(os.path.join(base_dir, "api_docs_classes.json"))
    
    print("\nAnalyzing API Functions:")
    analyze_chunks(os.path.join(base_dir, "api_docs_functions.json"))

if __name__ == "__main__":
    main() 