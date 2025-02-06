# Reachy2 Expert Agent - Project Overview

## Overall Project Objectives

- Build a robust Retrieval-Augmented Generation (RAG) system for Reachy2 robot documentation and code examples.
- Enhance semantic retrieval by leveraging collection-specific instructions and advanced chunking techniques.
- Develop advanced query handling, including decomposition of complex queries (e.g., 'wave hello with its right arm') into actionable sub-queries.
- Integrate a two-stage retrieval process with re-ranking to boost relevance and precision in search results.
- Implement a final synthesis and code generation step to produce coherent answers, potentially including executable code for robot control.
- Optimize for cost, resource usage, and latency while maintaining high retrieval and synthesis quality.

## Current Progress

### Completed Tasks

- **Document Processing & Retrieval:**
  - Implemented enhanced chunking strategies for API docs, tutorials, and SDK files.
  - Added improved text cleaning with whitespace normalization.
  - Integrated a vector store (ChromaDB) with collection-specific embedding instructions using the InstructorXL model.
  - Developed a basic chatbot interface for testing retrieval.

- **Evaluation System:**
  - Developed evaluation metrics (Precision@5, Recall@5, MRR, nDCG@5).
  - Created a test suite with diverse queries and detailed metrics export.
  - Added comprehensive testing for chunking functionality.
  - Implemented enhanced metrics tracking and analysis.

- **Infrastructure & Documentation:**
  - Updated documentation (README, .gitignore, and others) to reflect recent changes.
  - Established project tracking and roadmap documents.

### Ongoing & Upcoming Tasks

- **Advanced Query Handling:**
  - Implement a query decomposition module to break down complex queries into sub-queries (e.g., decomposing 'wave hello with its right arm' into actionable steps like 'raise right arm', 'rotate shoulder', etc.).
  - Evaluate lightweight LLM candidates (e.g., GPT-3.5 Turbo, LLaMA-2 7B, T5-base) for cost-effective query decomposition.

- **Tailored Retrieval Enhancements:**
  - Adapt the current retrieval process to handle multiple sub-queries from the decomposition step.
  - Implement an aggregation layer and optional re-ranking using a cross-encoder (e.g., cross-encoder/ms-marco-MiniLM-L-6-v2) to improve result precision.

- **Final Synthesis and Code Generation:**
  - Develop a synthesis component that aggregates re-ranked results and generates final responses or code snippets. Consider candidates such as GPT-4, StarCoder, or Code Llama.

- **Cost & Latency Analysis:**
  - Benchmark the multi-step pipeline (query decomposition, retrieval, re-ranking, synthesis) to analyze performance, cost per query, and end-to-end latency.

- **Integration and Testing:**
  - Integrate these advanced retrieval and synthesis components into the existing RAG pipeline.
  - Conduct thorough testing with sample queries and refine parameters based on real-world performance.

## Next Steps

1. **Implement Query Decomposition:**
   - Develop and test a module that uses a lightweight LLM to break down complex queries into sub-queries.

2. **Enhance Retrieval Process:**
   - Modify the vector store retrieval to handle multiple sub-queries and aggregate results.
   - Integrate a re-ranking mechanism to improve relevance of the final aggregated results.

3. **Develop Final Synthesis Module:**
   - Build a synthesis step that takes aggregated outputs and generates a final response or executable code.

4. **Benchmark and Optimize:**
   - Measure cost and latency using different model candidates (e.g., GPT-3.5 Turbo vs. GPT-4) and refine the pipeline accordingly.

5. **Update Documentation:**
   - Continuously update this project overview as new tasks and progress are made. 