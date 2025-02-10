from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional, Tuple
from langchain.docstore.document import Document
import numpy as np
from chromadb.api.types import Documents, EmbeddingFunction
import uuid
import os
import requests

class ChromaEmbeddingFunction(EmbeddingFunction):
    """Wrapper class for sentence-transformers model to match ChromaDB's interface."""
    def __init__(self, model: SentenceTransformer):
        self.model = model

    def __call__(self, input: Documents) -> List[List[float]]:
        return self.model.encode(input).tolist()

class EmbeddingGenerator(EmbeddingFunction):
    """Handles document embedding generation using a SentenceTransformer model."""
    def __init__(self, model_name: str = "hkunlp/instructor-xl"):
        """Initialize the embedding generator.
        
        Args:
            model_name: Name of the model to use. Defaults to InstructorXL.
        """
        self.model_name = model_name
        import torch
        device = "mps" if torch.backends.mps.is_available() else "cpu"
        print(f"Initializing embedding model: {model_name} on device {device}")
        self.model = SentenceTransformer(model_name, device=device)
        self.embedding_function = ChromaEmbeddingFunction(self.model)

    def __call__(self, input: Documents) -> List[List[float]]:
        instruction = "Represent this robotics documentation for retrieval:"
        text_pairs = [[instruction, text] for text in input]
        return self.embedding_function(text_pairs)

def clean_metadata_value(value: Any) -> Any:
    """Clean metadata values to ensure they are JSON serializable and compatible with ChromaDB."""
    if value is None:
        return ""  # Convert None to empty string for ChromaDB compatibility
    elif isinstance(value, (str, int, float, bool)):
        return value
    elif isinstance(value, (list, tuple)):
        return [clean_metadata_value(v) for v in value]
    elif isinstance(value, dict):
        return {k: clean_metadata_value(v) for k, v in value.items()}
    elif isinstance(value, np.integer):
        return int(value)
    elif isinstance(value, np.floating):
        return float(value)
    elif isinstance(value, np.ndarray):
        return value.tolist()
    else:
        return str(value)

def prepare_documents_for_db(documents: List[Any]) -> Tuple[List[str], List[Dict], List[str]]:
    """Prepare documents for database insertion by extracting texts, metadata, and generating IDs."""
    texts = []
    metadatas = []
    ids = []
    
    for i, doc in enumerate(documents):
        try:
            # Handle both Document objects and dictionaries
            if hasattr(doc, 'page_content'):
                content = doc.page_content
                metadata = doc.metadata if hasattr(doc, 'metadata') else {}
            else:
                content = doc.get('content', '')
                metadata = doc.get('metadata', {})
            
            # Clean metadata - ensure all values are valid types
            cleaned_metadata = {}
            for key, value in metadata.items():
                cleaned_value = clean_metadata_value(value)
                if cleaned_value is not None:  # Only add non-None values
                    cleaned_metadata[key] = cleaned_value
            
            # Generate unique ID
            doc_id = f"{cleaned_metadata.get('collection', 'doc')}_{cleaned_metadata.get('type', 'unknown')}_{i}"
            
            texts.append(content)
            metadatas.append(cleaned_metadata)
            ids.append(doc_id)
            
        except Exception as e:
            print(f"Warning: Could not prepare document {i}: {str(e)}")
            continue
    
    if not texts:
        raise ValueError("No valid documents to prepare")
    
    return texts, metadatas, ids 

class HuggingFaceInstructorEmbeddingFunction(EmbeddingFunction):
    """Wrapper class for InstructorXL that calls HuggingFace Inference API endpoints to generate embeddings."""
    def __init__(self, model_name: str, api_token: Optional[str] = None, api_url: Optional[str] = None):
        self.model_name = model_name
        self.api_token = api_token or os.environ.get("HUGGINGFACE_API_TOKEN")
        if self.api_token is None:
            raise ValueError("HUGGINGFACE_API_TOKEN environment variable not set")
        self.api_url = api_url or os.environ.get("HUGGINGFACE_ENDPOINT_URL") or f"https://api-inference.huggingface.co/models/{model_name}"

    def __call__(self, input: Documents) -> List[List[float]]:
        instruction = "Represent this robotics documentation for retrieval:"
        text_pairs = [[instruction, text] for text in input]
        headers = {"Authorization": f"Bearer {self.api_token}"}
        payload = {"inputs": text_pairs}
        response = requests.post(self.api_url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        return result

class EmbeddingGeneratorHF(EmbeddingFunction):
    """Handles document embedding generation using InstructorXL via HuggingFace inference endpoints."""
    def __init__(self, model_name: str = "hkunlp/instructor-xl", api_token: Optional[str] = None, api_url: Optional[str] = None):
        self.model_name = model_name
        print(f"Initializing HuggingFace inference embedding model: {model_name}")
        self.embedding_function = HuggingFaceInstructorEmbeddingFunction(model_name, api_token, api_url)

    def __call__(self, input: Documents) -> List[List[float]]:
        return self.embedding_function(input) 