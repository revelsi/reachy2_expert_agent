from sentence_transformers import SentenceTransformer
from typing import List, Dict
from langchain.docstore.document import Document

class EmbeddingGenerator:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize the embedding generator with a specific model."""
        self.model = SentenceTransformer(model_name)
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        return self.model.encode(texts, convert_to_tensor=False).tolist()

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
        
        texts.append(doc.page_content)
        metadatas.append(doc.metadata)
        ids.append(doc_id)
    
    return texts, metadatas, ids 