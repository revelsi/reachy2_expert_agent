#!/usr/bin/env python

import json
import os
import sys
from typing import List, Dict
import statistics
from collections import defaultdict

def load_chunks(filepath: str) -> List[Dict]:
    """Load chunks from a JSON file."""
    if not os.path.exists(filepath):
        print(f"Warning: File not found - {filepath}")
        return []
    with open(filepath, 'r') as f:
        return json.load(f)

def analyze_chunks(chunks: List[Dict], collection_name: str):
    """Analyze chunks and print statistics."""
    print(f"\nAnalyzing {collection_name}:")
    print("=" * 80)
    
    if not chunks:
        print("No chunks found.")
        return
    
    # Basic statistics
    print("\nBasic Statistics:")
    print("-" * 40)
    print(f"Total chunks: {len(chunks)}")
    
    # Character count statistics
    sizes = [len(chunk['content']) for chunk in chunks]
    avg_size = statistics.mean(sizes)
    median_size = statistics.median(sizes)
    std_dev = statistics.stdev(sizes) if len(sizes) > 1 else 0
    
    print("Character count statistics:")
    print(f"- Average size: {avg_size:.2f} characters")
    print(f"- Median size: {median_size:.0f} characters")
    print(f"- Standard deviation: {std_dev:.2f} characters")
    print(f"- Smallest chunk: {min(sizes)} characters")
    print(f"- Largest chunk: {max(sizes)} characters")
    
    # Size distribution
    print("\nSize distribution:")
    ranges = [(0, 500), (501, 1000), (1001, 1500), (1501, 2000), (2001, float('inf'))]
    for start, end in ranges:
        count = sum(1 for size in sizes if start <= size <= end)
        percentage = (count / len(sizes)) * 100
        range_label = f"{start}-{end if end != float('inf') else '+'}"
        print(f"- {range_label} chars: {count} chunks ({percentage:.1f}%)")
    
    # Metadata analysis
    print("\nMetadata Analysis:")
    print("-" * 40)
    metadata_keys = set()
    for chunk in chunks:
        metadata_keys.update(chunk.get('metadata', {}).keys())
    print(f"Metadata keys present: {metadata_keys}")
    
    # Analyze each metadata field
    for key in metadata_keys:
        values = [chunk.get('metadata', {}).get(key) for chunk in chunks if key in chunk.get('metadata', {})]
        if values:
            print(f"\n{key} analysis:")
            print(f"- Present in {len(values)} chunks")
            print(f"- Unique values: {len(set(values))}")
    
    # Content analysis
    print("\nContent Analysis:")
    print("-" * 40)
    code_chunks = sum(1 for chunk in chunks if '```python' in chunk['content'])
    header_chunks = sum(1 for chunk in chunks if any(line.strip().startswith('#') for line in chunk['content'].split('\n')))
    
    print(f"Chunks with code blocks: {code_chunks} ({(code_chunks/len(chunks)*100):.1f}%)")
    print(f"Chunks with markdown headers: {header_chunks} ({(header_chunks/len(chunks)*100):.1f}%)")
    
    # Display sample chunks
    print("\nDisplaying first 3 chunks as samples:")
    for i, chunk in enumerate(chunks[:3], 1):
        print("\n" + "=" * 80)
        print(f"Chunk {i}:")
        print("=" * 80)
        print("\nMetadata:")
        print("-" * 40)
        for key, value in chunk.get('metadata', {}).items():
            print(f"{key}: {value}")
        print("\nContent Preview (first 200 chars):")
        print(chunk['content'][:200] + "...")

def main():
    """Analyze chunks from all collections."""
    collections = {
        "API Modules": "api_docs_modules.json",
        "API Classes": "api_docs_classes.json",
        "API Functions": "api_docs_functions.json",
        "Reachy 2 Documentation": "reachy2_docs.json",
        "SDK Documentation": "reachy2_sdk.json",
        "Vision Examples": "vision_examples.json",
        "Tutorials": "reachy2_tutorials.json"
    }
    
    for name, filename in collections.items():
        filepath = os.path.join("external_docs/documents", filename)
        chunks = load_chunks(filepath)
        analyze_chunks(chunks, name)

if __name__ == "__main__":
    main() 