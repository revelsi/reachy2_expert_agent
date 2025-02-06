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

# Create a Gradio interface
with gr.Blocks(title="Reachy2 Expert Agent", theme=gr.themes.Soft()) as iface:
    gr.Markdown("""
    # 🤖 Reachy2 Expert Agent
    Ask questions about controlling and programming the Reachy robot. The agent will:
    1. Break down complex queries into simpler sub-tasks
    2. Search through documentation, tutorials, and code examples
    3. Generate detailed responses with relevant code snippets
    """)
    
    # Add a state indicator
    with gr.Row():
        status = gr.Markdown("💡 Ready to answer your questions!")
    
    chatbot = gr.Chatbot(
        height=500,
        show_label=False,
        container=True,
        show_copy_button=True,
        type="messages"
    )
    
    with gr.Row():
        query = gr.Textbox(
            placeholder="Enter your query here (e.g., 'How do I make Reachy wave hello with its right arm?')",
            label="Query",
            scale=9
        )
        submit = gr.Button("🚀 Ask", scale=1, variant="primary")
    
    with gr.Row():
        clear = gr.Button("🗑️ Clear History")
    
    # Example queries organized by category
    gr.Markdown("### 📚 Example Queries")
    
    with gr.Tabs():
        with gr.TabItem("🔰 Basic Operations"):
            gr.Examples(
                examples=[
                    "How do I make Reachy wave hello with its right arm?",
                    "Can you show me how to make Reachy pick up an object from the table?",
                    "How do I control the mobile base to move forward and turn?",
                ],
                inputs=query,
                label="Basic Movement and Control"
            )
        
        with gr.TabItem("⚙️ Setup & Maintenance"):
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
        
        with gr.TabItem("🔧 Advanced Features"):
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
    def set_status(status_text: str):
        return status_text

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