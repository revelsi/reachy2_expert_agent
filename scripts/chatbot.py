import gradio as gr
import sys, os
import time
from typing import Tuple, Generator, List

# Ensure the parent directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.rag_utils import RAGPipeline
from utils.config import config

# Initialize the RAG pipeline globally to reuse across queries
pipeline = RAGPipeline()

# Custom CSS to match Pollen Robotics website style
CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700&display=swap');

:root {
    --primary-color: #1B2B65;
    --accent-color: #4A90E2;
    --background-color: #FFFFFF;
    --light-bg: #F8FAFC;
    --border-color: #E5E7EB;
}

.gradio-container {
    font-family: 'Archivo', sans-serif !important;
    color: var(--primary-color);
    max-width: 1200px !important;
    margin: 0 auto !important;
    background-color: var(--background-color) !important;
}

.header-container {
    padding: 2rem;
    border-bottom: 1px solid var(--border-color);
    margin-bottom: 2rem;
    background-color: var(--background-color);
}

h1, h2, h3 {
    font-family: 'Archivo', sans-serif !important;
    color: var(--primary-color) !important;
    font-weight: 600 !important;
    letter-spacing: -0.02em;
}

h1 {
    font-size: 2.5rem !important;
    margin-bottom: 1rem !important;
}

.description {
    font-size: 1.1rem;
    line-height: 1.6;
    color: var(--primary-color);
    opacity: 0.8;
    margin-bottom: 2rem;
}

.main-container {
    padding: 0 2rem;
}

.primary-button {
    background: var(--accent-color) !important;
    border: none !important;
    color: white !important;
    font-weight: 500 !important;
    font-size: 1rem !important;
    padding: 0.75rem 1.5rem !important;
    border-radius: 8px !important;
    transition: all 0.2s ease !important;
}

.primary-button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(74, 144, 226, 0.2) !important;
}

.secondary-button {
    background: var(--light-bg) !important;
    border: 1px solid var(--border-color) !important;
    color: var(--primary-color) !important;
    font-weight: 500 !important;
    border-radius: 8px !important;
}

.secondary-button:hover {
    background: #E2E8F0 !important;
}

.chatbot {
    border: 1px solid var(--border-color) !important;
    border-radius: 12px !important;
    background: var(--background-color) !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1) !important;
    margin: 1rem 0 !important;
    padding: 1rem !important;
}

.message {
    border-radius: 8px !important;
    padding: 1rem !important;
    margin: 0.5rem 0 !important;
}

.user-message {
    background: var(--accent-color) !important;
    color: white !important;
}

.bot-message {
    background: var(--light-bg) !important;
    color: var(--primary-color) !important;
    border: 1px solid var(--border-color) !important;
}

.status-text {
    color: var(--primary-color) !important;
    font-weight: 500 !important;
    padding: 0.5rem 1rem !important;
    background: var(--light-bg) !important;
    border-radius: 8px !important;
    margin: 1rem 0 !important;
}

.input-container {
    background: var(--background-color) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 12px !important;
    padding: 1rem !important;
    margin: 1rem 0 !important;
}

.input-box {
    border: 1px solid var(--border-color) !important;
    border-radius: 8px !important;
    padding: 0.75rem !important;
    font-family: 'Archivo', sans-serif !important;
    background: white !important;
    color: var(--primary-color) !important;
}

.input-box:focus {
    border-color: var(--accent-color) !important;
    box-shadow: 0 0 0 2px rgba(74, 144, 226, 0.1) !important;
}

.examples-section {
    margin-top: 2rem !important;
    padding: 1rem !important;
    background: var(--light-bg) !important;
    border-radius: 12px !important;
    border: 1px solid var(--border-color) !important;
}

.tabs {
    border-bottom: 1px solid var(--border-color) !important;
    margin-bottom: 1rem !important;
}

.tab-nav {
    font-family: 'Archivo', sans-serif !important;
    color: var(--primary-color) !important;
    font-weight: 500 !important;
    padding: 0.75rem 1.5rem !important;
    opacity: 0.7;
}

.tab-nav.selected {
    opacity: 1;
    border-bottom: 2px solid var(--accent-color) !important;
}

.copy-button {
    background: var(--accent-color) !important;
    border: none !important;
    color: white !important;
    border-radius: 4px !important;
    padding: 0.25rem 0.5rem !important;
    font-size: 0.875rem !important;
}

.copy-button:hover {
    opacity: 0.9;
}

code {
    background: var(--light-bg) !important;
    color: var(--primary-color) !important;
    padding: 0.2em 0.4em !important;
    border-radius: 4px !important;
    font-size: 0.9em !important;
    border: 1px solid var(--border-color) !important;
}

pre {
    background: var(--light-bg) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 8px !important;
    padding: 1rem !important;
    margin: 1rem 0 !important;
    color: var(--primary-color) !important;
}
"""

def process_query(query: str, history: List[dict]) -> List[dict]:
    """Process a query and return the response with query decomposition steps."""
    try:
        # Create new history with the current query
        new_history = history + [{"role": "user", "content": query}]
        
        # Show thinking message
        status_msg = "🤔 Thinking..."
        new_history.append({"role": "assistant", "content": status_msg})
        yield new_history
        
        # Decompose query
        status_msg = "🔍 Analyzing query..."
        new_history[-1] = {"role": "assistant", "content": status_msg}
        yield new_history
        
        sub_queries = pipeline.decomposer.decompose_query(query)
        
        # Format sub-queries
        decomposition = "📋 Query Breakdown:\n" + "\n".join(f"{i+1}. {sq}" for i, sq in enumerate(sub_queries))
        status_msg = f"{decomposition}\n\n🔎 Searching documentation..."
        new_history[-1] = {"role": "assistant", "content": status_msg}
        yield new_history
        
        # Generate response
        response = pipeline.process_query(query)
        
        # Format final response
        final_response = f"{decomposition}\n\n📝 Response:\n{response}"
        new_history[-1] = {"role": "assistant", "content": final_response}
        yield new_history
        
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        if not history or history[-1]["role"] != "user":
            new_history = history + [
                {"role": "user", "content": query},
                {"role": "assistant", "content": error_msg}
            ]
        else:
            new_history = history
            new_history.append({"role": "assistant", "content": error_msg})
        yield new_history

# Create a Gradio interface with Pollen Robotics styling
with gr.Blocks(title="Reachy2 Expert Agent", theme=gr.themes.Default(), css=CUSTOM_CSS) as iface:
    with gr.Column(elem_classes=["header-container"]):
        gr.Markdown("""
        # Reachy2 Expert Agent
        """)
        gr.Markdown("""
        Ask questions about controlling and programming the Reachy robot. Our expert agent will:
        1. Break down complex queries into simpler sub-tasks
        2. Search through documentation, tutorials, and code examples
        3. Generate detailed responses with relevant code snippets
        """, elem_classes=["description"])
    
    with gr.Column(elem_classes=["main-container"]):
        # Add a state indicator
        with gr.Row():
            status = gr.Markdown("Ready to answer your questions", elem_classes=["status-text"])
        
        chatbot = gr.Chatbot(
            height=500,
            show_label=False,
            container=True,
            show_copy_button=True,
            type="messages",
            elem_classes=["chatbot"]
        )
        
        with gr.Row(elem_classes=["input-container"]):
            query = gr.Textbox(
                placeholder="Enter your query here (e.g., 'How do I make Reachy wave hello with its right arm?')",
                label="Query",
                scale=9,
                elem_classes=["input-box"]
            )
            submit = gr.Button("Ask", scale=1, variant="primary", elem_classes=["primary-button"])
        
        with gr.Row():
            clear = gr.Button("Clear History", elem_classes=["secondary-button"])
        
        # Example queries organized by category
        with gr.Column(elem_classes=["examples-section"]):
            gr.Markdown("### Example Queries")
            
            with gr.Tabs(elem_classes=["tabs"]):
                with gr.TabItem("Basic Operations", elem_classes=["tab-nav"]):
                    gr.Examples(
                        examples=[
                            "How do I make Reachy wave hello with its right arm?",
                            "Can you show me how to make Reachy pick up an object from the table?",
                            "How do I control the mobile base to move forward and turn?",
                        ],
                        inputs=query,
                        label="Basic Movement and Control"
                    )
                
                with gr.TabItem("Setup & Maintenance", elem_classes=["tab-nav"]):
                    gr.Examples(
                        examples=[
                            "What's the process to calibrate Reachy's arms?",
                            "How can I get the current positions of all joints?",
                            "What's the proper way to handle errors when controlling Reachy?",
                            "What safety measures should I consider when operating Reachy?",
                        ],
                        inputs=query,
                        label="Setup and Safety"
                    )
                
                with gr.TabItem("Advanced Features", elem_classes=["tab-nav"]):
                    gr.Examples(
                        examples=[
                            "Show me how to control Reachy's gripper to grasp objects",
                            "How do I use Reachy's cameras to detect objects?",
                            "How can I make Reachy perform a sequence of movements?",
                        ],
                        inputs=query,
                        label="Advanced Functionality"
                    )
    
    # Event handlers
    submit_click = submit.click(
        fn=lambda: "🔄 Processing...",
        outputs=status,
        queue=False
    ).then(
        process_query,
        inputs=[query, chatbot],
        outputs=chatbot
    ).then(
        fn=lambda: "💡 Ready for your next question!",
        outputs=status,
        queue=False
    )
    
    txt_submit = query.submit(
        fn=lambda: "🔄 Processing...",
        outputs=status,
        queue=False
    ).then(
        process_query,
        inputs=[query, chatbot],
        outputs=chatbot
    ).then(
        fn=lambda: "💡 Ready for your next question!",
        outputs=status,
        queue=False
    )
    
    # Clear button handlers
    def clear_all():
        return None, "", "💡 Ready for your next question!"
    
    clear.click(
        clear_all,
        outputs=[chatbot, query, status],
        queue=False
    )

if __name__ == '__main__':
    print("Starting Reachy2 Expert Agent Chatbot...")
    print(f"Debug mode: {config.debug}")
    iface.queue()
    iface.launch(share=False) 