.PHONY: refresh clean scrape chunk update_vectordb

clean:
	@echo "Cleaning external_docs and raw_docs directories..."
	rm -rf external_docs/* raw_docs/*
	mkdir -p external_docs/documents raw_docs

scrape:
	@echo "Scraping raw documents..."
	python scripts/scrape_notebooks.py
	python scripts/scrape_reachy2sdk.py
	python scripts/scrape_api_docs.py
	@echo "Raw documents scraping complete."

chunk:
	@echo "Chunking raw documents into JSON format..."
	python scripts/chunk_documents.py
	@echo "Document chunking complete."

update_vectordb:
	@echo "Updating vector database..."
	python scripts/update_vectordb.py

refresh: clean scrape chunk update_vectordb
	@echo "Refresh complete."