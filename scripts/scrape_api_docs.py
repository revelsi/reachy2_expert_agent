import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import requests


def main():
    # List of URLs to fetch raw HTML for API docs
    urls = [
        "https://pollen-robotics.github.io/reachy2-sdk/reachy2_sdk/reachy_sdk.html",
        "https://pollen-robotics.github.io/reachy2-sdk/reachy2_sdk.html"
    ]
    
    output_dir = os.path.join("raw_docs", "api_docs")
    os.makedirs(output_dir, exist_ok=True)
    
    for i, url in enumerate(urls):
        print(f"Fetching raw API docs from {url}...", flush=True)
        response = requests.get(url)
        if response.status_code == 200:
            file_path = os.path.join(output_dir, f"api_doc_{i+1}.html")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(response.text)
            print(f"Saved raw HTML to {file_path}")
        else:
            print(f"Error fetching {url}: status code {response.status_code}")
            

if __name__ == "__main__":
    main()