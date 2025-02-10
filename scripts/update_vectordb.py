#!/usr/bin/env python

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.doc_utils import load_documents_from_json
from utils.embedding_utils import EmbeddingGenerator, prepare_documents_for_db, EmbeddingFunction
from utils.db_utils import VectorStore
import argparse
import functools
import inspect

def process_json_file(filepath: str, db: VectorStore, embedding_generator: EmbeddingGenerator) -> bool:
    """Process a JSON file and add its documents to the vector store.
    Returns True if successful, False otherwise."""
    try:
        # Extract collection name from filepath
        collection_name = os.path.splitext(os.path.basename(filepath))[0]
        print(f"\nProcessing collection: {collection_name}")
        
        # Load documents
        try:
            documents = load_documents_from_json(filepath)
            if not documents:
                print(f"No documents found in {filepath}")
                return False
            print(f"Loaded {len(documents)} documents")
        except Exception as e:
            print(f"Error loading documents from {filepath}: {str(e)}")
            return False
        
        # Prepare documents for database
        try:
            texts, metadatas, ids = prepare_documents_for_db(documents)
            print(f"Prepared {len(texts)} documents for embedding")
        except Exception as e:
            print(f"Error preparing documents: {str(e)}")
            return False
        
        # Add to vector store
        try:
            print(f"Adding documents to collection '{collection_name}'...")
            class LoggingEmbeddingFunction(EmbeddingFunction):
                def __init__(self, embed_func):
                    self.embed_func = embed_func
                def __call__(self, input):
                    result = self.embed_func(input)
                    print(f"Generated embeddings for {len(input)} texts in batch.")
                    return result
            
            db.add_documents(
                collection_name=collection_name,
                texts=texts,
                metadatas=metadatas,
                ids=ids,
                embedding_function=embedding_generator
            )
            
            # Verify collection was created and populated
            collection = db.client.get_collection(name=collection_name)
            count = collection.count()
            if count != len(texts):
                print(f"Warning: Expected {len(texts)} documents but found {count} in collection")
            else:
                print(f"Successfully added {count} documents to collection '{collection_name}'")
            return True
            
        except Exception as e:
            print(f"Error adding documents to collection: {str(e)}")
            return False
            
    except Exception as e:
        print(f"Error processing {filepath}: {str(e)}")
        return False

def main():
    """Update the vector database with documents from JSON files."""
    parser = argparse.ArgumentParser(description="Update vector database with document embeddings")
    parser.add_argument("--test", action="store_true", help="Use lighter model for testing")
    args = parser.parse_args()
    
    try:
        # Initialize vector store and embedding generator
        print("\nInitializing vector store...")
        db = VectorStore(persist_directory="vectorstore")
        
        # Initialize embedding generator
        if args.test:
            model_name = "sentence-transformers/all-MiniLM-L6-v2"
            print(f"\nUsing lightweight model for testing: {model_name}")
        else:
            model_name = "hkunlp/instructor-xl"
            print(f"\nUsing InstructorXL model for production embeddings")
        
        embedding_generator = EmbeddingGenerator(model_name=model_name)
        
        # Clean up existing vectorstore
        print("\nCleaning up existing vector store...")
        db.cleanup()
        
        # Define collection processing order (most important first)
        collections = [
            "external_docs/documents/api_docs_functions.json",  # API functions (primary reference)
            "external_docs/documents/api_docs_classes.json",    # API classes
            "external_docs/documents/api_docs_modules.json",    # Module documentation
            "external_docs/documents/reachy2_sdk.json",        # SDK implementation
            "external_docs/documents/reachy2_docs.json",       # Reachy 2 official documentation
            "external_docs/documents/reachy2_tutorials.json",   # Usage examples
            "external_docs/documents/vision_examples.json"      # Vision examples
        ]
        
        # Track processing status
        processed = 0
        failed = 0
        
        # Process each collection
        for filepath in collections:
            if os.path.exists(filepath):
                if process_json_file(filepath, db, embedding_generator):
                    processed += 1
                else:
                    failed += 1
            else:
                print(f"\nWarning: Collection file not found: {filepath}")
                failed += 1
        
        # Save the database
        if processed > 0:
            print("\nSaving vector store...")
            db.save()
            print(f"\nVector store update complete! Successfully processed {processed} collections, {failed} failed.")
        else:
            print("\nError: No collections were successfully processed!")
            sys.exit(1)
        
    except Exception as e:
        print(f"\nError updating vector store: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 