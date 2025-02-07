from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional, Tuple
from langchain.docstore.document import Document
import numpy as np
from chromadb.api.types import Documents, EmbeddingFunction
import uuid

class ChromaEmbeddingFunction(EmbeddingFunction):
    """Wrapper class for sentence-transformers model to match ChromaDB's interface."""
    
    def __init__(self, model: SentenceTransformer):
        self.model = model
    
    def __call__(self, input: Documents) -> List[List[float]]:
        """Generate embeddings for input texts.
        
        Args:
            input: List of texts to embed
            
        Returns:
            List of embeddings as float lists
        """
        return self.model.encode(input).tolist()

class EmbeddingGenerator:
    """Handles document embedding generation using InstructorXL by default."""
    
    def __init__(self, model_name: str = "hkunlp/instructor-xl"):
        """Initialize the embedding generator.
        
        Args:
            model_name: Name of the model to use. Defaults to InstructorXL.
        """
        self.model_name = model_name
        print(f"Initializing embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.embedding_function = ChromaEmbeddingFunction(self.model)

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

def prepare_documents_for_db(documents: List) -> Tuple[List[str], List[Dict], List[str]]:
    """Prepare documents for database storage by extracting content and metadata.
    
    Args:
        documents: List of Document objects
        
    Returns:
        Tuple of (texts, metadatas, ids)
    """
    texts = []
    metadatas = []
    ids = []
    
    for doc in documents:
        try:
            # Get document content
            content = doc.page_content if hasattr(doc, 'page_content') else str(doc)
            
            # Get or create metadata
            metadata = {}
            if hasattr(doc, 'metadata'):
                metadata.update(doc.metadata)
            
            # Ensure required metadata fields exist
            if not metadata:
                metadata = {
                    "source": "unknown",
                    "type": "document",
                    "collection": "unknown"
                }
            
            # Generate unique ID
            doc_id = str(uuid.uuid4())
            
            texts.append(content)
            metadatas.append(metadata)
            ids.append(doc_id)
            
        except Exception as e:
            print(f"Warning: Could not prepare document for database: {e}")
            continue
    
    if not texts:
        raise ValueError("No valid documents to prepare")
    
    return texts, metadatas, ids 