import gradio as gr
from rag_pipeline import build_vectorstore
from chatbot import build_chatbot

# Initialize the RAG pipeline and chatbot.
vectorstore = build_vectorstore()
chatbot = build_chatbot(vectorstore)

def process_input(user_input):
    """
    Process user input: retrieve relevant info and generate code.
    """
    if not user_input.strip():
        return "Please provide an input instruction."
    try:
        # Run your query through the RetrievalQA chain.
        result = chatbot.run(user_input)
        return result
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Create a simple Gradio interface.
iface = gr.Interface(
    fn=process_input,
    inputs="text",
    outputs="text",
    title="Reachy 2 Code Generator",
    description="Generate code for Reachy 2 with natural language instructions."
)

if __name__ == "__main__":
    iface.launch() 