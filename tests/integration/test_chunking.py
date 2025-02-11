import os
import sys
import pytest

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tools.chunk_documents import clean_text, split_text


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


def test_clean_text():
    """Test text cleaning functionality."""
    test_cases = [
        ("Hello\nWorld", "Hello World"),
        ("Multiple    spaces", "Multiple spaces"),
        ("Line\nbreaks\nhere", "Line breaks here"),
    ]
    
    for input_text, expected in test_cases:
        assert clean_text(input_text) == expected

def test_split_text():
    """Test text splitting functionality."""
    text = "This is a test sentence. Here is another one. And a third."
    chunks = split_text(text, max_chunk_size=20)
    
    assert len(chunks) > 0
    assert all(len(chunk) <= 20 for chunk in chunks)


if __name__ == "__main__":
    pytest.main([__file__])
