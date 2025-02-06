import os
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import Optional

# Load environment variables from .env file
load_dotenv()

@dataclass
class ModelConfig:
    """Configuration for language models."""
    # Query decomposition model (lighter weight)
    QUERY_MODEL: str = "gpt-3.5-turbo"
    QUERY_MODEL_TEMP: float = 0.3
    QUERY_MAX_TOKENS: int = 300
    
    # Code generation model (more powerful)
    CODE_MODEL: str = "gpt-4"
    CODE_MODEL_TEMP: float = 0.7
    CODE_MAX_TOKENS: int = 1000
    
    # Re-ranking model
    RERANK_MODEL: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

@dataclass
class RAGConfig:
    """Configuration for RAG pipeline."""
    # Vector store settings
    VECTOR_STORE_DIR: str = "vectorstore"
    
    # Retrieval settings
    TOP_K_CHUNKS: int = 5
    RERANK_TOP_K: int = 3
    
    # Collection weights for different query types
    COLLECTION_WEIGHTS = {
        "code": {
            "api_docs_functions": 1.0,    # Function signatures and usage (primary source)
            "api_docs_classes": 0.9,      # Class structure and methods
            "reachy2_sdk": 0.9,          # Implementation details
            "reachy2_tutorials": 0.8     # Complete working examples
        },
        "concept": {
            "api_docs_classes": 1.0,      # Architecture and design (primary source)
            "reachy2_tutorials": 0.9,     # High-level explanations
            "reachy2_sdk": 0.9,          # Implementation context
            "api_docs_functions": 0.8     # Specific details
        },
        "error": {
            "api_docs_classes": 1.0,      # Error class definitions (primary source)
            "api_docs_functions": 0.9,    # Error-related methods
            "reachy2_sdk": 0.9,          # Error handling examples
            "reachy2_tutorials": 0.8      # Error scenarios
        },
        "setup": {
            "api_docs_classes": 1.0,      # Component initialization (primary source)
            "reachy2_sdk": 0.9,          # Configuration details
            "api_docs_functions": 0.9,    # Setup methods
            "reachy2_tutorials": 0.8      # Setup guides
        },
        "default": {
            "api_docs_functions": 1.0,    # API reference is the primary source
            "api_docs_classes": 0.9,      # Class documentation
            "reachy2_sdk": 0.9,          # SDK implementation
            "reachy2_tutorials": 0.8      # Usage examples
        }
    }
    
    # Query type detection keywords
    QUERY_KEYWORDS = {
        "code": [
            "how to", "example", "implement", "code", "function",
            "method", "call", "use", "write", "program"
        ],
        "concept": [
            "what is", "explain", "understand", "concept", "architecture",
            "design", "overview", "describe", "definition", "mean"
        ],
        "error": [
            "error", "exception", "fail", "issue", "bug", "problem",
            "wrong", "fix", "debug", "handle", "catch"
        ],
        "setup": [
            "setup", "install", "configure", "initialization", "start",
            "calibrate", "prepare", "connect", "setting", "configuration"
        ]
    }

class Config:
    """Main configuration class."""
    def __init__(self):
        # API keys (from environment variables)
        self.openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        # Model configurations
        self.model_config = ModelConfig()
        
        # RAG configurations
        self.rag_config = RAGConfig()
        
        # Debug mode
        self.debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    def validate(self) -> bool:
        """Validate the configuration."""
        if not self.openai_api_key:
            return False
        return True

# Create a global config instance
config = Config() 