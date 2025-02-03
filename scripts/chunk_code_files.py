#!/usr/bin/env python
import os
import argparse
from langchain.text_splitter import RecursiveCharacterTextSplitter


def split_file(filepath, chunk_size, chunk_overlap):
    """
    Reads a file and splits it into chunks using LangChain's RecursiveCharacterTextSplitter.
    Returns both the original text and the list of chunks.
    """
    with open(filepath, "r") as f:
        text = f.read()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = text_splitter.split_text(text)
    return text, chunks


def save_chunks(chunks, dest_dir, filename):
    """
    Saves each chunk to a separate file in dest_dir with a modified filename.
    """
    base, ext = os.path.splitext(filename)
    for i, chunk in enumerate(chunks):
        chunk_filename = f"{base}_chunk{i+1}{ext}"
        dest_path = os.path.join(dest_dir, chunk_filename)
        with open(dest_path, "w") as f:
            f.write(chunk)
        print(f"Saved chunk: {dest_path}")


def calculate_metrics(original_text, chunks, chunk_overlap):
    """
    Calculates and returns metrics:
      - original_length: number of characters in the original text
      - original_token_count: approximate token count based on whitespace splitting
      - number_of_chunks: number of chunks produced
      - total_chunk_tokens: total token count across all chunks
      - average_tokens_per_chunk: average token count per chunk
      - coverage_percentage: percentage of the original text covered by unique content
         (assuming the first chunk is fully unique and each subsequent chunk adds (len(chunk)-chunk_overlap) characters)
    """
    original_length = len(original_text)
    effective_unique_chars = len(chunks[0]) if chunks else 0
    for chunk in chunks[1:]:
        effective_unique_chars += max(0, len(chunk) - chunk_overlap)
    coverage_percentage = (effective_unique_chars / original_length * 100) if original_length > 0 else 0
    
    original_tokens = original_text.split()
    original_token_count = len(original_tokens)
    
    chunk_token_counts = [len(chunk.split()) for chunk in chunks]
    total_chunk_tokens = sum(chunk_token_counts)
    average_tokens_per_chunk = total_chunk_tokens / len(chunks) if chunks else 0
    
    metrics = {
        "original_length_chars": original_length,
        "original_token_count": original_token_count,
        "number_of_chunks": len(chunks),
        "total_chunk_tokens": total_chunk_tokens,
        "average_tokens_per_chunk": average_tokens_per_chunk,
        "coverage_percentage": coverage_percentage,
        "chunk_token_counts": chunk_token_counts
    }
    return metrics


def main():
    parser = argparse.ArgumentParser(description="Chunk code files from the Codebase directory using LangChain text splitting and report metrics.")
    parser.add_argument("--source", type=str, default=os.path.join("external_docs", "Codebase"),
                        help="Source directory containing code files to chunk.")
    parser.add_argument("--dest", type=str, default=os.path.join("external_docs", "Codebase_chunks"),
                        help="Destination directory to store the chunked files.")
    parser.add_argument("--chunk_size", type=int, default=1500,
                        help="Maximum size (in characters) of each chunk.")
    parser.add_argument("--chunk_overlap", type=int, default=300,
                        help="Number of overlapping characters between chunks.")
    parser.add_argument("--extensions", nargs="*", default=[".py", ".ipynb"],
                        help="List of file extensions to process.")
    args = parser.parse_args()

    for root, dirs, files in os.walk(args.source):
        for file in files:
            if any(file.endswith(ext) for ext in args.extensions):
                file_path = os.path.join(root, file)
                # Compute the relative directory structure to preserve it in the destination
                rel_dir = os.path.relpath(root, args.source)
                dest_dir = os.path.join(args.dest, rel_dir)
                os.makedirs(dest_dir, exist_ok=True)
                print(f"Processing file: {file_path}")
                original_text, chunks = split_file(file_path, args.chunk_size, args.chunk_overlap)
                save_chunks(chunks, dest_dir, file)
                
                # Calculate and print metrics
                metrics = calculate_metrics(original_text, chunks, args.chunk_overlap)
                print(f"Metrics for {file_path}:")
                print(f"  Original length: {metrics['original_length_chars']} characters")
                print(f"  Original token count (approx): {metrics['original_token_count']} tokens")
                print(f"  Number of chunks: {metrics['number_of_chunks']}")
                print(f"  Total tokens in chunks (approx): {metrics['total_chunk_tokens']}")
                print(f"  Average tokens per chunk (approx): {metrics['average_tokens_per_chunk']:.2f}")
                print(f"  Coverage percentage (based on characters): {metrics['coverage_percentage']:.2f}%")
                print("------")


if __name__ == "__main__":
    main() 