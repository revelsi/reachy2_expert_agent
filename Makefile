.PHONY: refresh

refresh:
	@echo "Refreshing notebooks..."
	python scripts/scrape_notebooks.py
	@echo "Refreshing Reachy2 SDK files..."
	python scripts/scrape_reachy2sdk.py
	@echo "Refreshing Pollen Vision files..."
	python scripts/scrape_pollen_vision.py
	@echo "Refresh complete."