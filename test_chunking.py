import os
from scripts.chunk_documents import chunk_tutorial_notebook

# Test with the first tutorial
notebook_path = os.path.join("raw_docs", "reachy2_tutorials", "1_Reachy_awakening.ipynb")

print("Testing new chunking strategy on:", notebook_path)
print("\nGenerated chunks:")
print("-" * 80)

chunks = chunk_tutorial_notebook(notebook_path)
for i, chunk in enumerate(chunks, 1):
    print(f"\nChunk {i}:")
    print("-" * 40)
    print(chunk)
    print("-" * 40)
    print(f"Chunk size: {len(chunk)} characters") 