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
import requests

# Configure logging to reduce verbosity
logging.getLogger('chromadb').setLevel(logging.ERROR)
logging.getLogger('chromadb.telemetry').setLevel(logging.ERROR)

def detect_query_type(query: str) -> str:
    """Detect the type of query based on keywords."""
    query = query.lower()
    
    # Check each query type's keywords
    for query_type, keywords in config.rag_config.QUERY_KEYWORDS.items():
        if any(keyword in query for keyword in keywords):
            return query_type
    
    return "default"

class QueryDecomposer:
    """Handles breaking down complex queries into sub-queries."""
    
    def __init__(self):
        self.api_key = config.model_config.MISTRAL_API_KEY
        self.endpoint = config.model_config.QUERY_MODEL_ENDPOINT
        self.model = config.model_config.QUERY_MODEL
        self.temperature = config.model_config.QUERY_MODEL_TEMP
        self.max_tokens = config.model_config.QUERY_MAX_TOKENS
        print(f"Using Mistral NeMo for query decomposition with model {self.model}")
    
    def decompose_query(self, query: str) -> List[str]:
        """Break down a complex query into simpler sub-queries."""
        try:
            messages = [
                {
                    "role": "system",
                    "content": "You are a robotics expert assistant specializing in the Reachy robot platform. Your task is to break down complex queries into 3-5 essential, actionable sub-tasks."
                },
                {
                    "role": "user",
                    "content": f"""Break down this robotics query into 3-5 essential sub-tasks, focusing on the most important actions needed.

Key aspects to consider:
- Core functionality (what's the main goal?)
- Required setup or initialization
- Key parameters or configurations
- Safety requirements

Query: {query}

Provide ONLY the 3-5 most important sub-tasks, numbered 1-5. Each sub-task should be clear and actionable."""
                }
            ]
            
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "top_p": 1,
                "stream": False
            }

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            response = requests.post(self.endpoint, json=payload, headers=headers)
            response.raise_for_status()  # Raise an error for bad status codes
            response_json = response.json()
            
            # Handle different possible response formats
            if "choices" in response_json and response_json["choices"]:
                if "message" in response_json["choices"][0]:
                    content = response_json["choices"][0]["message"]["content"].strip()
                elif "text" in response_json["choices"][0]:
                    content = response_json["choices"][0]["text"].strip()
                else:
                    raise ValueError(f"Unexpected response format from Mistral API: {response_json}")
            else:
                raise ValueError(f"No choices found in Mistral API response: {response_json}")
            
            # Parse the response into sub-queries
            sub_queries = [
                line.strip().split('. ', 1)[1] if '. ' in line else line.strip()
                for line in content.split("\n")
                if line.strip() and not line.strip().isspace()
            ]
            
            if not sub_queries:
                raise ValueError("No valid sub-queries found in the response")
            
            return sub_queries
            
        except requests.exceptions.RequestException as e:
            print(f"Error making request to Mistral API: {str(e)}")
            raise
        except (KeyError, ValueError) as e:
            print(f"Error processing Mistral API response: {str(e)}")
            raise
        except Exception as e:
            print(f"Unexpected error during query decomposition: {str(e)}")
            raise

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
    
    QUERY_TYPE_INSTRUCTIONS = {
        "code": "Generate a response that includes relevant code examples and implementation details.",
        "concept": "Explain the concept clearly with relevant technical details and architecture.",
        "error": "Provide error handling guidance and troubleshooting steps.",
        "setup": "Give step-by-step setup or configuration instructions.",
        "vision": "Explain vision-related functionality with camera setup details.",
        "default": "Provide a clear and detailed response with relevant examples."
    }
    
    def __init__(self):
        """Initialize the response generator."""
        self.api_key = config.model_config.MISTRAL_API_KEY
        self.endpoint = config.model_config.CODE_MODEL_ENDPOINT
        self.model = config.model_config.CODE_MODEL
        self.temperature = config.model_config.CODE_MODEL_TEMP
        self.max_tokens = config.model_config.CODE_MAX_TOKENS
    
    def generate_response(self, query: str, context: List[str], query_type: str = "default") -> str:
        """Generate a response based on the query and retrieved context."""
        try:
            # Get type-specific instructions
            type_instructions = self.QUERY_TYPE_INSTRUCTIONS.get(query_type, self.QUERY_TYPE_INSTRUCTIONS["default"])
            
            # Format context
            formatted_context = "\n\n".join(f"Document {i+1}:\n{doc}" for i, doc in enumerate(context))
            
            # Prepare the prompt
            messages = [
                {
                    "role": "system",
                    "content": f"""You are a robotics expert assistant specializing in the Reachy robot platform.
Your task is to generate detailed, accurate responses based on the provided documentation.
{type_instructions}"""
                },
                {
                    "role": "user",
                    "content": f"""Query: {query}

Relevant Documentation:
{formatted_context}

Generate a detailed response that directly answers the query using the provided documentation.
Include relevant code examples when appropriate."""
                }
            ]
            
            # Make API call
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            data = {
                "model": self.model,
                "messages": messages,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens
            }
            
            response = requests.post(self.endpoint, headers=headers, json=data)
            response.raise_for_status()
            
            # Extract and return the response
            result = response.json()
            return result['choices'][0]['message']['content']
            
        except Exception as e:
            print(f"Error generating response: {str(e)}")
            return f"I apologize, but I encountered an error while generating the response: {str(e)}"

class RAGPipeline:
    """Main RAG pipeline that coordinates all components."""
    
    def __init__(self):
        """Initialize pipeline components."""
        self.decomposer = QueryDecomposer()
        self.embedding_generator = EmbeddingGenerator(model_name="hkunlp/instructor-xl")
        print("Using InstructorXL for embeddings")
        self.vector_store = VectorStore()
        self.reranker = ReRanker()
        self.generator = ResponseGenerator()
    
    def get_collection_weights(self, query: str) -> dict:
        """Get collection weights based on query type."""
        query_type = detect_query_type(query)
        return config.rag_config.COLLECTION_WEIGHTS[query_type]
    
    def process_query(self, query: str) -> str:
        """Process a query through the complete RAG pipeline."""
        try:
            # 1. Get query type for context-aware processing
            query_type = detect_query_type(query)
            
            # 2. Get collection weights for this query
            collection_weights = self.get_collection_weights(query)
            
            # 3. Retrieve relevant documents from each collection
            all_results = []
            for collection, weight in collection_weights.items():
                results = self.vector_store.query_collection(
                    collection_name=collection,
                    query_texts=[query],
                    n_results=config.rag_config.TOP_K_CHUNKS,
                    embedding_function=self.embedding_generator.embedding_function
                )
                
                # Weight the results based on collection
                documents = results['documents'][0]
                distances = results['distances'][0]
                
                # Add source collection to metadata
                documents_with_source = [
                    f"[{collection}] {doc}" 
                    for doc in documents
                ]
                
                # Store results with their weighted scores
                for doc, dist in zip(documents_with_source, distances):
                    all_results.append((doc, dist * weight))
            
            # 4. Sort and select top results
            all_results.sort(key=lambda x: x[1])
            selected_docs = [doc for doc, _ in all_results[:config.rag_config.TOP_K_CHUNKS]]
            
            # 5. Generate the final response
            response = self.generator.generate_response(
                query=query,
                context=selected_docs,
                query_type=query_type
            )
            
            return response
            
        except Exception as e:
            print(f"Error processing query: {str(e)}")
            return f"I apologize, but I encountered an error while processing your query: {str(e)}"

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