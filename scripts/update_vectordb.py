#!/usr/bin/env python
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.doc_utils import load_documents_from_json
from utils.embedding_utils import EmbeddingGenerator, prepare_documents_for_db
from utils.db_utils import VectorStore
import os

def process_json_file(filepath: str, db: VectorStore, embedding_generator: EmbeddingGenerator):
    """Process a single JSON file and add its documents to the vector store."""
    print(f"Processing {filepath}...")
    
    # Load documents
    documents = load_documents_from_json(filepath)
    if not documents:
        print(f"No documents found in {filepath}")
        return
    
    # Get collection name from filename
    collection_name = os.path.splitext(os.path.basename(filepath))[0].replace("-", "_")
    
    # Prepare documents for database
    texts, metadatas, ids = prepare_documents_for_db(documents)
    
    # Generate embeddings
    print(f"Generating embeddings for {len(texts)} documents...")
    embeddings = embedding_generator.generate_embeddings(texts)
    
    # Add to database
    print(f"Adding documents to collection '{collection_name}'...")
    db.add_documents(
        collection_name=collection_name,
        texts=texts,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )
    print(f"Successfully processed {len(documents)} documents from {filepath}")

def main():
    # Initialize vector store and embedding generator
    db = VectorStore(persist_directory="vectorstore")
    embedding_generator = EmbeddingGenerator()
    
    # Process each JSON file in the Codebase directory
    codebase_dir = os.path.join("external_docs", "Codebase")
    for filename in os.listdir(codebase_dir):
        if filename.endswith('.json'):
            filepath = os.path.join(codebase_dir, filename)
            process_json_file(filepath, db, embedding_generator)
    
    print("\nVector database update complete!")

if __name__ == "__main__":
    main() 