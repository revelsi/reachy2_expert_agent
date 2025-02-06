# Reachy2 Expert Agent

A retrieval-based expert system for Reachy2 robot documentation and code examples, featuring an interactive chatbot interface.

## Overview

This system creates and maintains a semantic search index over Reachy2's documentation, tutorials, and SDK examples. It uses a sophisticated RAG (Retrieval-Augmented Generation) pipeline with query decomposition and the InstructorXL model for generating embeddings.

## Features

- Interactive chatbot interface with real-time feedback
- Query decomposition for complex robot control questions
- Multi-collection semantic search with collection-specific instructions
- Enhanced document chunking strategies for different content types
- Comprehensive evaluation metrics and testing suite

## Pipeline Structure

1. **Query Processing**
   - Query decomposition into actionable sub-tasks
   - Collection-specific instruction enhancement
   - Real-time progress feedback

2. **Document Retrieval**
   - Multi-collection semantic search
   - Collection-specific weighting
   - Enhanced context preservation
   - Efficient ChromaDB integration

3. **Response Generation**
   - Context-aware response synthesis
   - Code snippet generation
   - Error handling and timeout protection
   - Progress indication

## Installation

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Add your OpenAI API key
   - Configure debug settings if needed

## Usage

### Running the Chatbot
```bash
python scripts/chatbot.py
```

The chatbot interface provides:
- Real-time query processing feedback
- Example queries by category
- Code snippet copying
- Chat history management

### Pipeline Testing
```bash
# Test the complete RAG pipeline
python scripts/test_rag_pipeline.py

# Test query decomposition
python scripts/test_query_decomposition.py

# Evaluate retrieval performance
python scripts/evaluate_retrieval.py
```

### Document Processing
```bash
# Process new documents
python scripts/chunk_documents.py

# Update vector database
python scripts/update_vectordb.py
```

## Directory Structure

```
.
├── scripts/
│   ├── chatbot.py              # Interactive chatbot interface
│   ├── chunk_documents.py      # Document processing
│   ├── test_rag_pipeline.py    # Pipeline testing
│   ├── update_vectordb.py      # Vector store management
│   └── evaluate_retrieval.py   # Performance evaluation
├── utils/
│   ├── rag_utils.py           # Core RAG pipeline components
│   ├── db_utils.py            # Vector store utilities
│   ├── embedding_utils.py      # Embedding generation
│   └── config.py              # Configuration management
├── external_docs/             # Processed documents
├── vectorstore/              # ChromaDB storage
└── requirements.txt
```

## Configuration

The system uses a hierarchical configuration system:
- Environment variables (via `.env`)
- Model configurations (in `utils/config.py`)
- RAG pipeline settings
- Collection-specific weights and instructions

## Contributing

1. Fork the repository
2. Create a feature branch
3. Run the test suite before submitting changes:
```bash
python scripts/test_rag_pipeline.py
python scripts/evaluate_retrieval.py
```
4. Submit a pull request

## License

This project is licensed under the Apache License, Version 2.0 - see the [LICENSE](LICENSE) file for details.

```
Copyright 2024 Pollen Robotics

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

## Contact

For more information, please contact the project maintainers.

## Project Status

For detailed information about current progress and planned improvements, see [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md).