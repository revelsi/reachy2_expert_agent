import gradio as gr
import sys, os

# Ensure the parent directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.db_utils import VectorStore
from utils.embedding_utils import EmbeddingGenerator


def chatbot_response(query: str) -> str:
    """Generate a chatbot response by retrieving relevant documents from the RAG pipeline."""
    # Initialize the vector store and embedding generator
    db = VectorStore()
    embedding_generator = EmbeddingGenerator(model_name="hkunlp/instructor-xl")
    
    # Define the collections to search
    collections = ["reachy2_tutorials", "reachy2_sdk", "api_docs_classes", "api_docs_functions"]
    
    retrieved_results = {}
    for collection in collections:
        results = db.query_collection(
            collection_name=collection,
            query_texts=[query],
            n_results=3,
            embedding_function=embedding_generator.embedding_function
        )
        # Combine the retrieved documents (for now, we simply join the text content)
        docs = results['documents'][0]  # assuming one query
        retrieved_results[collection] = "\n\n".join(docs)
    
    # For this basic version, concatenate all retrieved texts in a formatted way
    response = f"Query: {query}\n"
    for collection, text in retrieved_results.items():
        response += f"\n--- {collection} ---\n{text}\n"
    
    # In a full RAG system, you might now pass this aggregated context to a language model to generate a final answer.
    return response


# Create a Gradio interface
iface = gr.Interface(
    fn=chatbot_response,
    inputs=gr.Textbox(lines=2, placeholder="Enter your query here..."),
    outputs="text",
    title="Reachy2 Expert Agent Chatbot",
    description="Enter a query to retrieve relevant information from the RAG pipeline. This is a basic scaffold." 
)

if __name__ == '__main__':
    iface.launch() 