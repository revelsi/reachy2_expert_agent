import os
import signal
import sys
import time
from contextlib import contextmanager

# Ensure the parent directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.utils.rag_utils import RAGPipeline


class TimeoutException(Exception):
    pass


@contextmanager
def timeout(seconds):
    def signal_handler(signum, frame):
        raise TimeoutException("Timed out!")

    # Register a function to raise a TimeoutException on the signal
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)

    try:
        yield
    finally:
        # Disable the alarm
        signal.alarm(0)


def test_pipeline(pipeline: RAGPipeline, query: str):
    """Test the complete RAG pipeline with a single query."""
    print("\nTesting Query:", query)
    print("=" * 80)

    try:
        # Get decomposed queries
        print("\n1. Query Decomposition Results:")
        print("-" * 40)
        with timeout(30):  # Set 30-second timeout for decomposition
            sub_queries = pipeline.decomposer.decompose_query(query)
            for i, sub_query in enumerate(sub_queries, 1):
                print(f"  {i}. {sub_query}")

        # Process the complete query through the pipeline
        print("\n2. Generated Response:")
        print("-" * 40)
        with timeout(60):  # Set 60-second timeout for response generation
            response = pipeline.process_query(query)
            print(response)

    except TimeoutException:
        print("Operation timed out! Please try again.")
    except KeyboardInterrupt:
        print("\nOperation interrupted by user.")
    except Exception as e:
        print(f"Error processing query: {str(e)}")

    print("\n" + "=" * 80)


def main():
    try:
        # Initialize the pipeline
        pipeline = RAGPipeline()

        # Test cases
        test_queries = [
            "Wave hello with Reachy's right arm",
            "How do I make Reachy pick up an object from the table?",
            "Make the robot turn left, move forward 2 meters, and wave its left arm",
        ]

        print("\nReachy2 Expert Agent - RAG Pipeline Test")
        print("=" * 80)

        for i, query in enumerate(test_queries, 1):
            print(f"\nTest Case {i}/{len(test_queries)}")
            test_pipeline(pipeline, query)
            time.sleep(1)  # Add a small delay between queries

    except KeyboardInterrupt:
        print("\nTest suite interrupted by user.")
    except Exception as e:
        print(f"Error in test suite: {str(e)}")
    finally:
        print("\nTest suite completed.")


if __name__ == "__main__":
    main()
