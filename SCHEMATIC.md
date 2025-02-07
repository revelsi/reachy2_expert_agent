# Reachy2 Expert Agent - System Architecture

```mermaid
graph TD
    subgraph "User Interface"
        UI[Gradio Interface] --> |Query| QP[Query Processor]
        QP --> |Response| UI
    end

    subgraph "Query Processing"
        QP --> |Input| QD[Query Decomposer]
        QD --> |Sub-queries| QT[Query Type Detector]
        QT --> |Type & Weights| DR[Document Retriever]
    end

    subgraph "Document Retrieval"
        DR --> |Search| VS[(Vector Store)]
        VS --> |Results| RR[Re-Ranker]
        RR --> |Ranked Docs| RG[Response Generator]
    end

    subgraph "Document Processing"
        DS[Doc Scrapers] --> |Raw| DC[Doc Chunker]
        DC --> |Chunks| EP[Embedding Pipeline]
        EP --> |Vectors| VS
    end

    subgraph "Collections"
        VS --> |Contains| C1[api_docs_functions]
        VS --> |Contains| C2[api_docs_classes]
        VS --> |Contains| C3[api_docs_modules]
        VS --> |Contains| C4[reachy2_sdk]
        VS --> |Contains| C5[vision_examples]
        VS --> |Contains| C6[reachy2_tutorials]
    end

    subgraph "Models"
        M1[Mistral-Small] --> |Query Decomposition| QD
        M2[InstructorXL] --> |Embeddings| EP
        M3[Cross-Encoder] --> |Re-ranking| RR
        M4[Mistral-Large] --> |Response Generation| RG
    end
```

## Component Details

### 1. User Interface Layer
- **Gradio Interface**: Web-based chat interface
- **Query Processor**: Manages query flow and response generation
- **Progress Tracking**: Real-time status updates

### 2. Query Processing Layer
- **Query Decomposer**: Breaks down complex queries
- **Query Type Detector**: Identifies query category
- **Collection Weighting**: Dynamic collection importance

### 3. Document Retrieval Layer
- **Vector Store**: ChromaDB-based document storage
- **Re-Ranker**: Cross-encoder based re-ranking
- **Response Generator**: Context-aware response synthesis

### 4. Document Processing Layer
- **Doc Scrapers**: Multi-source documentation collection
- **Doc Chunker**: Semantic document segmentation
- **Embedding Pipeline**: Vector generation and storage

### 5. Collections Layer
- **api_docs_functions**: Function documentation
- **api_docs_classes**: Class documentation
- **api_docs_modules**: Module documentation
- **reachy2_sdk**: SDK examples
- **vision_examples**: Vision system examples
- **reachy2_tutorials**: Tutorial content

### 6. Model Layer
- **Mistral-Small**: Query decomposition
- **InstructorXL**: Document embeddings
- **Cross-Encoder**: Result re-ranking
- **Mistral-Large**: Response generation

## Data Flow

1. **Query Input**
   - User submits query through Gradio interface
   - Query processor initiates pipeline

2. **Query Analysis**
   - Query decomposer breaks down complex queries
   - Query type detector determines category
   - Collection weights are assigned

3. **Document Retrieval**
   - Vector store searches across collections
   - Results are weighted by collection importance
   - Cross-encoder re-ranks results

4. **Response Generation**
   - Context is assembled from top results
   - Response is generated with code examples
   - Response is formatted and returned

5. **Continuous Updates**
   - Documentation is regularly scraped
   - New content is processed and embedded
   - Vector store is updated

## System Requirements

- Python 3.8+
- ChromaDB
- Sufficient storage for vector database
- Required API keys
- Memory for processing large documents 