from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document

def load_documents():
    """
    Load your source documents for Reachy 2.
    In practice, you could load files, fetch from an API, etc.
    """
    texts = [
        "Reachy 2 API docs: [Your API documentation goes here...]",
        "Code Example: ...",  # add more examples as needed.
    ]
    return [Document(page_content=text) for text in texts]

def build_vectorstore():
    """
    Build a Chroma vector store from your documents.
    """
    docs = load_documents()
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    split_docs = text_splitter.split_documents(docs)
    # Use a open-source embedding model. You can experiment with different models.
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = Chroma.from_documents(split_docs, embeddings)
    return vectorstore 