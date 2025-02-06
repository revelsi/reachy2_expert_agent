import sys
import os

# Ensure the parent directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.chunk_documents import clean_text, split_text


def main():
    # A sample text with extra whitespace and newlines
    sample_text = """   This is    a   test.
    
    It has   multiple   spaces and 
    
    several newlines.


    We want to see it cleaned and properly chunked.   """

    print("Original Text:")
    print(repr(sample_text))
    print("\n---\n")
    
    cleaned = clean_text(sample_text)
    print("Cleaned Text:")
    print(repr(cleaned))
    print("\n---\n")
    
    # Using a small chunk size to see multiple chunks
    chunks = split_text(sample_text, max_chunk=50, overlap=10)
    print("Chunks:")
    for i, chunk in enumerate(chunks):
        print(f"Chunk {i+1}:")
        print(repr(chunk))
        print("------")


if __name__ == '__main__':
    main() 