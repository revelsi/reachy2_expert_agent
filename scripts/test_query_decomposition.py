import sys
import os

# Ensure the parent directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.rag_utils import QueryDecomposer

def test_decomposition(decomposer: QueryDecomposer, query: str):
    """Test the decomposition of a single query and print results."""
    print("\nOriginal Query:", query)
    print("-" * 50)
    
    try:
        sub_queries = decomposer.decompose_query(query)
        print("Decomposed into:")
        for i, sub_query in enumerate(sub_queries, 1):
            print(f"{i}. {sub_query}")
    except Exception as e:
        print(f"Error decomposing query: {e}")
    
    print("-" * 50)

def main():
    # Initialize the decomposer
    decomposer = QueryDecomposer()
    
    # Test cases - from simple to complex queries
    test_queries = [
        "Wave hello with Reachy's right arm",
        "How do I make Reachy pick up an object from the table?",
        "Make the robot turn left, move forward 2 meters, and wave its left arm",
        "What's the process to calibrate both arms and check their joint positions?",
        "Can you show me how to make Reachy play a simple game of tic-tac-toe?"
    ]
    
    print("Testing Query Decomposition")
    print("=" * 50)
    
    for query in test_queries:
        test_decomposition(decomposer, query)

if __name__ == "__main__":
    main() 