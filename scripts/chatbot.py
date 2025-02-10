# Configure logging to reduce verbosity
import logging
logging.getLogger('chromadb').setLevel(logging.ERROR)
logging.getLogger('chromadb.telemetry').setLevel(logging.ERROR)

import gradio as gr
import sys, os
import time
from typing import Tuple, Generator, List

# Ensure the parent directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.rag_utils import RAGPipeline
from utils.config import config

class ChatbotInterface:
    def __init__(self):
        # Initialize the RAG pipeline once
        print("Initializing Reachy2 Expert Agent...")
        self.pipeline = RAGPipeline()
        
    def process_query(self, query: str, history: List[dict]) -> List[dict]:
        """Process a query and return the final response in the correct message format."""
        try:
            # Create new history with the current query
            new_history = history + [{"role": "user", "content": query}]

            # Generate final response
            response = self.pipeline.process_query(query)
            new_history.append({"role": "assistant", "content": response})
            
            return new_history

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            if not history:
                return [
                    {"role": "user", "content": query},
                    {"role": "assistant", "content": error_msg}
                ]
            else:
                return history + [{"role": "assistant", "content": error_msg}]

def main():
    # Create a single instance of the chatbot interface
    chatbot_interface = ChatbotInterface()
    
    # Create a Gradio interface with default theme
    with gr.Blocks(
        title="Reachy2 Expert Agent",
        theme=gr.themes.Soft()  # Using built-in Soft theme for clean look
    ) as iface:
        gr.Markdown("""
        # Reachy2 Expert Agent
        An intelligent assistant for the Reachy2 robot platform that:
        - Provides accurate, context-aware responses about robot control and programming
        - Maintains conversation context for follow-up questions
        - Ensures safety guidelines are followed
        - Includes necessary code imports and setup
        """)
        
        with gr.Row():
            with gr.Column(scale=2):
                # Main chat interface
                chatbot = gr.Chatbot(
                    height=600,
                    show_label=False,
                    container=True,
                    show_copy_button=True,
                    type="messages"  # Using messages type as recommended
                )
                
                with gr.Row():
                    query = gr.Textbox(
                        placeholder="Ask about Reachy2 robot control, programming, or safety guidelines...",
                        label="Query",
                        scale=8
                    )
                    submit = gr.Button("Ask", scale=1, variant="primary")
                    clear = gr.Button("Clear", scale=1)
                
                with gr.Row():
                    status = gr.Markdown("Ready to assist with your Reachy2 questions!")
            
            with gr.Column(scale=1):
                # Safety Guidelines
                gr.Markdown("""### Safety Guidelines""")
                safety_md = gr.Markdown("""
                - Always follow robot safety protocols
                - Start with slow movements
                - Monitor the robot's surroundings
                - Keep emergency stop accessible
                - Test in simulation when possible
                """)
                
                # Context Information
                gr.Markdown("""### Conversation Context""")
                context_info = gr.Markdown("No active conversation")
                
                # Code Memory
                gr.Markdown("""### Code Examples""")
                code_memory = gr.Markdown("No code examples shared yet")
        
        # Example queries organized by category
        gr.Markdown("""### Example Queries""")
        
        with gr.Tabs():
            with gr.TabItem("Basic Operations"):
                gr.Examples(
                    examples=[
                        "How do I make Reachy wave hello with its right arm?",
                        "Can you show me how to make Reachy pick up an object from the table?",
                        "How do I control the mobile base to move forward and turn?",
                    ],
                    inputs=query,
                    label="Basic Movement and Control"
                )
            
            with gr.TabItem("Setup & Safety"):
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
            
            with gr.TabItem("Advanced Features"):
                gr.Examples(
                    examples=[
                        "Show me how to control Reachy's gripper to grasp objects",
                        "How do I use Reachy's cameras to detect objects?",
                        "How can I make Reachy perform a sequence of movements?",
                    ],
                    inputs=query,
                    label="Advanced Functionality"
                )
            
            with gr.TabItem("Follow-up Examples"):
                gr.Examples(
                    examples=[
                        "Can you explain that last code example in more detail?",
                        "What safety considerations should I keep in mind for this movement?",
                        "Could you show a more complex version of that operation?",
                    ],
                    inputs=query,
                    label="Follow-up Questions"
                )
        
        # Event handlers
        def process_query_and_update(user_query, history):
            # Set context info
            context_info.value = "Active conversation with safety context"
            # Process query through chatbot
            return chatbot_interface.process_query(user_query, history)
        
        def update_code_memory(history):
            if history and any("```python" in str(msg) for msg in history[-2:]):
                code_memory.value = "Recent code examples available (click messages to copy)"
        
        def clear_all():
            context_info.value = "No active conversation"
            code_memory.value = "No code examples shared yet"
            return None, "", "Ready to assist with your Reachy2 questions!"
        
        # Connect event handlers
        submit_click = submit.click(
            fn=lambda: "Processing query...",
            outputs=status,
            queue=False
        ).then(
            process_query_and_update,
            inputs=[query, chatbot],
            outputs=[chatbot]
        ).then(
            update_code_memory,
            inputs=[chatbot]
        ).then(
            fn=lambda: "Ready for your next question!",
            outputs=status,
            queue=False
        )
        
        txt_submit = query.submit(
            fn=lambda: "Processing query...",
            outputs=status,
            queue=False
        ).then(
            process_query_and_update,
            inputs=[query, chatbot],
            outputs=[chatbot]
        ).then(
            update_code_memory,
            inputs=[chatbot]
        ).then(
            fn=lambda: "Ready for your next question!",
            outputs=status,
            queue=False
        )
        
        # Clear button handler
        clear.click(
            clear_all,
            outputs=[chatbot, query, status],
            queue=False
        )
        
        return iface

if __name__ == '__main__':
    print("Starting Reachy2 Expert Agent Chatbot...")
    print(f"Debug mode: {config.debug}")
    iface = main()
    iface.queue()
    iface.launch(share=False) 