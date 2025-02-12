import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class ModelConfig:
    """Configuration for language models."""

    # Query decomposition model (Mistral Small)
    QUERY_MODEL: str = (
        "mistral-small-latest"  # Use Mistral Small for query decomposition
    )
    QUERY_MODEL_TEMP: float = 0.3
    QUERY_MAX_TOKENS: int = 300

    # Code generation model (Mistral Large)
    CODE_MODEL: str = (
        "mistral-large-latest"  # Use Mistral Large for better code synthesis
    )
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
    VECTOR_STORE_DIR: str = "data/vectorstore"

    # Retrieval settings
    TOP_K_CHUNKS: int = 5
    RERANK_TOP_K: int = 3

    # Collection weights for different query types
    COLLECTION_WEIGHTS = {
        "code": {
            "api_docs_functions": 1.0,  # Primary source for function implementations
            "api_docs_classes": 0.95,  # Core class documentation
            "reachy2_sdk": 0.9,  # Complete working examples
            "reachy2_tutorials": 0.85,  # Tutorial code examples
            "vision_examples": 0.95,  # Vision-specific code (increased weight for vision queries)
            "api_docs_modules": 0.7,  # Module context
        },
        "default": {
            "api_docs_functions": 1.0,  # Default to prioritizing code
            "api_docs_classes": 0.95,
            "reachy2_sdk": 0.9,
            "reachy2_tutorials": 0.85,
            "vision_examples": 0.95,
            "api_docs_modules": 0.7,
        },
    }

    # Simplified query types focused on code
    QUERY_KEYWORDS = {
        "code": [
            "how to",
            "example",
            "implement",
            "code",
            "function",
            "method",
            "call",
            "use",
            "write",
            "program",
            "script",
            "create",
            "make",
            "control",
            "move",
            "set",
            "get",
        ],
        "default": [],  # All other queries default to code-focused weights
    }


class Config:
    """Main configuration class."""

    def __init__(self):
        # Model configurations
        self.model_config = ModelConfig()

        # RAG configurations
        self.rag_config = RAGConfig()

        # Debug mode
        self.debug: bool = os.getenv("DEBUG", "false").lower() == "true"

    def validate(self) -> bool:
        """Validate the configuration."""
        if not self.model_config.MISTRAL_API_KEY:
            return False
        return True


# Create a global config instance
config = Config()
