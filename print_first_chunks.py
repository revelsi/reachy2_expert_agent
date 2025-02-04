from doc_utils import load_documents_from_json
import os

def print_first_chunks(filename):
    print(f"\n{'='*50}")
    print(f"First three chunks from {filename}:")
    print(f"{'='*50}")
    
    filepath = os.path.join("external_docs", "Codebase", filename)
    try:
        docs = load_documents_from_json(filepath)
        if docs:
            for i in range(min(3, len(docs))):
                print(f"\nChunk {i+1}:")
                print(f"Content: {docs[i].page_content[:500]}...")  # Print first 500 chars
                print(f"Metadata: {docs[i].metadata}")
                print("-" * 30)
        else:
            print("No documents found in file")
    except Exception as e:
        print(f"Error reading file: {e}")

def main():
    files = [
        "api_docs.json",
        "reachy2-tutorials.json",
        "reachy2-sdk.json",
        "pollen-vision.json"
    ]
    
    for filename in files:
        print_first_chunks(filename)

if __name__ == "__main__":
    main() 