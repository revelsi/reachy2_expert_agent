# Reachy 2 Project Roadmap

## Overview
This project aims to build an app that generates code for the humanoid robot Reachy 2 using natural language instructions. The app is divided into three main modules:

- **RAG Pipeline:** Retrieves relevant information (API documentation, code examples, etc.) using a retrieval augmented generation (RAG) approach with LangChain and ChromaDB.
- **LLM-based Chatbot:** Processes natural language instructions and generates reliable code using an open-source language model for code generation.
- **User Interface:** Provides a simple and efficient interface (using Gradio) to interact with the system.


## Project Phases

### Phase 1: Core Development
- Prepare relevant documentation and code examples for ingestion.
- Develop the RAG pipeline (`rag_pipeline.py`) using LangChain, text splitting, and ChromaDB for vector storage.
- Build the LLM-based chatbot (`chatbot.py`) that wraps an open-source code generation model with a retrieval-based approach.

### Phase 2: UI Integration
- Develop a Gradio-based UI (`ui.py`) to allow user input and display generated code.
- Integrate the RAG pipeline and chatbot with the UI for real-time interaction.

### Phase 3: Extended Knowledge Base
- Expand the knowledge base to include FAQs, Q&A, extended API documentation, and robot descriptions.
- Enhance the retrieval capability to support more diverse queries and detailed robot information.

## Additional Considerations
- **Model Selection & Fine-Tuning:** Consider experimenting with or fine-tuning different open-source models to optimize code generation reliability.
- **Testing & Evaluation:** Implement thorough testing with various natural language inputs to ensure the system retrieves relevant context and generates accurate code.
- **Error Handling & Security:** Incorporate robust error handling measures and possibly implement a sandbox environment for safe code execution.

## Summary
This roadmap provides a clear path from developing the core capabilities (RAG pipeline, chatbot, UI) to eventually extending the system with a more comprehensive knowledge base to support a wide range of user queries and instructions. 