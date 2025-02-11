#!/usr/bin/env python
import ast
import importlib
import inspect
import json
import os
import pkgutil
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, get_type_hints

import nbformat

# Repository and directory configuration
GIT_URL = "https://github.com/pollen-robotics/reachy2-sdk.git"

# Output directories
RAW_DOCS_DIR = "data/raw_docs"
EXTRACTED_DIR = os.path.join(RAW_DOCS_DIR, "extracted")
EXTERNAL_DOCS_DIR = "data/external_docs/documents"
os.makedirs(EXTRACTED_DIR, exist_ok=True)
os.makedirs(EXTERNAL_DOCS_DIR, exist_ok=True)

# Repository directories
REPO_DIR = os.path.join(RAW_DOCS_DIR, "reachy2_sdk_repo")
SDK_SOURCE_DIR = os.path.join(REPO_DIR, "src", "reachy2_sdk")
EXAMPLES_SOURCE_DIR = os.path.join(REPO_DIR, "src", "examples")
TUTORIALS_SOURCE_DIR = os.path.join(RAW_DOCS_DIR, "reachy2_tutorials")

# Legacy directories (kept for compatibility)
API_DOCS_DIR = os.path.join(RAW_DOCS_DIR, "api_docs")
EXAMPLES_DIR = os.path.join(RAW_DOCS_DIR, "examples")
TUTORIALS_DIR = os.path.join(RAW_DOCS_DIR, "tutorials")


def clone_or_update_repo():
    """Clone the repository if it doesn't exist, or pull the latest changes."""
    try:
        if not os.path.exists(REPO_DIR):
            print(f"Cloning repository: {GIT_URL} into {REPO_DIR}...")
            subprocess.run(["git", "clone", GIT_URL, REPO_DIR], check=True)
            print("Repository cloned successfully")
        else:
            print("Repository exists. Pulling latest changes...")
            subprocess.run(["git", "-C", REPO_DIR, "pull"], check=True)
            print("Repository updated successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error during git operation: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False


def process_python_file(file_path: str) -> Dict:
    """Process a Python file into a document."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Parse the file to get docstring and other metadata
        tree = ast.parse(content)
        docstring = ast.get_docstring(tree) or ""

        # Get relative path for source tracking
        rel_path = os.path.relpath(file_path, REPO_DIR)

        return {
            "content": content,
            "metadata": {
                "source": rel_path,
                "type": "example",
                "format": "python",
                "collection": "reachy2_sdk",
                "docstring": docstring,
            },
        }
    except Exception as e:
        print(f"Error processing Python file {file_path}: {e}")
        return None


def process_notebook_file(file_path: str) -> Dict:
    """Process a Jupyter notebook into a document."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            nb = nbformat.read(f, as_version=4)

        # Extract markdown and code cells
        content = []
        for cell in nb.cells:
            if cell.cell_type == "markdown":
                content.append(f"# {cell.source}")
            elif cell.cell_type == "code":
                content.append(f"```python\n{cell.source}\n```")

        # Get relative path for source tracking
        rel_path = os.path.relpath(file_path, REPO_DIR)

        # Get notebook title from filename
        title = os.path.splitext(os.path.basename(file_path))[0]

        return {
            "content": "\n\n".join(content),
            "metadata": {
                "source": rel_path,
                "type": "example",
                "format": "notebook",
                "collection": "reachy2_sdk",
                "title": title,
            },
        }
    except Exception as e:
        print(f"Error processing notebook {file_path}: {e}")
        return None


def collect_sdk_examples() -> List[Dict]:
    """Collect examples from the SDK repository."""
    print("\nCollecting SDK examples...")
    examples = []

    if not os.path.exists(EXAMPLES_SOURCE_DIR):
        print(f"Warning: Examples directory not found at {EXAMPLES_SOURCE_DIR}")
        return examples

    # Walk through the examples directory
    for root, _, files in os.walk(EXAMPLES_SOURCE_DIR):
        for file in sorted(files):  # Sort files to process in a consistent order
            if not (file.endswith(".py") or file.endswith(".ipynb")):
                continue

            file_path = os.path.join(root, file)
            print(f"Processing: {file}")

            if file.endswith(".py"):
                doc = process_python_file(file_path)
                if doc:
                    examples.append(doc)
                    print(f"Added Python example: {file}")

            elif file.endswith(".ipynb"):
                doc = process_notebook_file(file_path)
                if doc:
                    examples.append(doc)
                    print(f"Added notebook example: {file}")

    print(f"Collected {len(examples)} examples")
    return examples


def save_sdk_examples(examples: List[Dict]):
    """Save SDK examples to the appropriate JSON file."""
    if not examples:
        print("No examples to save")
        return

    output_file = os.path.join(EXTRACTED_DIR, "raw_sdk_examples.json")
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(examples, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(examples)} examples to {output_file}")
    except Exception as e:
        print(f"Error saving examples to {output_file}: {e}")


def extract_sdk_documentation() -> List[Dict]:
    """Extract API documentation directly from SDK Python source files."""
    print("\nExtracting SDK API documentation...")
    documented_items = []

    def process_function_def(
        node: ast.FunctionDef, module_name: str, parent_class: str = None
    ) -> Dict:
        """Process a function definition node."""
        # Include more functions, but still skip private ones (single underscore)
        # Include special methods (double underscore) and property methods
        if (
            not node.name.startswith("_")
            or node.name.startswith("__")
            or any(
                isinstance(d, ast.Name) and d.id == "property"
                for d in node.decorator_list
            )
        ):

            func_source = source[node.lineno - 1 : node.end_lineno]
            return {
                "type": "function" if not parent_class else "method",
                "name": node.name,
                "module": f"reachy2_sdk.{module_name}",
                "class": parent_class,  # Will be None for standalone functions
                "signature": get_function_signature(node),
                "docstring": inspect.cleandoc(ast.get_docstring(node) or ""),
                "source_code": func_source,
                "return_type": get_return_annotation(node),
                "parameters": get_parameters(node),
                "source": f"reachy2_sdk.{module_name}.{parent_class + '.' if parent_class else ''}{node.name}",
                "decorators": [
                    d.id if isinstance(d, ast.Name) else d.func.id
                    for d in node.decorator_list
                    if isinstance(d, (ast.Name, ast.Call))
                ],
            }
        return None

    def process_class_def(node: ast.ClassDef, module_name: str) -> Dict:
        """Process a class definition node."""
        class_doc = {
            "type": "class",
            "name": node.name,
            "module": f"reachy2_sdk.{module_name}",
            "docstring": inspect.cleandoc(ast.get_docstring(node) or ""),
            "methods": [],
            "source": f"reachy2_sdk.{module_name}.{node.name}",
            "bases": [
                base.id if isinstance(base, ast.Name) else base.value.id
                for base in node.bases
                if isinstance(base, (ast.Name, ast.Attribute))
            ],
        }

        # Process all nodes in the class body
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_doc = process_function_def(item, module_name, node.name)
                if method_doc:
                    class_doc["methods"].append(method_doc)
            elif isinstance(item, ast.AsyncFunctionDef):
                # Handle async methods too
                method_doc = process_function_def(item, module_name, node.name)
                if method_doc:
                    method_doc["is_async"] = True
                    class_doc["methods"].append(method_doc)

        return class_doc

    # Walk through the SDK source directory
    for root, _, files in os.walk(SDK_SOURCE_DIR):
        for file in files:
            if not file.endswith(".py"):
                continue

            file_path = os.path.join(root, file)
            module_name = (
                os.path.relpath(file_path, SDK_SOURCE_DIR)
                .replace("/", ".")
                .replace(".py", "")
            )

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    source = f.read()

                # Try to parse the source code
                try:
                    tree = ast.parse(source)

                    # Extract module docstring if present
                    module_doc = ast.get_docstring(tree)
                    if module_doc:
                        documented_items.append(
                            {
                                "type": "module",
                                "name": f"reachy2_sdk.{module_name}",
                                "docstring": inspect.cleandoc(module_doc),
                                "source": module_name,
                            }
                        )

                    # Process top-level nodes
                    for node in tree.body:
                        if isinstance(node, ast.ClassDef):
                            class_doc = process_class_def(node, module_name)
                            documented_items.append(class_doc)

                        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            func_doc = process_function_def(node, module_name)
                            if func_doc:
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


def save_sdk_documentation(sdk_docs: List[Dict], examples: List[Dict]):
    """Save SDK documentation and examples to appropriate files."""
    print("\nSaving documentation...")

    # Save SDK API documentation
    api_docs_path = os.path.join(EXTRACTED_DIR, "raw_api_docs.json")
    with open(api_docs_path, "w", encoding="utf-8") as f:
        json.dump(sdk_docs, f, indent=2)
    print(f"Saved {len(sdk_docs)} SDK API documentation items to {api_docs_path}")

    # Save examples
    examples_path = os.path.join(EXTRACTED_DIR, "raw_sdk_examples.json")
    with open(examples_path, "w", encoding="utf-8") as f:
        json.dump(examples, f, indent=2)
    print(f"Saved {len(examples)} examples to {examples_path}")


def main():
    """Main function to scrape SDK documentation and examples."""
    print("Starting SDK documentation scraping...")

    # Step 1: Clone/update the repository
    if not clone_or_update_repo():
        print("Failed to clone/update repository. Aborting.")
        return

    # Step 2: Extract SDK API documentation
    sdk_docs = extract_sdk_documentation()
    print(f"Extracted documentation for {len(sdk_docs)} items")

    # Step 3: Collect SDK examples
    examples = collect_sdk_examples()
    print(f"Collected {len(examples)} examples")

    # Step 4: Save documentation and examples
    save_sdk_documentation(sdk_docs, examples)

    print("\nSDK documentation scraping complete!")


if __name__ == "__main__":
    main()
