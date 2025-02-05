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


def chunk_tutorial_notebook(file_path):
    """Chunking strategy for notebooks from the tutorials source.
    For tutorials, we focus on markdown cells to preserve narrative flow."""
    try:
        nb = nbformat.read(file_path, as_version=4)
    except Exception as e:
        print(f"Error reading notebook {file_path}: {e}")
        return []
    aggregated = ""
    for cell in nb.cells:
        if cell.cell_type == 'markdown':
            content = cell.source.strip()
            if content:
                aggregated += content + "\n\n"
    if not aggregated:
        return []
    return split_text(aggregated)


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


def main():
    base_output_dir = os.path.join("external_docs", "documents")
    os.makedirs(base_output_dir, exist_ok=True)

    # Process API docs (HTML files)
    api_docs_folder = os.path.join("raw_docs", "api_docs")
    output_api_path = os.path.join(base_output_dir, "api_docs.json")
    process_raw_files(api_docs_folder, output_api_path, chunk_html_file)

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