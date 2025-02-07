#!/usr/bin/env python

import json
import os
from typing import List, Dict
import re

# Constants for chunking
MAX_CHUNK_SIZE = 1500
OVERLAP_SIZE = 300

# Input/Output paths
RAW_DOCS_DIR = "raw_docs/extracted"
OUTPUT_DIR = "external_docs/documents"

def load_json_file(filepath: str) -> List[Dict]:
    """Load a JSON file containing raw documents."""
    if not os.path.exists(filepath):
        print(f"Warning: File not found - {filepath}")
        return []
    with open(filepath, 'r') as f:
        return json.load(f)

def save_chunks(chunks: List[Dict], filepath: str):
    """Save chunks to a JSON file."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w') as f:
        json.dump(chunks, f, indent=2)
    print(f"Saved {len(chunks)} chunks to {filepath}")

def clean_text(text: str) -> str:
    """Clean text by removing extra whitespace and normalizing newlines."""
    # Replace multiple newlines with a single newline
    text = re.sub(r'\n\s*\n', '\n\n', text)
    # Replace multiple spaces with a single space
    text = re.sub(r' +', ' ', text)
    return text.strip()

def split_text(text: str, max_size: int = MAX_CHUNK_SIZE, overlap_size: int = OVERLAP_SIZE) -> List[str]:
    """Split text into overlapping chunks of roughly equal size."""
    if not text:
        return []
    
    if len(text) <= max_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        # Calculate end position for this chunk
        end = min(start + max_size, len(text))
        
        # If this is not the end of text, try to find a good break point
        if end < len(text):
            # Look for sentence end within the last 20% of the chunk
            search_start = max(start, end - int(max_size * 0.2))
            break_point = -1
            
            # Try sentence endings first
            for pattern in ['. ', '.\n', '? ', '! ']:
                pos = text.rfind(pattern, search_start, end)
                if pos > break_point:
                    break_point = pos + len(pattern)
            
            # If no sentence ending found, try line breaks
            if break_point == -1:
                pos = text.rfind('\n', search_start, end)
                if pos > -1:
                    break_point = pos + 1
            
            # If still no break point, just break at a space
            if break_point == -1:
                pos = text.rfind(' ', search_start, end)
                if pos > -1:
                    break_point = pos + 1
            
            # If no good break point found, just use the calculated end
            if break_point > -1:
                end = break_point
        
        # Extract chunk
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        # Calculate next start position with overlap
        start = max(start + 1, end - overlap_size)
    
    return chunks

def chunk_api_docs(raw_docs: List[Dict]) -> Dict[str, List[Dict]]:
    """Process API documentation into chunks with appropriate context."""
    chunks = {
        'modules': [],  # Add module-level documentation
        'classes': [],
        'functions': []
    }
    
    for item in raw_docs:
        try:
            if item['type'] == 'module':
                # Process module documentation
                content = f"Module: {item['name']}\n\n"
                content += f"Documentation:\n{item.get('docstring', 'No documentation available.')}\n"
                
                chunks['modules'].append({
                    'content': content,
                    'metadata': {
                        'source': item['name'],
                        'type': 'module',
                        'name': item['name']
                    }
                })
            
            elif item['type'] == 'class':
                # Create main class chunk with overview
                class_content = f"Class: {item['name']}\nModule: {item['module']}\n\n"
                class_content += f"Documentation:\n{item.get('docstring', 'No documentation available.')}\n"
                
                # Add method summary
                if 'methods' in item:
                    class_content += "\nMethods:\n"
                    for method in item['methods']:
                        class_content += f"- {method['name']}{method.get('signature', '')}\n"
                
                # Add class overview chunk
                chunks['classes'].append({
                    'content': class_content,
                    'metadata': {
                        'source': f"{item['module']}.{item['name']}",
                        'type': 'class',
                        'name': item['name'],
                        'module': item['module'],
                        'chunk_type': 'overview'
                    }
                })
                
                # Add individual method chunks
                if 'methods' in item:
                    for method in item['methods']:
                        method_content = f"Method: {method['name']}\n"
                        method_content += f"Class: {item['name']}\n"
                        method_content += f"Module: {item['module']}\n\n"
                        
                        if 'signature' in method:
                            method_content += f"Signature: {method['signature']}\n\n"
                        if 'docstring' in method:
                            method_content += f"Documentation:\n{method['docstring']}\n\n"
                        if 'source_code' in method:
                            method_content += f"Implementation:\n```python\n{method['source_code']}\n```\n"
                        
                        chunks['classes'].append({
                            'content': method_content,
                            'metadata': {
                                'source': f"{item['module']}.{item['name']}.{method['name']}",
                                'type': 'class',
                                'name': item['name'],
                                'module': item['module'],
                                'method': method['name'],
                                'chunk_type': 'method'
                            }
                        })
            
            elif item['type'] == 'function':
                # Process standalone functions (not class methods)
                function_content = f"Function: {item['name']}"
                if 'signature' in item:
                    function_content += f"{item['signature']}\n"
                function_content += f"Module: {item['module']}\n\n"
                
                if 'docstring' in item:
                    function_content += f"Documentation:\n{item['docstring']}\n"
                
                if 'source_code' in item:
                    function_content += f"\nImplementation:\n```python\n{item['source_code']}\n```\n"
                
                # Split function content into chunks if needed
                function_chunks = split_text(function_content)
                for i, chunk in enumerate(function_chunks):
                    chunks['functions'].append({
                        'content': chunk,
                        'metadata': {
                            'source': f"{item['module']}.{item['name']}",
                            'type': 'function',
                            'name': item['name'],
                            'module': item['module'],
                            'chunk_index': i,
                            'total_chunks': len(function_chunks)
                        }
                    })
        
        except Exception as e:
            print(f"Error processing item: {item.get('name', 'unknown')}")
            print(f"Error: {str(e)}")
            continue
    
    return chunks

def extract_code_blocks(text: str) -> List[Dict[str, str]]:
    """Extract code blocks and their surrounding context."""
    blocks = []
    lines = text.split('\n')
    current_block = {'context': [], 'code': []}
    in_code = False
    code_fence_count = 0  # Track nested code fences
    
    for line in lines:
        if line.startswith('```'):
            if 'python' in line:
                code_fence_count += 1
                in_code = True
                if current_block['context'] and code_fence_count == 1:
                    blocks.append(dict(current_block))
                    current_block = {'context': [], 'code': []}
            elif in_code:
                code_fence_count -= 1
                if code_fence_count == 0:
                    in_code = False
                    if current_block['code']:
                        blocks.append(dict(current_block))
                        current_block = {'context': [], 'code': []}
        elif in_code:
            current_block['code'].append(line)
        else:
            current_block['context'].append(line)
    
    # Handle any unclosed code blocks
    if in_code and current_block['code']:
        blocks.append(dict(current_block))
    elif current_block['context']:
        blocks.append(dict(current_block))
    
    return blocks

def chunk_examples(raw_docs: List[Dict], collection: str) -> List[Dict]:
    """Process code examples and tutorials into chunks."""
    chunks = []
    max_chunk_size = MAX_CHUNK_SIZE * 1.5  # Allow slightly larger chunks for examples
    
    for doc in raw_docs:
        try:
            content = doc['content']
            metadata = doc['metadata']
            
            if metadata.get('format') == 'notebook':
                # Split at markdown headers and code blocks
                blocks = extract_code_blocks(content)
                
                current_chunk = []
                current_size = 0
                
                for block in blocks:
                    # Format block content
                    block_text = '\n'.join(block['context'])
                    if block['code']:
                        block_text += '\n```python\n' + '\n'.join(block['code']) + '\n```\n'
                    
                    block_size = len(block_text)
                    
                    # If this block would make the chunk too big, save current chunk
                    if current_size + block_size > max_chunk_size and current_chunk:
                        chunk_content = '\n\n'.join(current_chunk)
                        chunks.append({
                            'content': chunk_content,
                            'metadata': {
                                **metadata,
                                'chunk_index': len(chunks),
                                'has_code': '```python' in chunk_content
                            }
                        })
                        current_chunk = []
                        current_size = 0
                    
                    # If single block is too big, split it
                    if block_size > max_chunk_size:
                        # Keep context with first part of code
                        context = '\n'.join(block['context'])
                        code_parts = split_text('\n'.join(block['code']), max_chunk_size - len(context))
                        
                        for i, code_part in enumerate(code_parts):
                            chunk_content = context if i == 0 else f"(Continued from part {i})\n"
                            chunk_content += f"\n```python\n{code_part}\n```\n"
                            chunks.append({
                                'content': chunk_content,
                                'metadata': {
                                    **metadata,
                                    'chunk_index': len(chunks),
                                    'has_code': True,
                                    'code_part': i + 1,
                                    'total_parts': len(code_parts)
                                }
                            })
                    else:
                        current_chunk.append(block_text)
                        current_size += block_size
                
                # Save any remaining content
                if current_chunk:
                    chunk_content = '\n\n'.join(current_chunk)
                    chunks.append({
                        'content': chunk_content,
                        'metadata': {
                            **metadata,
                            'chunk_index': len(chunks),
                            'has_code': '```python' in chunk_content
                        }
                    })
            
            else:  # Regular code examples
                # Extract and process code blocks
                blocks = extract_code_blocks(content)
                current_chunk = []
                current_size = 0
                
                for block in blocks:
                    block_text = '\n'.join(block['context'])
                    if block['code']:
                        block_text += '\n```python\n' + '\n'.join(block['code']) + '\n```\n'
                    
                    block_size = len(block_text)
                    
                    if current_size + block_size > max_chunk_size and current_chunk:
                        chunks.append({
                            'content': '\n'.join(current_chunk),
                            'metadata': {
                                **metadata,
                                'chunk_index': len(chunks),
                                'has_code': any('```python' in block for block in current_chunk)
                            }
                        })
                        current_chunk = []
                        current_size = 0
                    
                    if block_size > max_chunk_size:
                        # Split large blocks while preserving structure
                        if block['context']:
                            chunks.append({
                                'content': '\n'.join(block['context']),
                                'metadata': {
                                    **metadata,
                                    'chunk_index': len(chunks),
                                    'has_code': False
                                }
                            })
                        
                        code_text = '\n'.join(block['code'])
                        for i, code_part in enumerate(split_text(code_text, max_chunk_size - 100)):
                            chunks.append({
                                'content': f"```python\n{code_part}\n```",
                                'metadata': {
                                    **metadata,
                                    'chunk_index': len(chunks),
                                    'has_code': True,
                                    'code_part': i + 1
                                }
                            })
                    else:
                        current_chunk.append(block_text)
                        current_size += block_size
                
                if current_chunk:
                    chunks.append({
                        'content': '\n'.join(current_chunk),
                        'metadata': {
                            **metadata,
                            'chunk_index': len(chunks),
                            'has_code': any('```python' in block for block in current_chunk)
                        }
                    })
        
        except Exception as e:
            print(f"Error processing {doc.get('source', 'unknown document')}: {str(e)}")
            continue
    
    return chunks

def main():
    """Process all raw documents into chunks."""
    print("\nProcessing raw documentation into chunks...")
    
    # Clean up existing chunked documents
    print("\nCleaning up existing chunked documents...")
    if os.path.exists(OUTPUT_DIR):
        for file in os.listdir(OUTPUT_DIR):
            if file.endswith('.json'):
                os.remove(os.path.join(OUTPUT_DIR, file))
    
    # Process API documentation
    api_docs = load_json_file(os.path.join(RAW_DOCS_DIR, "raw_api_docs.json"))
    if api_docs:
        chunks = chunk_api_docs(api_docs)
        save_chunks(chunks['modules'], os.path.join(OUTPUT_DIR, "api_docs_modules.json"))
        save_chunks(chunks['classes'], os.path.join(OUTPUT_DIR, "api_docs_classes.json"))
        save_chunks(chunks['functions'], os.path.join(OUTPUT_DIR, "api_docs_functions.json"))
    
    # Process SDK examples
    sdk_examples = load_json_file(os.path.join(RAW_DOCS_DIR, "raw_sdk_examples.json"))
    if sdk_examples:
        chunks = chunk_examples(sdk_examples, "reachy2_sdk")
        save_chunks(chunks, os.path.join(OUTPUT_DIR, "reachy2_sdk.json"))
    
    # Process Vision examples
    vision_examples = load_json_file(os.path.join(RAW_DOCS_DIR, "raw_vision_examples.json"))
    if vision_examples:
        chunks = chunk_examples(vision_examples, "vision_examples")
        save_chunks(chunks, os.path.join(OUTPUT_DIR, "vision_examples.json"))
    
    # Process tutorials
    tutorials = load_json_file(os.path.join(RAW_DOCS_DIR, "raw_tutorials.json"))
    if tutorials:
        chunks = chunk_examples(tutorials, "reachy2_tutorials")
        save_chunks(chunks, os.path.join(OUTPUT_DIR, "reachy2_tutorials.json"))
    
    print("\nChunking process complete!")

if __name__ == "__main__":
    main() 