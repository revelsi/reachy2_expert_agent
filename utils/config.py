import os
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import Optional

# Load environment variables from .env file
load_dotenv()

@dataclass
class ModelConfig:
    """Configuration for language models."""
    # Query decomposition model (Mistral Small)
    QUERY_MODEL: str = "mistral-small-latest"  # Use Mistral Small for query decomposition
    QUERY_MODEL_TEMP: float = 0.3
    QUERY_MAX_TOKENS: int = 300
    
    # Code generation model (Mistral Large)
    CODE_MODEL: str = "mistral-large-latest"  # Use Mistral Large for better code synthesis
    CODE_MODEL_TEMP: float = 0.2  # Lower temperature for more precise code generation
    CODE_MAX_TOKENS: int = 2000  # Increased token limit for complete code examples
    
    # Embedding model
    EMBEDDING_MODEL: str = "hkunlp/instructor-xl"  # Use InstructorXL for embeddings
    
    # Re-ranking model
    RERANK_MODEL: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    
    # Mistral API settings for managed endpoints
    MISTRAL_API_KEY: str = os.getenv("MISTRAL_API_KEY", "")
    QUERY_MODEL_ENDPOINT: str = "https://api.mistral.ai/v1/chat/completions"
    CODE_MODEL_ENDPOINT: str = "https://api.mistral.ai/v1/chat/completions"

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
            "api_docs_modules": 0.7,      # Module-level context
            "reachy2_sdk": 0.9,          # Implementation details
            "vision_examples": 0.8,       # Vision-specific examples
            "reachy2_tutorials": 0.8      # Complete working examples
        },
        "concept": {
            "api_docs_modules": 1.0,      # High-level architecture (primary source)
            "api_docs_classes": 0.9,      # Class structure and design
            "reachy2_tutorials": 0.9,     # High-level explanations
            "reachy2_sdk": 0.8,          # Implementation context
            "vision_examples": 0.8,       # Vision concepts
            "api_docs_functions": 0.7     # Specific details
        },
        "error": {
            "api_docs_classes": 1.0,      # Error class definitions (primary source)
            "api_docs_functions": 0.9,    # Error-related methods
            "api_docs_modules": 0.8,      # Module-level error handling
            "reachy2_sdk": 0.8,          # Error handling examples
            "vision_examples": 0.8,       # Vision-specific errors
            "reachy2_tutorials": 0.7      # Error scenarios
        },
        "setup": {
            "api_docs_modules": 1.0,      # Module setup (primary source)
            "api_docs_classes": 0.9,      # Component initialization
            "reachy2_sdk": 0.9,          # Configuration details
            "vision_examples": 0.9,       # Vision setup
            "api_docs_functions": 0.8,    # Setup methods
            "reachy2_tutorials": 0.8      # Setup guides
        },
        "vision": {
            "vision_examples": 1.0,       # Vision examples (primary source)
            "api_docs_modules": 0.9,      # Vision module documentation
            "api_docs_classes": 0.9,      # Vision classes
            "api_docs_functions": 0.8,    # Vision functions
            "reachy2_tutorials": 0.8,     # Vision tutorials
            "reachy2_sdk": 0.7           # General SDK context
        },
        "default": {
            "api_docs_functions": 1.0,    # API reference is the primary source
            "api_docs_classes": 0.9,      # Class documentation
            "api_docs_modules": 0.9,      # Module documentation
            "reachy2_sdk": 0.8,          # SDK implementation
            "vision_examples": 0.8,       # Vision examples
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
        ],
        "vision": [
            "camera", "vision", "image", "video", "detect", "recognize",
            "see", "view", "capture", "stream", "visual"
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