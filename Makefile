.PHONY: refresh clean update_vectordb

clean:
	@echo "Cleaning external_docs directory..."
	rm -rf external_docs/*
	mkdir -p external_docs/Codebase

update_vectordb:
	@echo "Updating vector database..."
	python scripts/update_vectordb.py

refresh: clean
	@echo "Refreshing notebooks..."
	python scripts/scrape_notebooks.py
	@echo "Refreshing Reachy2 SDK files..."
	python scripts/scrape_reachy2sdk.py
	@echo "Refreshing API docs..."
	python scripts/scrape_api_docs.py
	@echo "Updating vector database..."
	make update_vectordb
	@echo "Refresh complete."