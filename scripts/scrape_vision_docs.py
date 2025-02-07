#!/usr/bin/env python
import sys, os, subprocess, shutil
import inspect
import importlib
from typing import get_type_hints, Dict, List, Optional
from pathlib import Path
import json
import ast

# Repository and directory configuration
GIT_URL = "https://github.com/pollen-robotics/pollen-vision.git"

# Output directories
RAW_DOCS_DIR = "raw_docs"
EXTRACTED_DIR = os.path.join(RAW_DOCS_DIR, "extracted")
os.makedirs(EXTRACTED_DIR, exist_ok=True)

# Repository directories
REPO_DIR = os.path.join(RAW_DOCS_DIR, "pollen_vision_repo")
VISION_SOURCE_DIR = os.path.join(REPO_DIR, "pollen_vision", "pollen_vision")
EXAMPLES_SOURCE_DIR = os.path.join(REPO_DIR, "examples")  # Examples in root directory

def clone_or_update_repo():
    """Clone the repository if it doesn't exist, or pull the latest changes."""
    if not os.path.exists(REPO_DIR):
        print(f"Cloning repository: {GIT_URL} into {REPO_DIR}...")
        subprocess.run(["git", "clone", GIT_URL, REPO_DIR], check=True)
    else:
        print("Repository already cloned. Pulling latest changes...")
        subprocess.run(["git", "-C", REPO_DIR, "pull"], check=True)

def extract_vision_documentation() -> List[Dict]:
    """Extract API documentation directly from Python source files."""
    print("\nExtracting Vision API documentation...")
    documented_items = []
    
    # Walk through the vision source directory
    for root, _, files in os.walk(VISION_SOURCE_DIR):
        for file in files:
            if not file.endswith('.py'):
                continue
                
            file_path = os.path.join(root, file)
            module_name = os.path.relpath(file_path, VISION_SOURCE_DIR).replace('/', '.').replace('.py', '')
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    source = f.read()
                
                # Try to parse the source code
                try:
                    tree = ast.parse(source)
                    
                    # Extract module docstring if present
                    module_doc = ast.get_docstring(tree)
                    if module_doc:
                        documented_items.append({
                            'type': 'module',
                            'name': f"pollen_vision.{module_name}",
                            'docstring': inspect.cleandoc(module_doc),
                            'source': module_name
                        })
                    
                    # Process top-level nodes first
                    for node in tree.body:
                        if isinstance(node, ast.ClassDef):
                            class_doc = {
                                'type': 'class',
                                'name': node.name,
                                'module': f"pollen_vision.{module_name}",
                                'docstring': inspect.cleandoc(ast.get_docstring(node) or ''),
                                'methods': [],
                                'source': f"pollen_vision.{module_name}.{node.name}"
                            }
                            
                            # Extract methods
                            for item in node.body:
                                if isinstance(item, ast.FunctionDef):
                                    if not item.name.startswith('_') or item.name == '__init__':
                                        method_source = source[item.lineno-1:item.end_lineno]
                                        method_doc = {
                                            'name': item.name,
                                            'signature': get_function_signature(item),
                                            'docstring': inspect.cleandoc(ast.get_docstring(item) or ''),
                                            'source_code': method_source,
                                            'return_type': get_return_annotation(item),
                                            'parameters': get_parameters(item)
                                        }
                                        class_doc['methods'].append(method_doc)
                            
                            documented_items.append(class_doc)
                        
                        elif isinstance(node, ast.FunctionDef):
                            if not node.name.startswith('_'):
                                func_source = source[node.lineno-1:node.end_lineno]
                                func_doc = {
                                    'type': 'function',
                                    'name': node.name,
                                    'module': f"pollen_vision.{module_name}",
                                    'signature': get_function_signature(node),
                                    'docstring': inspect.cleandoc(ast.get_docstring(node) or ''),
                                    'source_code': func_source,
                                    'return_type': get_return_annotation(node),
                                    'parameters': get_parameters(node),
                                    'source': f"pollen_vision.{module_name}.{node.name}"
                                }
                                documented_items.append(func_doc)
                
                except SyntaxError as e:
                    print(f"Syntax error in {file_path}: {e}")
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
            
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
    
    return documented_items

def get_function_signature(node: ast.FunctionDef) -> str:
    """Extract function signature from AST node."""
    args = []
    
    # Add positional args
    for arg in node.args.args:
        arg_str = arg.arg
        if arg.annotation:
            arg_str += f": {ast.unparse(arg.annotation)}"
        args.append(arg_str)
    
    # Add vararg if present
    if node.args.vararg:
        args.append(f"*{node.args.vararg.arg}")
    
    # Add keyword args
    for arg in node.args.kwonlyargs:
        arg_str = arg.arg
        if arg.annotation:
            arg_str += f": {ast.unparse(arg.annotation)}"
        args.append(arg_str)
    
    # Add kwargs if present
    if node.args.kwarg:
        args.append(f"**{node.args.kwarg.arg}")
    
    # Add return annotation if present
    returns = f" -> {ast.unparse(node.returns)}" if node.returns else ""
    
    return f"({', '.join(args)}){returns}"

def get_return_annotation(node: ast.FunctionDef) -> Optional[str]:
    """Extract return type annotation from AST node."""
    if node.returns:
        return ast.unparse(node.returns)
    return None

def get_parameters(node: ast.FunctionDef) -> Dict[str, str]:
    """Extract parameter annotations from AST node."""
    params = {}
    for arg in node.args.args:
        if arg.annotation:
            params[arg.arg] = ast.unparse(arg.annotation)
        else:
            params[arg.arg] = "Any"
    return params

def collect_examples() -> List[Dict]:
    """Collect examples from the examples directory."""
    print("\nCollecting examples...")
    examples = []
    
    if os.path.exists(EXAMPLES_SOURCE_DIR):
        print(f"Processing examples from: {EXAMPLES_SOURCE_DIR}")
        for root, _, files in os.walk(EXAMPLES_SOURCE_DIR):
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, EXAMPLES_SOURCE_DIR)
                
                try:
                    if file.endswith('.py'):
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        examples.append({
                            'content': content,
                            'metadata': {
                                'source': rel_path,
                                'type': 'example',
                                'format': 'python',
                                'collection': 'vision_examples',
                                'title': os.path.splitext(file)[0]
                            }
                        })
                        print(f"Found Python example: {rel_path}")
                    
                    elif file.endswith('.ipynb'):
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        examples.append({
                            'content': content,
                            'metadata': {
                                'source': rel_path,
                                'type': 'example',
                                'format': 'notebook',
                                'collection': 'vision_examples',
                                'title': os.path.splitext(file)[0]
                            }
                        })
                        print(f"Found notebook example: {rel_path}")
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
    else:
        print(f"Warning: Examples directory not found at {EXAMPLES_SOURCE_DIR}")
    
    return examples

def save_documentation(vision_docs: List[Dict], examples: List[Dict]):
    """Save vision documentation and examples to appropriate directories."""
    print("\nSaving documentation...")
    
    # Save Vision API documentation
    vision_docs_path = os.path.join(EXTRACTED_DIR, "raw_vision_docs.json")
    with open(vision_docs_path, 'w', encoding='utf-8') as f:
        json.dump(vision_docs, f, indent=2)
    print(f"Saved {len(vision_docs)} Vision API documentation items to {vision_docs_path}")
    
    # Save examples
    examples_path = os.path.join(EXTRACTED_DIR, "raw_vision_examples.json")
    with open(examples_path, 'w', encoding='utf-8') as f:
        json.dump(examples, f, indent=2)
    print(f"Saved {len(examples)} examples to {examples_path}")

def main():
    """Main function to scrape all Vision API documentation."""
    # Step 1: Clone/update the repository
    clone_or_update_repo()
    
    # Step 2: Extract Vision API documentation via AST parsing
    vision_docs = extract_vision_documentation()
    print(f"Extracted documentation for {len(vision_docs)} items")
    
    # Step 3: Collect examples
    examples = collect_examples()
    print(f"Collected {len(examples)} examples")
    
    # Step 4: Save documentation and examples
    save_documentation(vision_docs, examples)
    
    print("\nVision documentation scraping complete!")

if __name__ == "__main__":
    main() 