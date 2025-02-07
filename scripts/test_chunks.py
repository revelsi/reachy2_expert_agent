import json
import os
from typing import Dict, List

def load_json_file(filepath: str) -> List[Dict]:
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return []
    with open(filepath, 'r') as f:
        return json.load(f)

def analyze_chunks(filepath: str, collection_name: str):
    print(f"\nAnalyzing {collection_name}:")
    print("=" * 80)
    
    chunks = load_json_file(filepath)
    if not chunks:
        return
    
    # Basic statistics
    total_chunks = len(chunks)
    print(f"\nBasic Statistics:")
    print("-" * 40)
    print(f"Total chunks: {total_chunks}")
    
    # Character count statistics
    sizes = [len(chunk.get('content', '')) for chunk in chunks]
    avg_size = sum(sizes) / len(sizes)
    median_size = sorted(sizes)[len(sizes)//2]
    std_dev = (sum((x - avg_size) ** 2 for x in sizes) / len(sizes)) ** 0.5
    
    print(f"Character count statistics:")
    print(f"- Average size: {avg_size:.2f} characters")
    print(f"- Median size: {median_size} characters")
    print(f"- Standard deviation: {std_dev:.2f} characters")
    print(f"- Smallest chunk: {min(sizes)} characters")
    print(f"- Largest chunk: {max(sizes)} characters")
    
    # Size distribution
    size_ranges = [(0, 500), (501, 1000), (1001, 1500), (1501, 2000), (2001, float('inf'))]
    print("\nSize distribution:")
    for start, end in size_ranges:
        count = sum(1 for size in sizes if start <= size <= end)
        percentage = (count / total_chunks) * 100
        print(f"- {start}-{end if end != float('inf') else '+'} chars: {count} chunks ({percentage:.1f}%)")
    
    # Metadata analysis
    print("\nMetadata Analysis:")
    print("-" * 40)
    
    # Collect all unique metadata keys
    metadata_keys = set()
    for chunk in chunks:
        metadata_keys.update(chunk.keys())
    metadata_keys.discard('content')  # Remove content as it's not metadata
    
    print("Metadata keys present:", metadata_keys)
    
    # Analyze values for each metadata key
    for key in metadata_keys:
        values = [chunk.get(key) for chunk in chunks if key in chunk]
        unique_values = set(str(v) for v in values if v is not None)
        print(f"\n{key} analysis:")
        print(f"- Present in {len(values)} chunks")
        print(f"- Unique values: {len(unique_values)}")
        if len(unique_values) <= 10:  # Only show all values if there aren't too many
            print(f"- Values: {sorted(unique_values)}")
    
    # Content type analysis
    print("\nContent Analysis:")
    print("-" * 40)
    code_chunks = sum(1 for chunk in chunks if '```python' in chunk.get('content', ''))
    markdown_chunks = sum(1 for chunk in chunks if '###' in chunk.get('content', ''))
    print(f"Chunks with code blocks: {code_chunks} ({(code_chunks/total_chunks)*100:.1f}%)")
    print(f"Chunks with markdown headers: {markdown_chunks} ({(markdown_chunks/total_chunks)*100:.1f}%)")
    
    # Display sample chunks
    print(f"\nDisplaying first 3 chunks as samples:\n")
    for i, chunk in enumerate(chunks[:3], 1):
        print("=" * 80)
        print(f"Chunk {i}:")
        print("=" * 80)
        print("\nMetadata:")
        print("-" * 40)
        for key, value in chunk.items():
            if key != 'content':
                print(f"{key}: {value}")
        print("\nContent Preview (first 200 chars):")
        content = chunk.get('content', '')
        print(content[:200] + "..." if len(content) > 200 else content)
        print()

def main():
    collections = {
        'API Classes': 'external_docs/documents/api_docs_classes.json',
        'API Functions': 'external_docs/documents/api_docs_functions.json',
        'SDK Documentation': 'external_docs/documents/reachy2_sdk.json',
        'Vision Examples': 'external_docs/documents/vision_examples.json',
        'Tutorials': 'external_docs/documents/reachy2_tutorials.json'
    }
    
    for name, filepath in collections.items():
        analyze_chunks(filepath, name)

if __name__ == '__main__':
    main() 