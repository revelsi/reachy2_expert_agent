from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional
from langchain.docstore.document import Document
import numpy as np
from chromadb.api.types import Documents, EmbeddingFunction

class ChromaEmbeddingFunction(EmbeddingFunction):
    """Wrapper class for sentence-transformers model to use with ChromaDB."""
    
    def __init__(self, model: SentenceTransformer):
        self.model = model
    
    def __call__(self, texts: Documents) -> List[List[float]]:
        return self.model.encode(texts).tolist()

class EmbeddingGenerator:
    """Class to generate embeddings using sentence-transformers."""
    
    def __init__(self, model_name: str = "all-roberta-large-v1"):
        """Initialize the embedding generator with RoBERTa model by default."""
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self.embedding_function = ChromaEmbeddingFunction(self.model)
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        return self.model.encode(texts).tolist()

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

def prepare_documents_for_db(documents: List[Document]) -> tuple[List[str], List[Dict], List[str]]:
    """Prepare documents for adding to the database."""
    texts = []
    metadatas = []
    ids = []
    
    for i, doc in enumerate(documents):
        # Extract text content
        text = doc.page_content
        if not text:
            continue
            
        # Clean metadata
        metadata = {k: clean_metadata_value(v) for k, v in doc.metadata.items()}
        
        # Generate a unique ID
        doc_id = f"doc_{i}"
        
        texts.append(text)
        metadatas.append(metadata)
        ids.append(doc_id)
    
    return texts, metadatas, ids 