# Configure logging to reduce verbosity
import logging
logging.getLogger('chromadb').setLevel(logging.ERROR)
logging.getLogger('chromadb.telemetry').setLevel(logging.ERROR)
logging.getLogger('httpx').setLevel(logging.WARNING)  # Suppress Gradio version check
logging.getLogger('gradio').setLevel(logging.WARNING)

import gradio as gr
import sys, os
import time
from typing import Tuple, Generator, List

# Ensure the parent directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.rag_utils import RAGPipeline, detect_query_type
from utils.config import config

class ChatbotInterface:
    def __init__(self):
        # Initialize the RAG pipeline once
        print("Initializing Reachy2 Expert Agent...")
        self.pipeline = RAGPipeline()
        
    def stream_response(self, query: str, history: List[dict]) -> Generator[List[dict], None, None]:
        """Stream the response with reasoning steps and code generation."""
        try:
            start_time = time.time()
            
            # Start with the user's query
            messages = history + [gr.ChatMessage(role="user", content=query)]
            yield messages
            
            # Add initial thinking message with timing
            messages.append(gr.ChatMessage(
                role="assistant",
                content="Let me think about that...",
                metadata={
                    "title": "🤔 Analyzing Query",
                    "status": "pending",
                    "log": "\n".join([
                        "Initializing query analysis...",
                        f"Query length: {len(query)} characters",
                        f"Context: {len(history)} previous messages"
                    ]),
                    "duration": time.time() - start_time
                }
            ))
            yield messages
            
            # Query type detection
            query_type = detect_query_type(query)
            detection_time = time.time() - start_time
            messages[-1] = gr.ChatMessage(
                role="assistant",
                content=f"This appears to be a {query_type} query.",
                metadata={
                    "title": "🔍 Query Analysis",
                    "status": "done",
                    "log": "\n".join([
                        f"Detected query type: {query_type}",
                        f"Analysis completed in {detection_time:.2f}s",
                        "Preparing to search relevant documentation..."
                    ]),
                    "duration": detection_time
                }
            )
            yield messages
            
            # Document retrieval process
            search_start = time.time()
            messages.append(gr.ChatMessage(
                role="assistant",
                content="",
                metadata={
                    "title": "📚 Document Search",
                    "status": "pending",
                    "log": "Initializing document search across collections...",
                    "duration": 0.0
                }
            ))
            yield messages
            
            # Get collection weights
            collection_weights = self.pipeline.get_collection_weights(query)
            
            # Search each collection
            all_results = []
            search_log = []
            collection_display_names = {
                "api_docs_functions": "📘 API Function",
                "api_docs_classes": "📗 API Class",
                "api_docs_modules": "📙 Module",
                "reachy2_sdk": "💻 SDK Example",
                "vision_examples": "👁️ Vision Example",
                "reachy2_tutorials": "📚 Tutorial",
                "reachy2_docs": "📖 Documentation"
            }
            
            for collection, weight in collection_weights.items():
                collection_start = time.time()
                messages[-1] = gr.ChatMessage(
                    role="assistant",
                    content="",
                    metadata={
                        "title": "📚 Document Search",
                        "status": "pending",
                        "log": "\n".join([
                            *search_log,
                            f"Searching {collection_display_names.get(collection, collection)}...",
                            f"Collection weight: {weight:.2f}"
                        ]),
                        "duration": time.time() - search_start
                    }
                )
                yield messages
                
                results = self.pipeline.vector_store.query_collection(
                    collection_name=collection,
                    query_texts=[query],
                    n_results=config.rag_config.TOP_K_CHUNKS,
                    embedding_function=self.pipeline.embedding_generator
                )
                
                documents = results['documents'][0]
                distances = results['distances'][0]
                
                # Store results with their weighted scores
                for doc, dist in zip(documents, distances):
                    doc_with_source = f"[{collection_display_names.get(collection, collection)}] {doc}"
                    all_results.append((doc_with_source, dist * weight))
                    
                collection_time = time.time() - collection_start
                search_log.append(f"✓ Found {len(documents)} matches in {collection_display_names.get(collection, collection)} ({collection_time:.2f}s)")
            
            # Sort and select top results
            all_results.sort(key=lambda x: x[1])
            selected_docs = [doc for doc, _ in all_results[:config.rag_config.TOP_K_CHUNKS]]
            
            search_duration = time.time() - search_start
            messages[-1] = gr.ChatMessage(
                role="assistant",
                content="\n".join(search_log),
                metadata={
                    "title": "📚 Document Search",
                    "status": "done",
                    "log": "\n".join([
                        *search_log,
                        f"Selected top {len(selected_docs)} most relevant documents",
                        f"Total search time: {search_duration:.2f}s"
                    ]),
                    "duration": search_duration
                }
            )
            yield messages
            
            # Code generation process
            generation_start = time.time()
            messages.append(gr.ChatMessage(
                role="assistant",
                content="",
                metadata={
                    "title": "⚙️ Code Generation",
                    "status": "pending",
                    "log": "\n".join([
                        "Analyzing context documents...",
                        f"Processing {len(selected_docs)} relevant sources",
                        "Generating response..."
                    ]),
                    "duration": 0.0
                }
            ))
            yield messages
            
            # Generate final response
            response = self.pipeline.generator.generate_response(
                query=query,
                context=selected_docs,
                query_type=query_type
            )
            
            generation_duration = time.time() - generation_start
            total_duration = time.time() - start_time
            
            # Update the thinking status
            messages[-1] = gr.ChatMessage(
                role="assistant",
                content="Response generated successfully",
                metadata={
                    "title": "⚙️ Code Generation",
                    "status": "done",
                    "log": "\n".join([
                        "Context analysis complete",
                        "Response generated successfully",
                        f"Generation time: {generation_duration:.2f}s",
                        f"Total processing time: {total_duration:.2f}s"
                    ]),
                    "duration": generation_duration
                }
            )
            yield messages
            
            # Add the final response as a separate message without metadata
            messages.append(gr.ChatMessage(
                role="assistant",
                content=response
            ))
            yield messages
            
        except Exception as e:
            error_time = time.time() - start_time
            error_msg = f"Error: {str(e)}"
            error_metadata = {
                "title": "❌ Error",
                "status": "done",
                "log": "\n".join([
                    f"Error occurred: {str(e)}",
                    f"Error occurred after {error_time:.2f}s",
                    "Please try again or rephrase your query"
                ]),
                "duration": error_time
            }
            
            if not history:
                yield [
                    gr.ChatMessage(role="user", content=query),
                    gr.ChatMessage(role="assistant", content=error_msg, metadata=error_metadata)
                ]
            else:
                yield history + [gr.ChatMessage(role="assistant", content=error_msg, metadata=error_metadata)]

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
        - Shows real-time reasoning steps and code generation
        - Maintains conversation context for follow-up questions
        - Ensures safety guidelines are followed
        - Includes necessary code imports and setup
        """)
        
        with gr.Row():
            with gr.Column(scale=2):
                # Main chat interface with message type
                chatbot = gr.Chatbot(
                    height=600,
                    show_label=False,
                    container=True,
                    show_copy_button=True,
                    type="messages"  # Enable metadata support
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
            with gr.TabItem("Basic Movement"):
                gr.Examples(
                    examples=[
                        "Show me code to move Reachy's right arm to a specific position",
                        "How to make Reachy's head track an object?",
                        "Code example for controlling the mobile base movement",
                        "How to get current joint positions and move relative to them?",
                    ],
                    inputs=query,
                    label="Basic Movement Code"
                )
            
            with gr.TabItem("Object Manipulation"):
                gr.Examples(
                    examples=[
                        "Code to control the gripper with force feedback",
                        "Example of pick and place operation with error handling",
                        "How to implement a grasping sequence with position checks",
                        "Code to detect and track objects with the cameras",
                    ],
                    inputs=query,
                    label="Object Manipulation Code"
                )
            
            with gr.TabItem("Error Handling"):
                gr.Examples(
                    examples=[
                        "Show me proper error handling for arm movements",
                        "How to implement safety checks in gripper control",
                        "Code example for handling vision detection failures",
                        "Example of graceful error recovery during motion",
                    ],
                    inputs=query,
                    label="Error Handling Code"
                )
            
            with gr.TabItem("Advanced Control"):
                gr.Examples(
                    examples=[
                        "Code for smooth trajectory generation",
                        "How to implement velocity control for the mobile base",
                        "Example of coordinated arm and head movement",
                        "Code for visual servoing with the cameras",
                    ],
                    inputs=query,
                    label="Advanced Control Code"
                )
            
            with gr.TabItem("Integration"):
                gr.Examples(
                    examples=[
                        "How to combine vision and arm control in one script",
                        "Example of a complete pick-and-place program",
                        "Code to integrate mobile base with arm movements",
                        "How to create a reusable movement sequence",
                    ],
                    inputs=query,
                    label="Integration Examples"
                )
        
        # Event handlers
        submit_click = submit.click(
            fn=lambda: "Processing query...",
            outputs=status,
            queue=False
        ).then(
            chatbot_interface.stream_response,  # Use streaming response
            inputs=[query, chatbot],
            outputs=chatbot
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
            chatbot_interface.stream_response,  # Use streaming response
            inputs=[query, chatbot],
            outputs=chatbot
        ).then(
            fn=lambda: "Ready for your next question!",
            outputs=status,
            queue=False
        )
        
        # Clear button handler
        def clear_chat():
            return None, "", "Ready to assist with your Reachy2 questions!"
            
        clear.click(
            fn=clear_chat,  # Use the clear_chat function instead of lambda
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