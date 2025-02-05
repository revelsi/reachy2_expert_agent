import chromadb
from chromadb.config import Settings
import os
import tempfile
from typing import List, Dict, Optional
import numpy as np
import shutil

class VectorStore:
    def __init__(self, persist_directory: str = "vectorstore"):
        """Initialize the vector store with persistence."""
        self.persist_directory = persist_directory
        
        # Create a temporary directory for the database
        self.temp_dir = tempfile.mkdtemp()
        print(f"Using temporary directory: {self.temp_dir}")
        
        # Initialize client with temporary directory
        self.client = chromadb.PersistentClient(path=self.temp_dir)
        
        # If the persist directory exists, try to copy its contents
        if os.path.exists(persist_directory):
            try:
                shutil.copytree(persist_directory, self.temp_dir, dirs_exist_ok=True)
                print(f"Copied existing database from {persist_directory}")
            except Exception as e:
                print(f"Warning: Could not copy existing database: {e}")

    def cleanup(self):
        """Clean up the vectorstore directory completely."""
        print(f"Cleaning up vectorstore directory")
        
        try:
            # Delete all collections first
            for collection in self.client.list_collections():
                print(f"Deleting collection: {collection.name}")
                self.client.delete_collection(collection.name)
            
            # Close the client connection
            del self.client
            
            # Remove the temporary directory
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                print(f"Removed temporary directory")
            
            # Create a new temporary directory
            self.temp_dir = tempfile.mkdtemp()
            print(f"Created new temporary directory: {self.temp_dir}")
            
        except Exception as e:
            print(f"Warning during cleanup: {e}")
        
        # Reinitialize the client with a fresh directory
        self.client = chromadb.PersistentClient(path=self.temp_dir)
        print("Initialized fresh vectorstore")

    def save(self):
        """Save the current state to the persist directory."""
        try:
            print('[DEBUG] Starting save operation...')
            print('[DEBUG] Deleting client connection...')
            del self.client
            
            print('[DEBUG] Checking if persist directory exists...')
            if os.path.exists(self.persist_directory):
                print(f'[DEBUG] Persist directory exists at {self.persist_directory}, removing it...')
                shutil.rmtree(self.persist_directory)
                print('[DEBUG] Persist directory removed.')
            else:
                print('[DEBUG] No persist directory found.')
            
            print(f'[DEBUG] Copying temporary directory from {self.temp_dir} to {self.persist_directory}...')
            shutil.copytree(self.temp_dir, self.persist_directory)
            print(f'[DEBUG] Copy complete. Database saved to {self.persist_directory}')
            
            print('[DEBUG] Reinitializing client with temporary directory...')
            self.client = chromadb.PersistentClient(path=self.temp_dir)
            print('[DEBUG] Save operation complete.')
        except Exception as e:
            print(f"[ERROR] Warning during save: {e}")
            # Reinitialize client in case of error
            self.client = chromadb.PersistentClient(path=self.temp_dir)

    def __del__(self):
        """Cleanup temporary directory on object destruction."""
        try:
            if hasattr(self, 'client'):
                del self.client
            if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
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
                collection.query(
                    query_texts=[dummy_text],
                    n_results=1
                )
                return collection
            except chromadb.errors.InvalidDimensionException:
                print(f"Recreating collection '{name}' due to dimension mismatch...")
                
                # Delete and recreate collection
                self.client.delete_collection(name)
                new_collection = self.client.create_collection(
                    name=name,
                    embedding_function=embedding_function
                )
                return new_collection
                
        except chromadb.errors.InvalidCollectionException:
            # Collection doesn't exist, create new one
            return self.client.create_collection(
                name=name,
                embedding_function=embedding_function
            )

    def add_documents(self, collection_name: str, texts: List[str], metadatas: List[Dict], ids: List[str], embedding_function):
        """Add documents to a collection, recreating it if dimensions don't match."""
        # Get or create collection with dimension checking
        collection = self.get_collection_with_dimension_check(
            name=collection_name,
            embedding_function=embedding_function
        )
        
        # Add documents
        collection.add(
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
    
    def query_collection(self,
                        collection_name: str,
                        query_texts: List[str],
                        n_results: int = 5,
                        where: Optional[Dict] = None,
                        embedding_function=None) -> List[Dict]:
        """Query the collection with the given texts and optional filters."""
        collection = self.client.get_collection(collection_name)
        
        # If embedding function is provided, use it for this query
        if embedding_function:
            collection._embedding_function = embedding_function
        
        # If where filter is provided, use it
        if where:
            results = collection.query(
                query_texts=query_texts,
                n_results=n_results,
                where=where
            )
        else:
            results = collection.query(
                query_texts=query_texts,
                n_results=n_results
            )
        
        return results 