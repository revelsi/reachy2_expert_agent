.PHONY: clean scrape chunk update-db refresh test evaluate help

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

# Clean generated files
clean:
	rm -rf raw_docs/extracted/*
	rm -rf external_docs/documents/*
	rm -rf vectorstore/*
	@echo "Cleaned generated files"

# Scrape documentation (excluding reachy2_docs)
scrape:
	python scripts/scrape_sdk_docs.py
	python scripts/scrape_vision_docs.py
	python scripts/scrape_tutorials.py
	@echo "Documentation scraping complete (reachy2_docs excluded)"

# Optional full scrape including reachy2_docs (if needed)
scrape-full:
	python scripts/scrape_sdk_docs.py
	python scripts/scrape_vision_docs.py
	python scripts/scrape_tutorials.py
	python scripts/scrape_reachy2_docs.py
	@echo "Full documentation scraping complete"

# Process documents into chunks
chunk:
	python scripts/chunk_documents.py
	@echo "Document chunking complete"

# Update vector database
update-db:
	python scripts/update_vectordb.py
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
	@echo "\nTesting markdown chunking..."
	python scripts/test_markdown_chunking.py
	@echo "\nTesting Reachy 2 documentation..."
	python scripts/test_reachy2_docs.py
	@echo "\nTesting chunk analysis..."
	python scripts/test_chunks.py
	@echo "\nTests complete"

# Run evaluation
evaluate:
	python scripts/evaluate.py
	@echo "Evaluation complete"

# Create necessary directories
init:
	mkdir -p raw_docs/extracted
	mkdir -p external_docs/documents
	mkdir -p vectorstore
	touch raw_docs/extracted/.gitkeep
	touch external_docs/documents/.gitkeep
	touch vectorstore/.gitkeep
	@echo "Initialized directory structure"