#!/usr/bin/env python
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.db_utils import VectorStore
from utils.embedding_utils import EmbeddingGenerator

def list_collections(db: VectorStore):
    """List all collections and their sizes."""
    print("\n=== Collections in Database ===")
    collection_names = db.client.list_collections()
    for name in collection_names:
        collection = db.client.get_collection(name)
        print(f"\nCollection: {name}")
        print(f"Count: {collection.count()} documents")

def run_test_queries(db: VectorStore, embedding_generator: EmbeddingGenerator):
    """Run some test queries on each collection."""
    print("\n=== Test Queries ===")
    
    # Example queries for different types of information
    test_queries = [
        "How to move Reachy's arm?",
        "What is the camera API?",
        "How to control the gripper?",
        "What are the safety precautions?",
    ]
    
    collection_names = db.client.list_collections()
    for name in collection_names:
        collection = db.client.get_collection(name)
        print(f"\nQuerying collection: {name}")
        print("-" * 50)
        
        for query in test_queries:
            print(f"\nQuery: '{query}'")
            # Generate embedding for the query
            query_embedding = embedding_generator.generate_embeddings([query])[0]
            
            # Get results
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=2,
                include=["documents", "metadatas", "distances"]
            )
            
            # Print results
            for i in range(len(results["documents"][0])):
                print(f"\nMatch {i+1} (distance: {results['distances'][0][i]:.3f}):")
                print(f"Content: {results['documents'][0][i][:200]}...")
                print(f"Metadata: {results['metadatas'][0][i]}")
                print("-" * 30)

def main():
    # Initialize vector store and embedding generator
    db = VectorStore(persist_directory="vectorstore")
    embedding_generator = EmbeddingGenerator()
    
    # List collections and their sizes
    list_collections(db)
    
    # Run test queries
    run_test_queries(db, embedding_generator)

if __name__ == "__main__":
    main() 