from langchain.docstore.document import Document
import json


def document_to_dict(doc: Document) -> dict:
    """Converts a Document to a dictionary."""
    return {"page_content": doc.page_content, "metadata": doc.metadata}


def document_from_dict(d: dict) -> Document:
    """Creates a Document from a dictionary."""
    return Document(page_content=d["page_content"], metadata=d["metadata"])


def save_documents_to_json(documents: list, output_file: str):
    """Serializes a list of Document objects to a JSON file."""
    with open(output_file, "w") as f:
        json.dump([document_to_dict(doc) for doc in documents], f, indent=2)


def load_documents_from_json(input_file: str) -> list:
    """Loads a JSON file and returns a list of Document objects."""
    with open(input_file, "r") as f:
        data = json.load(f)
    return [document_from_dict(doc) for doc in data] 