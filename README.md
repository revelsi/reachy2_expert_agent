# Reachy2 Expert Agent

A retrieval-based expert system for Reachy2 robot documentation and code examples.

## Overview

This system creates and maintains a semantic search index over Reachy2's documentation, tutorials, and SDK examples. It uses a two-stage pipeline for document processing and the InstructorXL model for generating embeddings.

## Pipeline Structure

1. **Scraping Stage**
   - Fetches raw documents from multiple sources:
     * Reachy2 Tutorials (Jupyter notebooks)
     * Reachy2 SDK examples (Python files and notebooks)
     * API documentation (HTML)
   - Raw files are stored in `raw_docs/` directory

2. **Chunking Stage**
   - Processes raw documents using source-specific strategies:
     * Tutorial notebooks: Preserves narrative flow from markdown cells
     * SDK files: Specialized handling for code and documentation
     * API docs: Structured extraction at both class- and function-level
     * Enhanced context preservation for better retrieval
   - Outputs JSON files with LangChain Document objects in `external_docs/documents/`

3. **Vector Database**
   - Uses ChromaDB for storing document embeddings
   - Implements InstructorXL model for high-quality embeddings
   - Collection-specific embedding instructions for improved relevance
   - Supports semantic search across all document collections

4. **Evaluation System**
   - Comprehensive evaluation metrics (Precision@5, Recall@5, MRR, nDCG@5)
   - Test suite with diverse queries covering different robot functionalities
   - Detailed metrics output in both console and file formats
   - Support for semantic matching and relevance grading

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

## Usage

### Complete Pipeline Refresh
To run the complete pipeline (clean → scrape → chunk → update vector store):
```bash
make refresh
```

### Individual Steps
You can also run individual stages:

1. Clean all directories:
```bash
make clean
```

2. Scrape raw documents:
```bash
make scrape
```

3. Process documents into chunks:
```bash
make chunk
```

4. Update vector store:
```bash
make update_vectordb
```

### Testing and Evaluation

1. Run evaluation metrics:
```bash
python scripts/evaluate_retrieval.py --debug
```

2. Test specific queries:
```bash
python scripts/test_queries.py
```

3. Generate detailed metrics report:
```bash
python scripts/evaluate_retrieval.py --output test_metrics.txt
```

## Directory Structure

```
.
├── raw_docs/                  # Raw documents from scraping
│   ├── api_docs/             # Raw HTML files
│   ├── reachy2_tutorials/    # Raw notebook files
│   └── reachy2_sdk/          # Raw Python and notebook files
├── external_docs/
│   └── documents/           # Processed JSON documents
├── scripts/
│   ├── scrape_*.py          # Scraping scripts
│   ├── chunk_documents.py   # Document processing
│   └── evaluate_*.py        # Evaluation scripts
├── utils/                    # Utility modules
├── vectorstore/             # ChromaDB storage
└── requirements.txt
```

## Future Improvements

Planned enhancements include:
- Implementation of two-stage retrieval with re-ranking
- Fine-tuning of embedding models on domain-specific data
- Query expansion and improved semantic matching
- Enhanced evaluation metrics and benchmarking

## Contributing

When modifying the codebase:
1. Each source type (tutorials, SDK, API docs) has its own chunking strategy
2. Changes to chunking strategies should be made in `chunk_documents.py`
3. Run evaluation scripts to ensure retrieval quality
4. Update test queries and metrics as needed

## License

[Add your license information here]

## Contact

For more information, please contact the project maintainers.