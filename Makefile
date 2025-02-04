.PHONY: refresh clean

clean:
	@echo "Cleaning external_docs directory..."
	rm -rf external_docs/*
	mkdir -p external_docs/Codebase

refresh: clean
	@echo "Refreshing notebooks..."
	python scripts/scrape_notebooks.py
	@echo "Refreshing Reachy2 SDK files..."
	python scripts/scrape_reachy2sdk.py
	@echo "Refreshing API docs..."
	python scripts/scrape_api_docs.py
	@echo "Refresh complete."