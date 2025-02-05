#!/usr/bin/env python

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.doc_utils import load_documents_from_json
from utils.embedding_utils import EmbeddingGenerator, prepare_documents_for_db
from utils.db_utils import VectorStore

def process_json_file(filepath: str, db: VectorStore, embedding_generator: EmbeddingGenerator):
    """Process a JSON file and add its documents to the vector store."""
    # Extract collection name from filepath
    collection_name = os.path.splitext(os.path.basename(filepath))[0]
    
    # Load documents
    documents = load_documents_from_json(filepath)
    if not documents:
        print(f"No documents found in {filepath}")
        return
    
    # Prepare documents for database
    texts, metadatas, ids = prepare_documents_for_db(documents)
    
    # Add to vector store
    print(f"Adding documents to collection '{collection_name}'...")
    db.add_documents(
        collection_name=collection_name,
        texts=texts,
        metadatas=metadatas,
        ids=ids,
        embedding_function=embedding_generator.embedding_function
    )
    print(f"Successfully processed {len(documents)} documents from {filepath}")

def main():
    """Update the vector database with documents from JSON files."""
    # Initialize vector store and embedding generator
    db = VectorStore(persist_directory="vectorstore")
    embedding_generator = EmbeddingGenerator(model_name="hkunlp/instructor-xl")
    
    print("\nInitializing vector store with RoBERTa embeddings...")
    
    # Clean up existing vectorstore
    db.cleanup()
    
    # Process each JSON file
    for filepath in [
        "external_docs/Codebase/reachy2-tutorials.json",
        "external_docs/Codebase/reachy2-sdk.json",
        "external_docs/Codebase/api_docs.json"
    ]:
        process_json_file(filepath, db, embedding_generator)
    
    # Save the database to the persist directory
    db.save()
    print("\nVector store update complete!")

if __name__ == "__main__":
    main() 