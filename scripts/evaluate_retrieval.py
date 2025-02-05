#!/usr/bin/env python

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.db_utils import VectorStore
from utils.embedding_utils import EmbeddingGenerator
import argparse
from typing import Dict, List

# Test queries and their relevant document IDs for each collection
TEST_QUERIES = {
    "How to move Reachy's arm?": {
        "reachy2-tutorials": ["Arm movement", "goto", "translate_by", "rotate_by"],
        "reachy2-sdk": ["Move Reachy's right arm", "goto_posture", "rotate_by"],
        "api_docs": ["Get Reachy's right arm", "Get Reachy's left arm"]
    },
    "What is the camera API?": {
        "reachy2-tutorials": ["PollenSDKCameraWrapper", "camera_wrapper"],
        "reachy2-sdk": ["reachy.cameras", "CameraView", "camera_manager"],
        "api_docs": ["CameraManager", "camera_manager"]
    },
    "How to control the gripper?": {
        "reachy2-tutorials": ["gripper.open", "gripper.close"],
        "reachy2-sdk": ["Gripper Control", "open", "close", "set_opening"],
        "api_docs": ["gripper"]
    }
}

def calculate_metrics(results: Dict, relevant_ids: List[str]) -> Dict[str, float]:
    """Calculate retrieval metrics for a single query."""
    retrieved_docs = results['documents'][0]
    k = len(retrieved_docs)
    
    # For simplicity, we'll treat each retrieved document as relevant if it contains
    # any of the relevant document IDs in its content or metadata
    relevant_retrieved = []
    for doc in retrieved_docs:
        is_relevant = any(rel_id.lower() in doc.lower() for rel_id in relevant_ids)
        relevant_retrieved.append(is_relevant)
    
    # Calculate metrics
    num_relevant_retrieved = sum(relevant_retrieved)
    precision_at_k = num_relevant_retrieved / k if k > 0 else 0
    recall_at_k = num_relevant_retrieved / len(relevant_ids) if relevant_ids else 0
    
    # Calculate MRR
    mrr = 0
    for i, is_relevant in enumerate(relevant_retrieved):
        if is_relevant:
            mrr = 1 / (i + 1)
            break
    
    # Calculate nDCG@k
    dcg = sum(rel / log2(i + 2) for i, rel in enumerate(relevant_retrieved))
    idcg = sum(1 / log2(i + 2) for i in range(min(len(relevant_ids), k)))
    ndcg = dcg / idcg if idcg > 0 else 0
    
    return {
        "precision": precision_at_k,
        "recall": recall_at_k,
        "mrr": mrr,
        "ndcg": ndcg
    }

def evaluate_retrieval(db: VectorStore, embedding_generator: EmbeddingGenerator):
    """Evaluate retrieval performance across all test queries."""
    collections = ["reachy2-tutorials", "reachy2-sdk", "api_docs"]
    collection_metrics = {col: {"precision": [], "recall": [], "mrr": [], "ndcg": []} for col in collections}
    
    for query, relevant_docs in TEST_QUERIES.items():
        print(f"\nQuery: {query}")
        print("=" * 80)
        
        for collection in collections:
            results = db.query_collection(
                collection_name=collection,
                query_texts=[query],
                n_results=5,
                embedding_function=embedding_generator.embedding_function
            )
            
            # Calculate metrics
            metrics = calculate_metrics(results, relevant_docs.get(collection, []))
            
            # Store metrics
            for metric_name, value in metrics.items():
                collection_metrics[collection][metric_name].append(value)
            
            # Print results
            print(f"\nResults from {collection}:")
            print("-" * 80)
            documents = results['documents'][0]
            distances = results['distances'][0]
            for doc, dist in zip(documents, distances):
                print(f"\nDocument (distance: {dist:.3f}):")
                print(f"Content: {doc[:200]}..." if len(doc) > 200 else f"Content: {doc}")
            print(f"\nMetrics - P@5: {metrics['precision']:.3f}, R@5: {metrics['recall']:.3f}, "
                  f"MRR: {metrics['mrr']:.3f}, nDCG@5: {metrics['ndcg']:.3f}")
    
    # Print average metrics
    print("\nAverage Metrics by Collection:")
    print("-" * 80)
    print(f"{'Collection':<20} {'Precision@5':<12} {'Recall@5':<12} {'MRR':<12} {'nDCG@5':<12}")
    print("-" * 80)
    for collection in collections:
        metrics = collection_metrics[collection]
        avg_metrics = {
            name: sum(values) / len(values) if values else 0 
            for name, values in metrics.items()
        }
        print(f"{collection:<20} {avg_metrics['precision']:<12.3f} "
              f"{avg_metrics['recall']:<12.3f} {avg_metrics['mrr']:<12.3f} "
              f"{avg_metrics['ndcg']:<12.3f}")

def main():
    """Main function to run the evaluation."""
    parser = argparse.ArgumentParser(description="Evaluate retrieval performance")
    parser.add_argument("--debug", action="store_true", help="Print debug information")
    args = parser.parse_args()
    
    # Initialize with InstructorXL model
    db = VectorStore()
    embedding_generator = EmbeddingGenerator(model_name="hkunlp/instructor-xl")
    
    print("\n=== Retrieval Evaluation Summary ===\n")
    print(f"Using embedding model: {embedding_generator.model_name}")
    print(f"Model description: InstructorXL model for improved performance\n")
    
    if args.debug:
        print("Checking collection sizes:")
        print("-" * 50)
        for collection_name in ["api_docs", "reachy2_sdk", "reachy2_tutorials"]:
            try:
                collection = db.client.get_collection(collection_name)
                count = collection.count()
                print(f"{collection_name}: {count} documents")
            except Exception as e:
                print(f"Could not get collection {collection_name}: {e}")
        print()
    
    print("Starting evaluation...\n")
    evaluate_retrieval(db, embedding_generator)

if __name__ == "__main__":
    from math import log2
    main() 