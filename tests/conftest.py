"""Pytest configuration file for Reachy2 Expert Agent tests."""

import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from src.utils.embedding_utils import EmbeddingGenerator
from src.utils.rag_utils import QueryDecomposer, RAGPipeline


@pytest.fixture
def test_data_dir():
    """Return the path to the test data directory."""
    return os.path.join(os.path.dirname(__file__), "data")


@pytest.fixture
def sample_query():
    """Return a sample query for testing."""
    return "How to move Reachy's right arm?"


@pytest.fixture
def sample_context():
    """Return sample context documents for testing."""
    return [
        "Example of moving Reachy's right arm using position control",
        "Documentation about arm movement safety guidelines",
        "Tutorial on basic arm movements",
    ]


@pytest.fixture
def model_name():
    """Fixture providing the default model name for embeddings."""
    return "hkunlp/instructor-base"


@pytest.fixture
def test_texts():
    """Fixture providing test texts for embedding generation."""
    return [
        "This is a test sentence about robotics and automation.",
        "Another example discussing robot control systems.",
        "Documentation about mechanical components and sensors.",
        "Information about robot programming and interfaces.",
        "Details about robot kinematics and motion planning.",
    ]


@pytest.fixture
def decomposer():
    """Fixture providing a QueryDecomposer instance."""
    return QueryDecomposer()


@pytest.fixture
def query():
    """Fixture providing a test query."""
    return "Wave hello with Reachy's right arm"


@pytest.fixture
def pipeline():
    """Fixture providing a RAGPipeline instance."""
    return RAGPipeline()
