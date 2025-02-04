import chromadb
from chromadb.config import Settings
import os
from typing import List, Dict, Optional

class VectorStore:
    def __init__(self, persist_directory: str = "vectorstore"):
        """Initialize ChromaDB with persistence."""
        self.persist_directory = persist_directory
        os.makedirs(persist_directory, exist_ok=True)
        
        self.client = chromadb.PersistentClient(path=persist_directory)
    
    def get_or_create_collection(self, name: str):
        """Get an existing collection or create a new one."""
        return self.client.get_or_create_collection(name=name)
    
    def add_documents(self, 
                     collection_name: str,
                     texts: List[str],
                     embeddings: List[List[float]],
                     metadatas: List[Dict],
                     ids: List[str]):
        """
        Add documents to a collection.
        If the collection doesn't exist, it will be created.
        """
        collection = self.get_or_create_collection(collection_name)
        
        # Add documents in batches to avoid memory issues
        batch_size = 100
        for i in range(0, len(texts), batch_size):
            end_idx = min(i + batch_size, len(texts))
            collection.add(
                embeddings=embeddings[i:end_idx],
                documents=texts[i:end_idx],
                metadatas=metadatas[i:end_idx],
                ids=ids[i:end_idx]
            )
    
    def query_collection(self,
                        collection_name: str,
                        query_texts: List[str],
                        n_results: int = 5,
                        where: Optional[Dict] = None) -> List[Dict]:
        """
        Query the collection with the given texts and optional filters.
        Returns the n_results most similar documents for each query.
        """
        collection = self.get_or_create_collection(collection_name)
        
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