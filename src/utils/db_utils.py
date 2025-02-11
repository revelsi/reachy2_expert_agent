import io
import os
import shutil
import sys
import tempfile
from contextlib import contextmanager
from typing import Callable, Dict, List, Optional

import chromadb
import numpy as np
from chromadb.config import Settings


@contextmanager
def suppress_stdout():
    """Context manager to temporarily suppress stdout."""
    stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        yield
    finally:
        sys.stdout = stdout


class VectorStore:
    """Vector store wrapper for document storage and retrieval."""

    # Collection-specific search instructions for better embeddings
    COLLECTION_INSTRUCTIONS = {
        "api_docs_functions": """Represent this OFFICIAL API function documentation for the Reachy2 SDK.
This collection contains standalone functions with their signatures, documentation, and implementations.
Use these functions for actual implementation as they are guaranteed to be part of the public API.""",
        "api_docs_classes": """Represent this OFFICIAL API class documentation for the Reachy2 SDK.
This collection contains two types of chunks:
1. Class overviews with class docstrings and method summaries
2. Individual method documentation with signatures and implementations
Use these classes and methods for actual implementation as they are guaranteed to be part of the public API.""",
        "api_docs_modules": """Represent this OFFICIAL module documentation for the Reachy2 SDK.
This collection contains high-level module documentation and organization information.
Use this to understand the SDK's structure and module purposes.""",
        "reachy2_tutorials": """Represent this tutorial content which contains example code and explanations.
Each chunk contains either tutorial explanations or complete working code examples.
Note: While tutorials demonstrate usage patterns, they may contain custom helper functions.
Always verify methods against the official API documentation.""",
        "reachy2_sdk": """Represent this SDK example code and implementation patterns.
Each chunk contains complete, working examples showing how to use the SDK.
Note: While examples show implementation patterns, always verify methods against the API documentation.""",
        "vision_examples": """Represent this Vision module example code and documentation.
Each chunk contains complete examples of using the vision system and cameras.
Note: These examples demonstrate vision-specific functionality and camera integration.""",
    }

    def __init__(self, persist_directory: str = "data/vectorstore"):
        """Initialize the vector store with persistence."""
        self.persist_directory = persist_directory

        # Create a temporary directory for the database
        self.temp_dir = tempfile.mkdtemp()
        print(f"Using temporary directory: {self.temp_dir}")

        # Initialize client with temporary directory and settings
        self._initialize_client()

        # If the persist directory exists, try to copy its contents
        if os.path.exists(persist_directory):
            try:
                shutil.copytree(persist_directory, self.temp_dir, dirs_exist_ok=True)
                print(f"Copied existing database from {persist_directory}")
            except Exception as e:
                print(f"Warning: Could not copy existing database: {e}")

    def _initialize_client(self):
        """Initialize the ChromaDB client with appropriate settings."""
        settings = chromadb.Settings(
            anonymized_telemetry=False, allow_reset=True, is_persistent=True
        )

        try:
            self.client = chromadb.PersistentClient(
                path=self.temp_dir, settings=settings
            )
        except Exception as e:
            print(f"Error initializing ChromaDB client: {e}")
            raise

    def cleanup(self):
        """Clean up the vectorstore directory completely."""
        print(f"Cleaning up vectorstore directory")

        try:
            # Delete all collections first
            collections = self.client.list_collections()
            for collection in collections:
                try:
                    self.client.delete_collection(collection)
                except Exception as e:
                    print(f"Warning: Could not delete collection {collection}: {e}")

            # Close the client connection
            del self.client

            # Remove the temporary directory
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                print(f"Removed temporary directory")

            # Create a new temporary directory
            self.temp_dir = tempfile.mkdtemp()
            print(f"Created new temporary directory: {self.temp_dir}")

            # Reinitialize the client
            self._initialize_client()
            print("Initialized fresh vectorstore")

        except Exception as e:
            print(f"Warning during cleanup: {e}")
            # Ensure client is reinitialized even if cleanup fails
            self._initialize_client()

    def save(self):
        """Save the current state to the persist directory."""
        try:
            print("[DEBUG] Starting save operation...")

            # Close client connection
            del self.client
            print("[DEBUG] Closed client connection")

            # Remove existing persist directory if it exists
            if os.path.exists(self.persist_directory):
                print(
                    f"[DEBUG] Removing existing persist directory: {self.persist_directory}"
                )
                shutil.rmtree(self.persist_directory)

            # Copy temporary directory to persist directory
            print(f"[DEBUG] Copying from {self.temp_dir} to {self.persist_directory}")
            shutil.copytree(self.temp_dir, self.persist_directory)
            print(f"[DEBUG] Database saved to {self.persist_directory}")

            # Reinitialize client
            self._initialize_client()
            print("[DEBUG] Reinitialized client")

        except Exception as e:
            print(f"[ERROR] Error during save: {e}")
            # Ensure client is reinitialized
            self._initialize_client()

    def __del__(self):
        """Cleanup temporary directory on object destruction."""
        try:
            if hasattr(self, "client"):
                del self.client
            if hasattr(self, "temp_dir") and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
        except Exception:
            pass

    def get_collection_with_dimension_check(self, name: str, embedding_function):
        """Get or create a collection with dimension checking and auto-recreation if needed."""
        try:
            # Try to get existing collection
            collection = self.client.get_collection(name=name)

            # Test dimensionality with a dummy embedding
            dummy_text = "test"
            dummy_embedding = embedding_function([dummy_text])
            expected_dim = len(dummy_embedding[0])

            # Try a dummy query to check if dimensions match
            try:
                collection.query(query_texts=[dummy_text], n_results=1)
                return collection
            except chromadb.errors.InvalidDimensionException:
                print(f"Recreating collection '{name}' due to dimension mismatch...")

                # Delete and recreate collection
                self.client.delete_collection(name)
                new_collection = self.client.create_collection(
                    name=name, embedding_function=embedding_function
                )
                return new_collection

        except chromadb.errors.InvalidCollectionException:
            # Collection doesn't exist, create new one
            return self.client.create_collection(
                name=name, embedding_function=embedding_function
            )

    def add_documents(
        self,
        collection_name: str,
        texts: List[str],
        metadatas: List[Dict],
        ids: List[str],
        embedding_function,
    ):
        """Add documents to a collection with collection-specific embedding instructions."""
        # Get or create collection
        collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=embedding_function,
            metadata={"hnsw:space": "cosine"},
        )

        # Add collection-specific instruction to each text
        instruction = self.COLLECTION_INSTRUCTIONS.get(collection_name, "")
        if instruction:
            texts = [f"{instruction}:\n{text}" for text in texts]

        # Process in batches of 100 documents
        BATCH_SIZE = 100
        for i in range(0, len(texts), BATCH_SIZE):
            batch_end = min(i + BATCH_SIZE, len(texts))
            batch_texts = texts[i:batch_end]
            batch_metadatas = metadatas[i:batch_end]
            batch_ids = ids[i:batch_end]
            
            print(f"Adding batch {i//BATCH_SIZE + 1} ({len(batch_texts)} documents)...")
            try:
                # Add documents to collection
                collection.add(
                    documents=batch_texts,
                    metadatas=batch_metadatas,
                    ids=batch_ids
                )
            except Exception as e:
                print(f"Error adding batch: {str(e)}")
                # If batch fails, try with smaller batch size
                RETRY_BATCH_SIZE = 50
                for j in range(i, batch_end, RETRY_BATCH_SIZE):
                    retry_end = min(j + RETRY_BATCH_SIZE, batch_end)
                    print(f"Retrying with smaller batch {j//RETRY_BATCH_SIZE + 1}...")
                    try:
                        collection.add(
                            documents=texts[j:retry_end],
                            metadatas=metadatas[j:retry_end],
                            ids=ids[j:retry_end]
                        )
                    except Exception as e:
                        print(f"Error adding smaller batch: {str(e)}")
                        raise

    def query_collection(
        self,
        collection_name: str,
        query_texts: List[str],
        n_results: int = 5,
        embedding_function: Callable = None,
    ) -> Dict:
        """Query a collection with collection-specific embedding instructions."""
        collection = self.client.get_collection(
            name=collection_name, embedding_function=embedding_function
        )

        # Add collection-specific instruction to query
        instruction = self.COLLECTION_INSTRUCTIONS.get(collection_name, "")
        if instruction:
            query_texts = [
                f"{instruction}\n\nQuery for relevant information from this source: {text}"
                for text in query_texts
            ]

        # Only include necessary data in the query
        return collection.query(
            query_texts=query_texts,
            n_results=n_results,
            include=["documents", "distances"],
        )
