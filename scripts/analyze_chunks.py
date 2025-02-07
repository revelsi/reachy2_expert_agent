#!/usr/bin/env python

import json
import os
from typing import Dict, List
from collections import defaultdict

def load_json_file(filepath: str) -> List[Dict]:
    """Load and parse a JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)

def analyze_chunks(documents: List[Dict]) -> Dict:
    """Analyze chunk sizes and metadata."""
    sizes = [len(doc['content']) for doc in documents]
    
    stats = {
        'total_chunks': len(documents),
        'avg_size': sum(sizes) / len(documents) if sizes else 0,
        'min_size': min(sizes) if sizes else 0,
        'max_size': max(sizes) if sizes else 0,
        'size_distribution': defaultdict(int),
        'metadata_keys': set(),
        'has_code': sum(1 for doc in documents if doc.get('metadata', {}).get('has_code', False))
    }
    
    # Analyze size distribution
    for size in sizes:
        if size <= 500:
            stats['size_distribution']['0-500'] += 1
        elif size <= 1000:
            stats['size_distribution']['501-1000'] += 1
        elif size <= 1500:
            stats['size_distribution']['1001-1500'] += 1
        elif size <= 2000:
            stats['size_distribution']['1501-2000'] += 1
        else:
            stats['size_distribution']['2000+'] += 1
    
    # Collect metadata keys
    for doc in documents:
        stats['metadata_keys'].update(doc.get('metadata', {}).keys())
    
    return stats

def display_chunk_sample(chunk: Dict, index: int):
    """Display a sample chunk with its metadata."""
    print(f"\nChunk {index}:")
    print("=" * 80)
    print("\nMetadata:")
    for key, value in chunk.get('metadata', {}).items():
        print(f"  {key}: {value}")
    
    print("\nContent Preview (first 300 chars):")
    content = chunk['content']
    print(content[:300] + "..." if len(content) > 300 else content)
    print("\n" + "=" * 80)

def main():
    """Analyze all chunk files."""
    collections = {
        'API Classes': 'external_docs/documents/api_docs_classes.json',
        'API Functions': 'external_docs/documents/api_docs_functions.json',
        'SDK Examples': 'external_docs/documents/reachy2_sdk.json',
        'Vision Examples': 'external_docs/documents/vision_examples.json',
        'Tutorials': 'external_docs/documents/reachy2_tutorials.json'
    }
    
    for name, filepath in collections.items():
        print(f"\nAnalyzing {name}:")
        print("=" * 80)
        
        if not os.path.exists(filepath):
            print(f"File not found: {filepath}")
            continue
        
        documents = load_json_file(filepath)
        stats = analyze_chunks(documents)
        
        print(f"\nBasic Statistics:")
        print(f"- Total chunks: {stats['total_chunks']}")
        print(f"- Average size: {stats['avg_size']:.1f} characters")
        print(f"- Minimum size: {stats['min_size']} characters")
        print(f"- Maximum size: {stats['max_size']} characters")
        
        print("\nSize Distribution:")
        total = stats['total_chunks']
        for size_range, count in sorted(stats['size_distribution'].items()):
            percentage = (count / total) * 100
            print(f"- {size_range}: {count} chunks ({percentage:.1f}%)")
        
        print("\nMetadata Keys:", sorted(stats['metadata_keys']))
        if 'has_code' in stats:
            print(f"Chunks with code: {stats['has_code']} ({(stats['has_code']/total)*100:.1f}%)")
        
        print("\nSample Chunks:")
        # Show first chunk and a middle chunk
        if documents:
            display_chunk_sample(documents[0], 1)
            if len(documents) > 1:
                mid_idx = len(documents) // 2
                display_chunk_sample(documents[mid_idx], f"middle ({mid_idx + 1})")

if __name__ == '__main__':
    main() 