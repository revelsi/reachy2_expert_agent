.PHONY: clean scrape chunk update-db refresh test evaluate help lint format docs venv install-dev

# Default target
help:
	@echo "Available commands:"
	@echo "  make clean      - Remove all generated files"
	@echo "  make scrape     - Scrape documentation (excluding reachy2_docs)"
	@echo "  make scrape-full- Scrape all documentation including reachy2_docs"
	@echo "  make chunk      - Process documents into chunks"
	@echo "  make update-db  - Update vector database with chunked documents"
	@echo "  make refresh    - Clean, scrape, chunk, and update database"
	@echo "  make test       - Run test suite"
	@echo "  make evaluate   - Run evaluation metrics"
	@echo "  make lint       - Run code quality checks"
	@echo "  make format     - Format code using black and isort"
	@echo "  make docs       - Generate documentation"
	@echo "  make venv       - Set up virtual environment"
	@echo "  make install-dev- Install package in development mode"

# Clean generated files
clean:
	rm -rf data/raw_docs/*
	rm -rf data/external_docs/*
	rm -rf data/vectorstore/*
	@echo "Cleaned generated files"

# Scrape documentation (excluding reachy2_docs)
scrape:
	python tools/scrape_sdk_docs.py
	python tools/scrape_vision_docs.py
	python tools/scrape_tutorials.py
	@echo "Documentation scraping complete (reachy2_docs excluded)"

# Optional full scrape including reachy2_docs (if needed)
scrape-full:
	python tools/scrape_sdk_docs.py
	python tools/scrape_vision_docs.py
	python tools/scrape_tutorials.py
	python tools/scrape_reachy2_docs.py
	@echo "Full documentation scraping complete"

# Process documents into chunks
chunk:
	python tools/chunk_documents.py
	@echo "Document chunking complete"

# Update vector database
update-db:
	python tools/update_vectordb.py
	@echo "Vector database update complete"

# Clean and rebuild everything (excluding reachy2_docs)
refresh: clean scrape chunk update-db
	@echo "Refresh complete (reachy2_docs excluded)"

# Full refresh including reachy2_docs
refresh-full: clean scrape-full chunk update-db
	@echo "Full refresh complete"

# Run tests
test:
	@echo "Running test suite..."
	pytest tests/
	@echo "Tests complete"

# Run evaluation
evaluate:
	python tools/evaluate_retrieval.py
	@echo "Evaluation complete"

# Create necessary directories
init:
	mkdir -p data/raw_docs
	mkdir -p data/external_docs
	mkdir -p data/vectorstore
	mkdir -p data/cache
	touch data/raw_docs/.gitkeep
	touch data/external_docs/.gitkeep
	touch data/vectorstore/.gitkeep
	touch data/cache/.gitkeep
	@echo "Initialized directory structure"

# Code quality
lint:
	flake8 src/ tests/ tools/
	mypy src/ tests/ tools/
	@echo "Lint checks complete"

# Code formatting
format:
	black src/ tests/ tools/
	isort src/ tests/ tools/
	@echo "Code formatting complete"

# Documentation generation
docs:
	mkdocs build
	@echo "Documentation generated"

# Virtual environment setup
venv:
	python -m venv venv
	@echo "To activate virtual environment:"
	@echo "  source venv/bin/activate  # Unix/macOS"
	@echo "  .\\venv\\Scripts\\activate  # Windows"
	@echo "Then install dependencies:"
	@echo "  pip install -r requirements.txt"

# Install in development mode
install-dev:
	pip install -e .