import time
from utils.embedding_utils import EmbeddingGenerator
import numpy as np

def test_model(model_name: str, test_texts: list):
    print(f"\nTesting model: {model_name}")
    
    # Test initialization time
    start_time = time.time()
    model = EmbeddingGenerator(model_name=model_name)
    init_time = time.time() - start_time
    print(f"Initialization time: {init_time:.2f} seconds")
    
    # Test embedding generation time
    start_time = time.time()
    embeddings = model(test_texts)
    embed_time = time.time() - start_time
    print(f"Embedding generation time for {len(test_texts)} texts: {embed_time:.2f} seconds")
    print(f"Average time per text: {(embed_time/len(test_texts)):.3f} seconds")
    
    # Print embedding dimensionality
    if isinstance(embeddings, list):
        dim = len(embeddings[0])
        print(f"Embedding dimensionality: {dim}")
    
    return init_time, embed_time

def main():
    # Test data
    test_texts = [
        "This is a test sentence about robotics and automation.",
        "Another example discussing robot control systems.",
        "Documentation about mechanical components and sensors.",
        "Information about robot programming and interfaces.",
        "Details about robot kinematics and motion planning."
    ]
    
    # Models to test
    models = [
        "hkunlp/instructor-xl",    # Extra large model
        "hkunlp/instructor-large", # Large model
        "hkunlp/instructor-base",  # Base model
    ]
    
    results = []
    
    # Run tests
    for model_name in models:
        try:
            init_time, embed_time = test_model(model_name, test_texts)
            results.append({
                'model': model_name,
                'init_time': init_time,
                'embed_time': embed_time,
                'avg_time_per_text': embed_time/len(test_texts)
            })
        except Exception as e:
            print(f"Error testing {model_name}: {str(e)}")
    
    # Print summary
    print("\nSummary:")
    print("-" * 80)
    print(f"{'Model':<40} | {'Init (s)':<10} | {'Total (s)':<10} | {'Avg/text (s)':<10}")
    print("-" * 80)
    for r in results:
        print(f"{r['model']:<40} | {r['init_time']:<10.2f} | {r['embed_time']:<10.2f} | {r['avg_time_per_text']:<10.3f}")

if __name__ == "__main__":
    main() 