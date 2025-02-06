import os
from typing import List, Dict, Any, Callable
from openai import OpenAI
from .config import config
from .db_utils import VectorStore
from sentence_transformers import CrossEncoder
from .embedding_utils import EmbeddingGenerator
import tempfile
import shutil
import chromadb
import logging

# Configure logging to reduce verbosity
logging.getLogger('chromadb').setLevel(logging.ERROR)
logging.getLogger('chromadb.telemetry').setLevel(logging.ERROR)

class QueryDecomposer:
    """Handles breaking down complex queries into sub-queries."""
    
    def __init__(self):
        # Debug: Print the API key (masked) that we're receiving
        api_key = config.openai_api_key
        if api_key:
            masked_key = f"{api_key[:6]}...{api_key[-4:]}"
            print(f"Loaded API key: {masked_key}")
        else:
            print("No API key loaded!")
            
        self.client = OpenAI(api_key=api_key)
        self.model = config.model_config.QUERY_MODEL
        self.temperature = config.model_config.QUERY_MODEL_TEMP
        self.max_tokens = config.model_config.QUERY_MAX_TOKENS
    
    def decompose_query(self, query: str) -> List[str]:
        """Break down a complex query into simpler sub-queries."""
        prompt = f"""Break down the following query about robot control into simple, atomic sub-queries.
        Focus on identifying specific actions, parameters, or information needed.
        For example, a complex query might be broken down into movement commands, arm control, etc.
        
        Query: {query}
        
        Return the sub-queries as a numbered list, with each sub-query on a new line.
        Each sub-query should be focused on a single action or piece of information.
        """
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        
        # Parse the response into a list of sub-queries
        content = response.choices[0].message.content.strip()
        sub_queries = [
            line.strip().split('. ', 1)[1] if '. ' in line else line.strip()
            for line in content.split('\n')
            if line.strip() and not line.strip().isspace()
        ]
        
        return sub_queries

class ReRanker:
    """Handles re-ranking of retrieved documents using a cross-encoder."""
    
    def __init__(self):
        self.model = CrossEncoder(config.model_config.RERANK_MODEL)
        self.top_k = config.rag_config.RERANK_TOP_K
    
    def rerank(self, query: str, documents: List[str], scores: List[float]) -> List[tuple]:
        """Re-rank documents using the cross-encoder model."""
        # Create query-document pairs for scoring
        pairs = [[query, doc] for doc in documents]
        
        # Get cross-encoder scores
        cross_scores = self.model.predict(pairs)
        
        # Combine with original scores and sort
        doc_scores = [(doc, cross_score * 0.7 + orig_score * 0.3)
                     for doc, cross_score, orig_score 
                     in zip(documents, cross_scores, scores)]
        
        # Sort by combined score and return top k
        reranked = sorted(doc_scores, key=lambda x: x[1], reverse=True)
        return reranked[:self.top_k]

class ResponseGenerator:
    """Generates final responses including code snippets."""
    
    def __init__(self):
        self.client = OpenAI(api_key=config.openai_api_key)
        self.model = config.model_config.CODE_MODEL
        self.temperature = config.model_config.CODE_MODEL_TEMP
        self.max_tokens = config.model_config.CODE_MAX_TOKENS
    
    def generate_response(self, query: str, context: List[str]) -> str:
        """Generate a response based on the query and retrieved context."""
        # Combine context with appropriate formatting
        formatted_context = "\n\n".join(
            f"Document {i+1}:\n{doc}" for i, doc in enumerate(context)
        )
        
        prompt = f"""You are a specialized robot programming assistant. Your task is to answer questions about the Reachy robot using ONLY the provided documentation context. 
        DO NOT use any knowledge outside of the given context.
        
        If the context doesn't contain enough information to fully answer the query, acknowledge this limitation in your response.
        
        When providing code examples:
        1. Only include code patterns that are explicitly shown in the context
        2. Explain each part of the code using information from the context
        3. If you need to make assumptions, clearly state them
        
        Query: {query}
        
        Documentation Context:
        {formatted_context}
        
        Generate a response that:
        1. Only uses information from the provided context
        2. Includes relevant code examples if shown in the context
        3. Explains any limitations or assumptions
        """
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        
        return response.choices[0].message.content.strip()

class RAGPipeline:
    """Main RAG pipeline that coordinates all components."""
    
    def __init__(self):
        self.decomposer = QueryDecomposer()
        self.embedding_generator = EmbeddingGenerator(model_name="hkunlp/instructor-xl")
        self.vector_store = VectorStore()
        self.reranker = ReRanker()
        self.generator = ResponseGenerator()
    
    def process_query(self, query: str) -> str:
        """Process a query through the complete RAG pipeline."""
        # 1. Decompose query into sub-queries
        sub_queries = self.decomposer.decompose_query(query)
        
        # 2. Retrieve relevant documents for each sub-query
        all_results = []
        for sub_query in sub_queries:
            for collection in config.rag_config.COLLECTION_WEIGHTS.keys():
                results = self.vector_store.query_collection(
                    collection_name=collection,
                    query_texts=[sub_query],
                    n_results=config.rag_config.TOP_K_CHUNKS,
                    embedding_function=self.embedding_generator.embedding_function
                )
                
                # Weight the results based on collection
                weight = config.rag_config.COLLECTION_WEIGHTS[collection]
                weighted_scores = [
                    score * weight 
                    for score in results['distances'][0]
                ]
                
                all_results.extend(list(zip(
                    results['documents'][0],
                    weighted_scores
                )))
        
        # 3. Re-rank combined results
        if all_results:
            docs, scores = zip(*all_results)
            reranked_results = self.reranker.rerank(query, list(docs), list(scores))
            context = [doc for doc, _ in reranked_results]
        else:
            context = []
        
        # 4. Generate final response
        response = self.generator.generate_response(query, context)
        
        return response 

class VectorStore:
    """Vector store wrapper for document storage and retrieval."""
    
    # Collection-specific search instructions for better embeddings
    COLLECTION_INSTRUCTIONS = {
        "api_docs_functions": "Represent this function documentation for retrieving relevant Python API methods and functions",
        "api_docs_classes": "Represent this class documentation for retrieving relevant Python classes and their capabilities",
        "reachy2_tutorials": "Represent this tutorial content for retrieving relevant robot programming examples and explanations",
        "reachy2_sdk": "Represent this SDK documentation for retrieving relevant robot control and programming information"
    }

    def __init__(self, persist_directory: str = "vectorstore"):
        """Initialize the vector store with persistence."""
        self.persist_directory = persist_directory
        
        # Create a temporary directory for the database
        self.temp_dir = tempfile.mkdtemp()
        print(f"Using temporary directory: {self.temp_dir}")
        
        # Initialize client with temporary directory and settings to reduce output
        settings = chromadb.Settings(
            anonymized_telemetry=False,
            allow_reset=True,
            is_persistent=True
        )
        
        self.client = chromadb.PersistentClient(
            path=self.temp_dir,
            settings=settings
        )
        
        # If the persist directory exists, try to copy its contents
        if os.path.exists(persist_directory):
            try:
                shutil.copytree(persist_directory, self.temp_dir, dirs_exist_ok=True)
                print(f"Copied existing database from {persist_directory}")
            except Exception as e:
                print(f"Warning: Could not copy existing database: {e}")

    def query_collection(self, collection_name: str, query_texts: List[str], 
                        n_results: int = 5, embedding_function: Callable = None) -> Dict:
        """Query a collection with collection-specific embedding instructions."""
        collection = self.client.get_collection(
            name=collection_name,
            embedding_function=embedding_function
        )
        
        # Add collection-specific instruction to query
        instruction = self.COLLECTION_INSTRUCTIONS.get(collection_name, "")
        if instruction:
            query_texts = [f"{instruction}:\n{text}" for text in query_texts]
        
        # Only include necessary data in the query
        return collection.query(
            query_texts=query_texts,
            n_results=n_results,
            include=['documents', 'distances']
        ) 