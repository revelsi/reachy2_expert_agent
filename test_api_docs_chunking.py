import os
from bs4 import BeautifulSoup
from scripts.chunk_documents import chunk_api_docs_classes, split_text

def print_chunk(chunk: str, chunk_type: str):
    """Helper function to print chunks with consistent formatting."""
    print(f"\n{chunk_type} Chunk (size: {len(chunk)}):")
    print("-" * 80)
    print(chunk)
    print("-" * 80)

def chunk_api_docs_functions(file_path: str, max_chunk_size=1500, overlap=300):
    """Extract function-level documentation chunks from API docs HTML file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    
    chunks = []
    
    # Find all function definitions in code blocks
    for span in soup.find_all('span', class_='k'):
        if span.text == 'def':
            # Get the function definition line
            func_def = span.find_parent('span', id=lambda x: x and x.startswith('L-'))
            if not func_def:
                continue
                
            # Get the docstring and implementation
            current_line = func_def
            func_content = []
            while current_line and len(func_content) < 50:  # Limit to avoid infinite loops
                if current_line.name == 'span' and current_line.get('id', '').startswith('L-'):
                    text = ''.join(t.text for t in current_line.find_all('span', recursive=False))
                    func_content.append(text)
                current_line = current_line.find_next_sibling()
                
                # Stop if we hit another function definition
                if current_line and current_line.find('span', class_='k', text='def'):
                    break
            
            if func_content:
                chunk = '\n'.join(func_content)
                if len(chunk) > max_chunk_size:
                    sub_chunks = split_text(chunk, max_chunk_size, overlap)
                    chunks.extend(sub_chunks)
                else:
                    chunks.append(chunk)
    
    return chunks

def process_file(file_path: str):
    """Process a single HTML file and print its chunks."""
    print(f"\nProcessing {os.path.basename(file_path)}:")
    print("=" * 80)
    
    # Get class-level chunks
    class_chunks = chunk_api_docs_classes(file_path)
    for chunk in class_chunks:
        print_chunk(chunk, "Class")
    
    # Get function-level chunks
    function_chunks = chunk_api_docs_functions(file_path)
    for chunk in function_chunks:
        print_chunk(chunk, "Function")

def main():
    docs_dir = "raw_docs/api_docs"
    html_files = [f for f in os.listdir(docs_dir) if f.endswith('.html')]
    
    for html_file in sorted(html_files):
        file_path = os.path.join(docs_dir, html_file)
        process_file(file_path)

if __name__ == "__main__":
    main() 