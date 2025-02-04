from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
from langchain.docstore.document import Document

class EmbeddingGenerator:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize the embedding generator with a specific model."""
        self.model = SentenceTransformer(model_name)
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        return self.model.encode(texts, convert_to_tensor=False).tolist()

def clean_metadata_value(value: Any) -> Any:
    """
    Clean metadata values to ensure they're compatible with ChromaDB.
    ChromaDB only accepts str, int, float, or bool.
    """
    if value is None:
        return ""  # Convert None to empty string
    if isinstance(value, (str, int, float, bool)):
        return value
    return str(value)  # Convert any other type to string

def clean_metadata(metadata: Dict) -> Dict:
    """Clean all values in a metadata dictionary."""
    return {k: clean_metadata_value(v) for k, v in metadata.items()}

def prepare_documents_for_db(documents: List[Document]) -> tuple[List[str], List[Dict], List[str]]:
    """
    Prepare documents for database storage by extracting necessary components.
    Returns:
        tuple containing (documents texts, metadata dicts, document ids)
    """
    texts = []
    metadatas = []
    ids = []
    
    for idx, doc in enumerate(documents):
        # Create a unique ID based on content hash and index
        doc_id = f"doc_{hash(doc.page_content)}_{idx}"
        
        # Clean metadata to ensure compatibility with ChromaDB
        cleaned_metadata = clean_metadata(doc.metadata)
        
        texts.append(doc.page_content)
        metadatas.append(cleaned_metadata)
        ids.append(doc_id)
    
    return texts, metadatas, ids 