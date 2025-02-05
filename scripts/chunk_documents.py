import os
import sys
import nbformat
import re
from bs4 import BeautifulSoup
from langchain.docstore.document import Document

# Import save_documents_to_json from utils.doc_utils if available
try:
    from utils.doc_utils import save_documents_to_json
except ImportError:
    def save_documents_to_json(docs, filepath):
        import json
        # Simple json dump assuming docs are serializable
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump([{'page_content': doc.page_content, 'metadata': doc.metadata} for doc in docs], f, indent=2)


def split_text(text, max_chunk=1500, overlap=300):
    """Splits text into chunks of max_chunk size with an overlap."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + max_chunk
        chunk = text[start:end]
        chunks.append(chunk)
        if end >= len(text):
            break
        start = end - overlap
    return chunks


def chunk_html_file(file_path):
    """Chunking strategy for HTML API docs.
    Extracts the main content from the HTML and splits into chunks."""
    with open(file_path, 'r', encoding='utf-8') as f:
        html = f.read()
    soup = BeautifulSoup(html, 'html.parser')
    main_tag = soup.find('main')
    if main_tag:
        text = main_tag.get_text(separator='\n').strip()
    else:
        text = soup.get_text(separator='\n').strip()
    return split_text(text)


def chunk_tutorial_notebook(file_path, max_chunk_size=1500, overlap=300):
    """Chunking strategy for notebooks from the tutorials source.
    Each chunk consists of a markdown cell paired with its following code cell (if exists)
    to preserve the tutorial's explanation-demonstration flow.
    
    Args:
        file_path: Path to the notebook file
        max_chunk_size: Maximum size of each chunk (default: 1500)
        overlap: Number of characters to overlap between chunks (default: 300)
    """
    try:
        nb = nbformat.read(file_path, as_version=4)
    except Exception as e:
        print(f"Error reading notebook {file_path}: {e}")
        return []

    chunks = []
    i = 0
    while i < len(nb.cells):
        current_cell = nb.cells[i]
        
        # If we find a markdown cell
        if current_cell.cell_type == 'markdown':
            markdown_content = current_cell.source.strip()
            
            # Look ahead for the next cell
            next_cell = nb.cells[i + 1] if i + 1 < len(nb.cells) else None
            
            # If next cell is code, combine them
            if next_cell and next_cell.cell_type == 'code':
                code_content = next_cell.source.strip()
                combined_content = f"### Tutorial Explanation:\n{markdown_content}\n\n### Code Example:\n```python\n{code_content}\n```"
                chunks.append(combined_content)
                i += 2  # Skip both cells
            else:
                # If no following code cell, just use the markdown
                if markdown_content:
                    chunks.append(f"### Tutorial Explanation:\n{markdown_content}")
                i += 1
        else:
            # If it's a standalone code cell, include it with a header
            if current_cell.cell_type == 'code' and current_cell.source.strip():
                code_content = current_cell.source.strip()
                chunks.append(f"### Code Example:\n```python\n{code_content}\n```")
            i += 1

    # Process chunks that exceed max_chunk_size while maintaining overlap
    final_chunks = []
    for chunk in chunks:
        if len(chunk) > max_chunk_size:
            # Try to split at the "### Code Example:" marker if present
            parts = chunk.split("### Code Example:", 1)
            if len(parts) > 1:
                markdown_part = parts[0].strip()
                code_part = "### Code Example:" + parts[1].strip()
                
                # Handle markdown part
                if len(markdown_part) > max_chunk_size:
                    markdown_chunks = split_text(markdown_part, max_chunk=max_chunk_size, overlap=overlap)
                    # Ensure each chunk maintains the tutorial explanation header
                    markdown_chunks = [
                        chunk if chunk.startswith("### Tutorial") else f"### Tutorial Explanation:\n{chunk}"
                        for chunk in markdown_chunks
                    ]
                    final_chunks.extend(markdown_chunks)
                else:
                    final_chunks.append(markdown_part)
                
                # Handle code part
                if len(code_part) > max_chunk_size:
                    # For code, we try to split at newlines to preserve code structure
                    code_lines = code_part.split('\n')
                    current_chunk = []
                    current_size = 0
                    
                    for line in code_lines:
                        line_size = len(line) + 1  # +1 for newline
                        if current_size + line_size > max_chunk_size and current_chunk:
                            # Join current chunk and add to final chunks
                            final_chunks.append('\n'.join(current_chunk))
                            # Start new chunk with overlap from previous chunk
                            overlap_lines = current_chunk[-3:]  # Take last 3 lines for context
                            current_chunk = overlap_lines + [line]
                            current_size = sum(len(l) + 1 for l in current_chunk)
                        else:
                            current_chunk.append(line)
                            current_size += line_size
                    
                    if current_chunk:
                        final_chunks.append('\n'.join(current_chunk))
                else:
                    final_chunks.append(code_part)
            else:
                # If no code marker, use standard text splitting with overlap
                final_chunks.extend(split_text(chunk, max_chunk=max_chunk_size, overlap=overlap))
        else:
            final_chunks.append(chunk)

    return final_chunks


def chunk_reachy2sdk_file(file_path):
    """Chunking strategy for Reachy2 SDK raw files.
    For .py files, perform simple splitting based on double newlines; for notebooks, handle code and markdown separately."""
    if file_path.endswith('.py'):
        with open(file_path, 'r', encoding='utf-8') as f:
            code_text = f.read()
        return chunk_python_code(code_text)
    elif file_path.endswith('.ipynb'):
        try:
            nb = nbformat.read(file_path, as_version=4)
        except Exception as e:
            print(f"Error reading notebook {file_path}: {e}")
            return []
        chunks = []
        # For SDK notebooks, process code cells with a code-specific strategy and markdown cells with general splitting
        for cell in nb.cells:
            if cell.cell_type == 'code':
                code = cell.source.strip()
                if code:
                    chunks.extend(chunk_python_code(code))
            elif cell.cell_type == 'markdown':
                text = cell.source.strip()
                if text:
                    chunks.extend(split_text(text))
        return chunks
    else:
        return []


def chunk_python_code(code_text):
    """Simple chunking for Python code by splitting on double newlines and further splitting if needed."""
    parts = code_text.split('\n\n')
    chunks = []
    for part in parts:
        part = part.strip()
        if part:
            if len(part) > 1500:
                chunks.extend(split_text(part))
            else:
                chunks.append(part)
    return chunks


def process_raw_files(source_folder, output_json_path, chunking_function):
    """Process raw files in source_folder using the provided chunking_function.
    Convert each raw file into multiple Document objects with metadata.
    Save all documents to output_json_path as JSON."""
    documents = []
    for file in os.listdir(source_folder):
        file_path = os.path.join(source_folder, file)
        chunks = chunking_function(file_path)
        for i, chunk in enumerate(chunks):
            doc = Document(page_content=chunk, metadata={"source_file": file_path, "chunk_index": i})
            documents.append(doc)
    save_documents_to_json(documents, output_json_path)
    print(f"Saved {len(documents)} documents to {output_json_path}")


def chunk_api_docs_classes(file_path, max_chunk_size=2000):
    """Chunking strategy for API docs at the class level.
    This function removes code blocks (div.pdoc-code.codehilite) and extracts each class section as a chunk.

    Args:
        file_path: Path to the HTML file
        max_chunk_size: Maximum size of each chunk (default: 2000 characters)
    Returns:
        List of text chunks, each representing a class section with its summary and methods.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        html = f.read()
    soup = BeautifulSoup(html, 'html.parser')

    # Remove code blocks
    for code_div in soup.find_all('div', class_='pdoc-code codehilite'):
        code_div.decompose()

    main_tag = soup.find('main')
    if not main_tag:
        main_tag = soup.body

    # Try to find class sections; pdoc usually wraps classes in a <section> with class 'pdoc-class'
    class_sections = main_tag.find_all('section', class_='pdoc-class')
    chunks = []
    if class_sections:
        for sec in class_sections:
            text = sec.get_text(separator='\n').strip()
            if text:
                if len(text) > max_chunk_size:
                    chunks.extend(split_text(text, max_chunk=max_chunk_size))
                else:
                    chunks.append(text)
    else:
        # Fallback: if specific sections are not defined, use entire main content
        text = main_tag.get_text(separator='\n').strip()
        chunks = split_text(text, max_chunk=max_chunk_size)
    return chunks


def chunk_api_docs_functions(file_path, max_chunk_size=1500, overlap=300):
    """Chunking strategy for API docs at the function level.
    This function identifies function definitions in pdoc-generated HTML documentation.
    It looks for div elements with class 'attr function' and extracts the function name and docstring.

    Args:
        file_path: Path to the HTML file.
        max_chunk_size: Maximum size of each chunk (default: 1500).
        overlap: Overlap between chunks if splitting is required.

    Returns:
        List of text chunks, each containing the extracted function name and docstring.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        html = f.read()
    soup = BeautifulSoup(html, 'html.parser')

    # Find all function definitions (they have class 'attr function')
    function_divs = soup.find_all('div', class_='attr function')
    chunks = []
    
    for div in function_divs:
        # Get the function name from the div's text content
        function_name = div.get_text().strip()
        
        # Find the associated docstring div (it's the next div with class 'docstring')
        docstring_div = div.find_next('div', class_='docstring')
        docstring = docstring_div.get_text().strip() if docstring_div else ""
        
        # Combine the extracted information
        function_chunk = f"Function: {function_name}\nDocstring:\n{docstring}"
        
        # Split the chunk if it's too large
        if len(function_chunk) > max_chunk_size:
            splitted = split_text(function_chunk, max_chunk=max_chunk_size, overlap=overlap)
            chunks.extend(splitted)
        else:
            chunks.append(function_chunk)
    
    return chunks


def process_api_docs(source_folder, output_api_classes, output_api_functions):
    """Process all API docs HTML files in source_folder using the new chunking strategies.
    Saves two JSON files: one for class-level chunks and one for function-level chunks.
    """
    from langchain.docstore.document import Document
    documents_classes = []
    documents_functions = []
    for file in os.listdir(source_folder):
        if file.endswith('.html'):
            file_path = os.path.join(source_folder, file)
            class_chunks = chunk_api_docs_classes(file_path)
            for i, chunk in enumerate(class_chunks):
                doc = Document(page_content=chunk, metadata={"source_file": file_path, "chunk_index": i, "type": "class"})
                documents_classes.append(doc)
            function_chunks = chunk_api_docs_functions(file_path)
            for i, chunk in enumerate(function_chunks):
                doc = Document(page_content=chunk, metadata={"source_file": file_path, "chunk_index": i, "type": "function"})
                documents_functions.append(doc)
    save_documents_to_json(documents_classes, output_api_classes)
    save_documents_to_json(documents_functions, output_api_functions)
    print(f"Saved {len(documents_classes)} class documents to {output_api_classes}")
    print(f"Saved {len(documents_functions)} function documents to {output_api_functions}")


def main():
    base_output_dir = os.path.join("external_docs", "documents")
    os.makedirs(base_output_dir, exist_ok=True)

    # Process API docs (HTML files) using new two-stage chunking strategy
    api_docs_folder = os.path.join("raw_docs", "api_docs")
    output_api_classes = os.path.join(base_output_dir, "api_docs_classes.json")
    output_api_functions = os.path.join(base_output_dir, "api_docs_functions.json")
    process_api_docs(api_docs_folder, output_api_classes, output_api_functions)

    # Process tutorials notebooks
    tutorials_folder = os.path.join("raw_docs", "reachy2_tutorials")
    output_tutorials_path = os.path.join(base_output_dir, "reachy2_tutorials.json")
    process_raw_files(tutorials_folder, output_tutorials_path, chunk_tutorial_notebook)

    # Process Reachy2 SDK files
    sdk_folder = os.path.join("raw_docs", "reachy2_sdk")
    output_sdk_path = os.path.join(base_output_dir, "reachy2_sdk.json")
    process_raw_files(sdk_folder, output_sdk_path, chunk_reachy2sdk_file)


if __name__ == "__main__":
    main() 