#!/usr/bin/env python

import json
import os
from collections import defaultdict
from typing import Dict, List, Set

# Paths
RAW_DOCS_DIR = "raw_docs/extracted"
OUTPUT_DIR = "external_docs/documents"

def load_json_file(filepath: str) -> List[Dict]:
    """Load a JSON file containing documents."""
    if not os.path.exists(filepath):
        print(f"Warning: File not found - {filepath}")
        return []
    with open(filepath, 'r') as f:
        return json.load(f)

def analyze_api_coverage():
    """Analyze coverage of API documentation."""
    print("\nAnalyzing API Documentation Coverage")
    print("=" * 80)
    
    # Load raw API docs
    raw_docs = load_json_file(os.path.join(RAW_DOCS_DIR, "raw_api_docs.json"))
    if not raw_docs:
        print("No raw API documentation found!")
        return
    
    # Count items in raw docs
    raw_counts = defaultdict(int)
    raw_items = defaultdict(set)
    for item in raw_docs:
        item_type = item.get('type', 'unknown')
        raw_counts[item_type] += 1
        raw_items[item_type].add(f"{item.get('module', '')}.{item.get('name', '')}")
    
    print("\nRaw Documentation Contents:")
    print("-" * 40)
    for item_type, count in raw_counts.items():
        print(f"{item_type.capitalize()}: {count} items")
    
    # Load processed chunks
    processed_modules = load_json_file(os.path.join(OUTPUT_DIR, "api_docs_modules.json"))
    processed_classes = load_json_file(os.path.join(OUTPUT_DIR, "api_docs_classes.json"))
    processed_functions = load_json_file(os.path.join(OUTPUT_DIR, "api_docs_functions.json"))
    
    # Extract unique items from processed chunks
    processed_items = defaultdict(set)
    
    # Process modules
    for chunk in processed_modules:
        if chunk.get('metadata', {}).get('type') == 'module':
            name = chunk.get('metadata', {}).get('name', '')
            processed_items['module'].add(name)
    
    # Process classes (accounting for continuation chunks)
    class_chunks = defaultdict(list)
    for chunk in processed_classes:
        metadata = chunk.get('metadata', {})
        if metadata.get('type') == 'class':
            key = f"{metadata.get('module', '')}.{metadata.get('name', '')}"
            class_chunks[key].append(chunk)
            processed_items['class'].add(key)
    
    # Process functions (accounting for implementation chunks)
    function_chunks = defaultdict(list)
    for chunk in processed_functions:
        metadata = chunk.get('metadata', {})
        if metadata.get('type') in ['function', 'function_implementation']:
            key = f"{metadata.get('module', '')}.{metadata.get('name', '')}"
            function_chunks[key].append(chunk)
            if metadata.get('type') == 'function':
                processed_items['function'].add(key)
    
    print("\nProcessed Documentation Contents:")
    print("-" * 40)
    for item_type, items in processed_items.items():
        print(f"{item_type.capitalize()}: {len(items)} items")
    
    # Compare coverage
    print("\nCoverage Analysis:")
    print("-" * 40)
    for item_type in raw_items.keys():
        raw_set = raw_items[item_type]
        processed_set = processed_items[item_type]
        
        missing = raw_set - processed_set
        extra = processed_set - raw_set
        
        print(f"\n{item_type.capitalize()}:")
        print(f"Coverage: {len(processed_set)}/{len(raw_set)} ({(len(processed_set)/len(raw_set)*100 if raw_set else 0):.1f}%)")
        
        if missing:
            print("Missing items:")
            for item in sorted(missing):
                print(f"  - {item}")
        
        if extra:
            print("Extra items (in processed but not in raw):")
            for item in sorted(extra):
                print(f"  - {item}")

def analyze_example_coverage():
    """Analyze coverage of examples and tutorials."""
    print("\nAnalyzing Examples and Tutorials Coverage")
    print("=" * 80)
    
    # Analyze SDK examples
    raw_sdk = load_json_file(os.path.join(RAW_DOCS_DIR, "raw_sdk_examples.json"))
    processed_sdk = load_json_file(os.path.join(OUTPUT_DIR, "reachy2_sdk.json"))
    
    print("\nSDK Examples:")
    print("-" * 40)
    if raw_sdk:
        raw_examples = {ex.get('metadata', {}).get('source', 'unknown') for ex in raw_sdk}
        processed_examples = {chunk.get('metadata', {}).get('source', 'unknown') for chunk in processed_sdk}
        
        print(f"Raw examples: {len(raw_examples)}")
        print(f"Processed chunks: {len(processed_sdk)}")
        print(f"Unique examples in chunks: {len(processed_examples)}")
        
        missing = raw_examples - processed_examples
        if missing:
            print("\nMissing examples:")
            for ex in sorted(missing):
                print(f"  - {ex}")
    
    # Analyze tutorials
    raw_tutorials = load_json_file(os.path.join(RAW_DOCS_DIR, "raw_tutorials.json"))
    processed_tutorials = load_json_file(os.path.join(OUTPUT_DIR, "reachy2_tutorials.json"))
    
    print("\nTutorials:")
    print("-" * 40)
    if raw_tutorials:
        raw_tut = {tut.get('metadata', {}).get('source', 'unknown') for tut in raw_tutorials}
        processed_tut = {chunk.get('metadata', {}).get('source', 'unknown') for chunk in processed_tutorials}
        
        print(f"Raw tutorials: {len(raw_tut)}")
        print(f"Processed chunks: {len(processed_tutorials)}")
        print(f"Unique tutorials in chunks: {len(processed_tut)}")
        
        missing = raw_tut - processed_tut
        if missing:
            print("\nMissing tutorials:")
            for tut in sorted(missing):
                print(f"  - {tut}")

def main():
    """Main function to analyze documentation coverage."""
    analyze_api_coverage()
    analyze_example_coverage()

if __name__ == "__main__":
    main() 