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
        "api_docs_modules": ["arm", "goto_based_part", "joints_based_part"],
        "api_docs_classes": ["Arm", "ArmController", "goto", "translate_by", "rotate_by"],
        "api_docs_functions": ["turn_on", "goto", "rotate_by", "translate_by", "set_goal_positions"],
        "reachy2_sdk": ["Move Reachy's right arm", "goto_posture", "rotate_by"],
        "reachy2_tutorials": ["Arm movement", "goto", "translate_by", "rotate_by"]
    },
    "What is the camera API?": {
        "api_docs_modules": ["camera", "camera_manager", "media"],
        "api_docs_classes": ["CameraManager", "CameraView", "get_image"],
        "api_docs_functions": ["get_image", "get_intrinsics", "get_camera_info"],
        "vision_examples": ["camera_wrapper", "SDKWrapper", "get_image"],
        "reachy2_tutorials": ["camera_usage", "get_image", "camera_setup"]
    },
    "How to control the gripper?": {
        "api_docs_modules": ["hand", "gripper"],
        "api_docs_classes": ["Gripper", "GripperController", "open", "close"],
        "api_docs_functions": ["open", "close", "set_opening", "get_opening"],
        "reachy2_sdk": ["Gripper Control", "open", "close", "set_opening"],
        "reachy2_tutorials": ["gripper.open", "gripper.close", "gripper_control"]
    },
    "How to get joint positions?": {
        "api_docs_modules": ["joints_based_part", "part"],
        "api_docs_classes": ["Joint", "JointState", "get_positions"],
        "api_docs_functions": ["get_current_positions", "get_joint_states", "get_state"],
        "reachy2_sdk": ["get_positions", "joint_states", "current_position"],
        "reachy2_tutorials": ["joint_positions", "get_positions", "joint_states"]
    },
    "How to handle errors and exceptions?": {
        "api_docs_modules": ["utils", "error_handling"],
        "api_docs_classes": ["RobotError", "ConnectionManager", "handle_error"],
        "api_docs_functions": ["is_connected", "check_connection", "handle_error"],
        "reachy2_sdk": ["error_handling", "try_except", "connection_error"],
        "reachy2_tutorials": ["error_handling", "try_except", "connection_error"]
    },
    "How to control mobile base movement?": {
        "api_docs_modules": ["mobile_base", "base_controller"],
        "api_docs_classes": ["MobileBase", "BaseController", "move_to"],
        "api_docs_functions": ["move_forward", "turn", "set_velocity", "stop"],
        "reachy2_sdk": ["mobile_base", "move_to", "rotate"],
        "reachy2_tutorials": ["mobile_base", "move_forward", "turn"]
    }
}

# Use a smaller model for faster evaluation
EVAL_MODEL = "hkunlp/instructor-base"

def calculate_metrics(results: Dict, relevant_ids: List[str]) -> Dict[str, float]:
    """Calculate retrieval metrics with enhanced semantic matching.
    
    Args:
        results: Dictionary containing retrieved documents and their distances
        relevant_ids: List of relevant document IDs to compare against
        
    Returns:
        Dictionary containing precision, recall, MRR, and nDCG metrics
    """
    retrieved_docs = results['documents'][0]
    k = len(retrieved_docs)
    
    # Enhanced relevance matching
    relevant_retrieved = []
    for doc in retrieved_docs:
        # Extract content for matching
        content = doc.lower()
        
        # Check exact matches
        exact_match = any(rel_id.lower() in content for rel_id in relevant_ids)
        
        # Check semantic matches with context awareness
        semantic_match = any(
            rel_id.lower().replace('_', '.') in content or  # handle method calls
            rel_id.lower().replace('.', '_') in content or  # handle function names
            any(word in content for word in rel_id.lower().split('_')) or  # partial matches
            any(  # handle common variations
                variation in content 
                for rel_id in relevant_ids 
                for variation in [
                    f"def {rel_id}",  # function definitions
                    f"class {rel_id}",  # class definitions
                    f"{rel_id}(",  # function calls
                    f".{rel_id}",  # method calls
                    f"'{rel_id}'",  # string literals
                    f"\"{rel_id}\"",  # string literals
                    f"Method: {rel_id}",  # method documentation
                    f"Function: {rel_id}"  # function documentation
                ]
            )
            for rel_id in relevant_ids
        )
        
        # Consider distance score for borderline cases
        distance_score = results['distances'][0][retrieved_docs.index(doc)]
        distance_boost = distance_score < 0.4  # Consider very close matches
        
        relevant_retrieved.append(exact_match or semantic_match or distance_boost)
    
    # Calculate standard metrics
    num_relevant_retrieved = sum(relevant_retrieved)
    precision_at_k = num_relevant_retrieved / k if k > 0 else 0
    recall_at_k = num_relevant_retrieved / len(relevant_ids) if relevant_ids else 0
    
    # Calculate MRR with position weighting
    mrr = 0
    for i, is_relevant in enumerate(relevant_retrieved):
        if is_relevant:
            position_weight = 1.0 if i == 0 else 0.9 ** i  # Exponential decay for later positions
            mrr = position_weight * (1.0 / (i + 1))
            break
    
    # Calculate nDCG with graded relevance
    def get_relevance_grade(doc, rel_ids):
        exact_matches = sum(1 for rel_id in rel_ids if rel_id.lower() in doc.lower())
        semantic_matches = sum(1 for rel_id in rel_ids if any(
            variation in doc.lower() 
            for variation in [
                rel_id.lower().replace('_', '.'),
                rel_id.lower().replace('.', '_'),
                f"def {rel_id.lower()}",
                f"class {rel_id.lower()}",
                f"{rel_id.lower()}("
            ]
        ))
        return min(3, exact_matches + semantic_matches)  # Cap at 3 for reasonable scaling
    
    relevance_grades = [get_relevance_grade(doc, relevant_ids) for doc in retrieved_docs]
    dcg = sum(
        (2 ** grade - 1) / log2(i + 2)
        for i, grade in enumerate(relevance_grades)
    )
    
    # Calculate ideal DCG
    ideal_grades = sorted([3] * len(relevant_ids), reverse=True)[:k]
    idcg = sum(
        (2 ** grade - 1) / log2(i + 2)
        for i, grade in enumerate(ideal_grades)
    ) if ideal_grades else 1
    
    ndcg = dcg / idcg if idcg > 0 else 0
    
    return {
        "precision": precision_at_k,
        "recall": recall_at_k,
        "mrr": mrr,
        "ndcg": ndcg
    }

def save_metrics_to_file(collection_metrics: Dict, output_file: str):
    """Save evaluation metrics to a file with detailed formatting."""
    with open(output_file, 'w') as f:
        f.write("=== Reachy2 Expert Agent Retrieval Evaluation Results ===\n\n")
        
        # Write summary statistics
        f.write("Summary Statistics:\n")
        f.write("-" * 80 + "\n")
        f.write(f"{'Collection':<20} {'Precision@5':<12} {'Recall@5':<12} {'MRR':<12} {'nDCG@5':<12}\n")
        f.write("-" * 80 + "\n")
        
        for collection in collection_metrics:
            metrics = collection_metrics[collection]
            avg_metrics = {
                name: sum(values) / len(values) if values else 0 
                for name, values in metrics.items()
            }
            f.write(f"{collection:<20} {avg_metrics['precision']:<12.3f} "
                   f"{avg_metrics['recall']:<12.3f} {avg_metrics['mrr']:<12.3f} "
                   f"{avg_metrics['ndcg']:<12.3f}\n")
        
        # Write detailed metrics per query
        f.write("\n\nDetailed Metrics by Query:\n")
        f.write("=" * 80 + "\n\n")
        
        for i, (query, _) in enumerate(TEST_QUERIES.items()):
            f.write(f"Query {i+1}: {query}\n")
            f.write("-" * 80 + "\n")
            f.write(f"{'Collection':<20} {'Precision@5':<12} {'Recall@5':<12} {'MRR':<12} {'nDCG@5':<12}\n")
            f.write("-" * 40 + "\n")
            
            for collection in collection_metrics:
                metrics = collection_metrics[collection]
                f.write(f"{collection:<20} {metrics['precision'][i]:<12.3f} "
                       f"{metrics['recall'][i]:<12.3f} {metrics['mrr'][i]:<12.3f} "
                       f"{metrics['ndcg'][i]:<12.3f}\n")
            f.write("\n")

def evaluate_retrieval(db: VectorStore, embedding_generator: EmbeddingGenerator):
    """Evaluate retrieval performance across all test queries."""
    collections = ["reachy2_tutorials", "reachy2_sdk", "api_docs_classes", "api_docs_functions"]
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
    
    return collection_metrics

def main():
    """Run the evaluation pipeline."""
    print(f"Using {EVAL_MODEL} for evaluation")
    
    # Initialize embedding generator with evaluation model
    embedding_generator = EmbeddingGenerator(model_name=EVAL_MODEL)
    
    # Initialize vector store
    vector_store = VectorStore()
    
    # Run evaluation
    evaluate_retrieval(vector_store, embedding_generator)
    
    # Save results
    save_metrics_to_file(
        collection_metrics={},  # Will be populated by evaluate_retrieval
        output_file="evaluation_results.txt"
    )

if __name__ == "__main__":
    from math import log2
    main() 