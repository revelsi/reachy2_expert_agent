#!/usr/bin/env python

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.db_utils import VectorStore
from utils.embedding_utils import EmbeddingGenerator

def print_results(results, collection_name):
    print(f"\nResults from {collection_name}:")
    print("-" * 80)
    
    documents = results['documents'][0]
    distances = results['distances'][0]
    
    for doc, dist in zip(documents, distances):
        print(f"\nDocument (distance: {dist:.3f}):")
        print(f"Content: {doc[:200]}..." if len(doc) > 200 else f"Content: {doc}")
    print("-" * 80)

def main():
    # Initialize vector store and embedding generator with RoBERTa model
    db = VectorStore()
    embedding_generator = EmbeddingGenerator(model_name="all-roberta-large-v1")
    
    print(f"Using model: {embedding_generator.model_name}\n")
    
    # Test queries
    test_queries = [
        "How do I control the robot's head?",
        "What sensors does Reachy have?",
        "How can I make Reachy pick up an object?"
    ]
    
    collections = ["reachy2-tutorials", "reachy2-sdk", "api_docs"]
    
    for query in test_queries:
        print(f"Query: {query}")
        print("=" * 80)
        
        for collection in collections:
            results = db.query_collection(
                collection_name=collection,
                query_texts=[query],
                n_results=3,
                embedding_function=embedding_generator.embedding_function
            )
            print_results(results, collection)
        print("\n")

if __name__ == "__main__":
    main() 