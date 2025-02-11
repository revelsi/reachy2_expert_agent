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
    # Replace single newlines with spaces
    text = re.sub(r'\n', ' ', text)
    # Replace multiple spaces with a single space
    text = re.sub(r' +', ' ', text)
    return text.strip()

def split_text(text: str, max_chunk_size: int = MAX_CHUNK_SIZE, overlap_size: int = OVERLAP_SIZE) -> List[str]:
    """Split text into overlapping chunks of roughly equal size."""
    if not text:
        return []
    
    if len(text) <= max_chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        # Calculate end position for this chunk
        end = min(start + max_chunk_size, len(text))
        
        # If this is not the end of text, try to find a good break point
        if end < len(text):
            # Look for sentence end within the last 20% of the chunk
            search_start = max(start, end - int(max_chunk_size * 0.2))
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

def extract_code_blocks(text: str) -> List[Dict]:
    """Extract code blocks and their surrounding context from text."""
    blocks = []
    lines = text.split('\n')
    current_context = []
    current_code = []
    in_code_block = False
    
    for line in lines:
        if line.strip().startswith('```python'):
            in_code_block = True
            if current_context:
                blocks.append({'context': current_context, 'code': []})
                current_context = []
        elif line.strip() == '```' and in_code_block:
            in_code_block = False
            if current_code:
                blocks.append({'context': current_context, 'code': current_code})
                current_context = []
                current_code = []
        elif in_code_block:
            current_code.append(line)
        else:
            current_context.append(line)
    
    # Add any remaining content
    if current_context:
        blocks.append({'context': current_context, 'code': []})
    
    return blocks

def chunk_markdown_docs(raw_docs: List[Dict]) -> List[Dict]:
    """Process markdown documentation into semantic chunks."""
    chunks = []
    
    for doc in raw_docs:
        try:
            print(f"\nProcessing document: {doc.get('metadata', {}).get('source', 'unknown')}")
            content = doc['content']
            metadata = doc['metadata']
            
            # Split content at major headers (h1 and h2) while capturing header hierarchy
            sections = []
            current_section = []
            header_stack = []  # Track header hierarchy
            lines = content.split('\n')
            
            # Debug: Print initial content size
            print(f"Document size: {len(content)} characters")
            
            for line in lines:
                try:
                    # New section only at h1 and h2 headers to keep related content together
                    if line.strip().startswith('#') and (
                        line.strip().startswith('# ') or 
                        line.strip().startswith('## ')
                    ):
                        # Save previous section if exists and not too small
                        if current_section:
                            section_content = '\n'.join(current_section)
                            # Only create new section if significant content
                            if len(section_content) > 100:
                                sections.append({
                                    'content': section_content,
                                    'headers': list(header_stack)
                                })
                                print(f"Created section with {len(section_content)} chars at header: {line.strip()}")
                                current_section = []
                            
                        # Update header stack
                        header_level = len(line) - len(line.lstrip('#'))
                        # Pop headers until we're at the right level
                        while header_stack and len(header_stack) >= header_level:
                            header_stack.pop()
                        header_stack.append(line.strip())
                    
                    current_section.append(line)
                except Exception as e:
                    print(f"Error processing line: {line}")
                    print(f"Error: {str(e)}")
                    continue
            
            # Add final section if significant
            if current_section:
                section_content = '\n'.join(current_section)
                if len(section_content) > 100:
                    sections.append({
                        'content': section_content,
                        'headers': list(header_stack)
                    })
                    print(f"Created final section with {len(section_content)} chars")
            
            print(f"Found {len(sections)} sections")
            
            # Process each section
            for i, section in enumerate(sections):
                try:
                    # Extract code blocks and their context
                    blocks = extract_code_blocks(section['content'])
                    current_chunk = []
                    current_size = 0
                    
                    # Get section navigation safely
                    prev_header = sections[i-1]['headers'][-1] if i > 0 and sections[i-1]['headers'] else None
                    next_header = sections[i+1]['headers'][-1] if i < len(sections)-1 and sections[i+1]['headers'] else None
                    
                    # Add header context from parent sections
                    section_context = '\n'.join(section['headers']) + '\n\n' if section['headers'] else ''
                    
                    # If section is small enough, keep it as one chunk
                    if len(section['content']) <= MAX_CHUNK_SIZE:
                        chunks.append({
                            'content': section['content'],
                            'metadata': {
                                **metadata,
                                'chunk_index': len(chunks),
                                'has_code': '```python' in section['content'],
                                'section_path': ' > '.join(section['headers']) if section['headers'] else '',
                                'prev_section': prev_header,
                                'next_section': next_header
                            }
                        })
                        continue
                    
                    # Combine blocks that would fit together
                    combined_blocks = []
                    current_combined = []
                    combined_size = 0
                    
                    for block in blocks:
                        block_text = '\n'.join(block['context'])
                        if block['code']:
                            block_text += '\n```python\n' + '\n'.join(block['code']) + '\n```\n'
                        
                        # If adding this block would exceed chunk size, save current combination
                        if combined_size + len(block_text) > MAX_CHUNK_SIZE and current_combined:
                            combined_blocks.append('\n'.join(current_combined))
                            current_combined = [block_text]
                            combined_size = len(block_text)
                        else:
                            current_combined.append(block_text)
                            combined_size += len(block_text)
                    
                    # Add any remaining combined blocks
                    if current_combined:
                        combined_blocks.append('\n'.join(current_combined))
                    
                    # Process combined blocks
                    for block_content in combined_blocks:
                        if len(block_content) <= MAX_CHUNK_SIZE:
                            chunks.append({
                                'content': block_content,
                                'metadata': {
                                    **metadata,
                                    'chunk_index': len(chunks),
                                    'has_code': '```python' in block_content,
                                    'section_path': ' > '.join(section['headers']) if section['headers'] else '',
                                    'prev_section': prev_header,
                                    'next_section': next_header
                                }
                            })
                        else:
                            # Split while preserving markdown structure
                            sub_chunks = split_text(block_content, MAX_CHUNK_SIZE, OVERLAP_SIZE)
                            for j, sub_chunk in enumerate(sub_chunks):
                                chunks.append({
                                    'content': sub_chunk,
                                    'metadata': {
                                        **metadata,
                                        'chunk_index': len(chunks),
                                        'has_code': '```python' in sub_chunk,
                                        'section_path': ' > '.join(section['headers']) if section['headers'] else '',
                                        'sub_chunk': j + 1,
                                        'total_sub_chunks': len(sub_chunks),
                                        'prev_section': prev_header,
                                        'next_section': next_header
                                    }
                                })
                    
                except Exception as e:
                    print(f"Error processing section {i}: {str(e)}")
                    continue
            
            print(f"Created {len(chunks)} chunks")
            
        except Exception as e:
            print(f"Error processing document {doc.get('metadata', {}).get('source', 'unknown')}: {str(e)}")
            print("Document content preview:", doc.get('content', '')[:200])
            continue
    
    return chunks

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
    print("\nProcessing API documentation...")
    api_docs = load_json_file(os.path.join(RAW_DOCS_DIR, "raw_api_docs.json"))
    if api_docs:
        print(f"Found {len(api_docs)} API documents")
        chunks = chunk_api_docs(api_docs)
        save_chunks(chunks['modules'], os.path.join(OUTPUT_DIR, "api_docs_modules.json"))
        save_chunks(chunks['classes'], os.path.join(OUTPUT_DIR, "api_docs_classes.json"))
        save_chunks(chunks['functions'], os.path.join(OUTPUT_DIR, "api_docs_functions.json"))
    
    # Process Reachy 2 documentation
    print("\nProcessing Reachy 2 documentation...")
    reachy2_docs = load_json_file(os.path.join(RAW_DOCS_DIR, "raw_reachy2_docs.json"))
    if reachy2_docs:
        print(f"Found {len(reachy2_docs)} Reachy 2 documents")
        chunks = chunk_markdown_docs(reachy2_docs)
        save_chunks(chunks, os.path.join(OUTPUT_DIR, "reachy2_docs.json"))
    
    # Process SDK examples
    print("\nProcessing SDK examples...")
    sdk_examples = load_json_file(os.path.join(RAW_DOCS_DIR, "raw_sdk_examples.json"))
    if sdk_examples:
        print(f"Found {len(sdk_examples)} SDK examples")
        chunks = chunk_examples(sdk_examples, "reachy2_sdk")
        save_chunks(chunks, os.path.join(OUTPUT_DIR, "reachy2_sdk.json"))
    
    # Process Vision examples
    print("\nProcessing Vision examples...")
    vision_examples = load_json_file(os.path.join(RAW_DOCS_DIR, "raw_vision_examples.json"))
    if vision_examples:
        print(f"Found {len(vision_examples)} Vision examples")
        chunks = chunk_examples(vision_examples, "vision_examples")
        save_chunks(chunks, os.path.join(OUTPUT_DIR, "vision_examples.json"))
    
    # Process tutorials
    print("\nProcessing tutorials...")
    tutorials = load_json_file(os.path.join(RAW_DOCS_DIR, "raw_tutorials.json"))
    if tutorials:
        print(f"Found {len(tutorials)} tutorials")
        chunks = chunk_examples(tutorials, "reachy2_tutorials")
        save_chunks(chunks, os.path.join(OUTPUT_DIR, "reachy2_tutorials.json"))
    
    print("\nChunking process complete!")

if __name__ == "__main__":
    main() 