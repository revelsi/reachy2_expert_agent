from langchain.docstore.document import Document
import json
from typing import List, Dict, Tuple


def document_to_dict(doc: Document) -> dict:
    """Converts a Document to a dictionary."""
    return {"page_content": doc.page_content, "metadata": doc.metadata}


def document_from_dict(d: dict) -> Document:
    """Creates a Document from a dictionary with robust error handling."""
    try:
        # Handle both 'page_content' and 'content' keys for backward compatibility
        content = d.get("page_content", d.get("content", ""))
        if not content and not isinstance(content, str):
            content = ""
            print("Warning: Empty or invalid content found")
        
        # Handle missing or invalid metadata
        metadata = d.get("metadata", {})
        if not isinstance(metadata, dict):
            print(f"Warning: Invalid metadata format found: {type(metadata)}, using empty dict")
            metadata = {}
        
        return Document(page_content=content, metadata=metadata)
    except Exception as e:
        print(f"Error creating document: {str(e)}")
        # Return a minimal valid document rather than failing
        return Document(page_content="", metadata={})


def save_documents_to_json(documents: list, output_file: str):
    """Serializes a list of Document objects to a JSON file."""
    try:
        # Convert documents to dicts, handling potential errors
        doc_dicts = []
        for doc in documents:
            try:
                doc_dicts.append(document_to_dict(doc))
            except Exception as e:
                print(f"Warning: Could not convert document to dict: {str(e)}")
                continue
        
        # Save to file
        with open(output_file, "w", encoding='utf-8') as f:
            json.dump(doc_dicts, f, indent=2, ensure_ascii=False)
            
    except Exception as e:
        print(f"Error saving documents to {output_file}: {str(e)}")
        raise


def load_documents_from_json(input_file: str) -> list:
    """Loads a JSON file and returns a list of Document objects with error handling."""
    try:
        with open(input_file, "r", encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            raise ValueError(f"Expected a list of documents, got {type(data)}")
        
        documents = []
        for i, doc_dict in enumerate(data):
            try:
                doc = document_from_dict(doc_dict)
                documents.append(doc)
            except Exception as e:
                print(f"Warning: Could not load document {i}: {str(e)}")
                continue
        
        if not documents:
            print(f"Warning: No valid documents loaded from {input_file}")
        
        return documents
        
    except Exception as e:
        print(f"Error loading documents from {input_file}: {str(e)}")
        return []


def prepare_documents_for_db(documents: List[Dict]) -> Tuple[List[str], List[Dict], List[str]]:
    """Prepare documents for database insertion by extracting texts, metadata, and generating IDs."""
    texts = []
    metadatas = []
    ids = []
    
    for i, doc in enumerate(documents):
        # Extract content and metadata
        content = doc.get('content', '')
        metadata = doc.get('metadata', {})
        
        # Clean metadata - ensure all values are valid types
        cleaned_metadata = {}
        for key, value in metadata.items():
            if value is None:
                cleaned_metadata[key] = ""  # Replace None with empty string
            elif isinstance(value, (str, int, float, bool)):
                cleaned_metadata[key] = value
            else:
                cleaned_metadata[key] = str(value)  # Convert other types to string
        
        # Generate unique ID
        doc_id = f"{cleaned_metadata.get('collection', 'doc')}_{cleaned_metadata.get('type', 'unknown')}_{i}"
        
        texts.append(content)
        metadatas.append(cleaned_metadata)
        ids.append(doc_id)
    
    return texts, metadatas, ids 