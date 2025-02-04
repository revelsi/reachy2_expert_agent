import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import requests
from bs4 import BeautifulSoup
from langchain.docstore.document import Document
from utils.doc_utils import save_documents_to_json

def fetch_reachy_sdk_api(url):
    """
    Fetch the ReachySDK API documentation page and return its useful textual content.
    It focuses on the structure: body -> main -> section.
    For each <section>, it extracts the h1 (header/title) and then for each <div> within the section,
    creates a separate chunk (with the header prepended if available).
    It excludes any unwanted elements such as labels or anchors with "view source".
    Returns a list of strings, each representing a chunk.
    """
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        # Locate the main container.
        main_content = soup.find('main')
        if not main_content:
            raise Exception("No <main> tag found in the page")
        
        # Remove unwanted elements from the main container.
        for label in main_content.find_all('label', class_="view-source-button"):
            label.decompose()
        for a in main_content.find_all('a'):
            if "view source" in a.get_text(strip=True).lower():
                a.decompose()
        # Additionally remove any elements with the class 'pdoc-code codehilite'
        for elem in main_content.select(".pdoc-code.codehilite"):
            elem.decompose()
        
        # Extract sections within the main tag.
        sections = main_content.find_all('section')
        chunk_texts = []
        for sec in sections:
            header_elem = sec.find('h1')
            header_text = header_elem.get_text(strip=True) if header_elem else ""
            
            # Get each div in the section as a separate chunk.
            div_elements = sec.find_all('div')
            for div in div_elements:
                div_text = div.get_text(separator="\n", strip=True)
                if not div_text:
                    continue
                if header_text:
                    combined_text = header_text + "\n" + div_text
                else:
                    combined_text = div_text
                # Optionally, filter out any lines that mention "view source"
                filtered_lines = [line for line in combined_text.splitlines() if "view source" not in line.lower()]
                combined_text = "\n".join(filtered_lines)
                chunk_texts.append(combined_text)
        return chunk_texts
    else:
        raise Exception(f"Error fetching page: {response.status_code}")

def custom_chunk_text(text, max_chunk=1500, overlap=300):
    """
    Splits the text into chunks by leveraging boundaries where there's a 
    class or function definition (lines starting with "class " or "def ").
    Ensures each chunk is no longer than max_chunk characters, applying an overlap.
    
    This approach helps in preserving complete API definitions including names,
    parameters, description and code blocks.
    """
    import re
    boundaries = list(re.finditer(r'\n(class |def )', text))
    
    if not boundaries:
        return [text[i: i + max_chunk] for i in range(0, len(text), max_chunk - overlap)]
    
    chunks = []
    start = 0
    for boundary in boundaries:
        boundary_start = boundary.start()
        while boundary_start - start > max_chunk:
            chunk = text[start: start + max_chunk]
            chunks.append(chunk)
            start += max_chunk - overlap
        if boundary_start - start >= int(0.8 * max_chunk):
            chunk = text[start: boundary_start]
            chunks.append(chunk)
            start = boundary_start - overlap
    if start < len(text):
        chunks.append(text[start:])
    return chunks

def main():
    # List of URLs to scrape
    urls = [
        "https://pollen-robotics.github.io/reachy2-sdk/reachy2_sdk/reachy_sdk.html",
        "https://pollen-robotics.github.io/reachy2-sdk/reachy2_sdk.html"
    ]

    all_documents = []
    for url in urls:
        print(f"Fetching ReachySDK API docs from {url}...", flush=True)
        chunks = fetch_reachy_sdk_api(url)
        print("Fetched API docs and extracted useful chunks (each div).", flush=True)
        print(f"Extracted {len(chunks)} chunk(s).", flush=True)

        # Wrap each chunk as a Document object with source metadata including '@'
        documents = [Document(page_content=chunk, metadata={"source": "@" + url}) for chunk in chunks]
        print(f"Scraped the ReachySDK API docs into {len(documents)} document(s).", flush=True)
        all_documents.extend(documents)

    # For demonstration: print the entire content of each chunk.
    for i, doc in enumerate(all_documents):
        print(f"\n--- Chunk {i + 1} ---", flush=True)
        print(doc.page_content, flush=True)

    output_dir = os.path.join("external_docs", "Codebase")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "api_docs.json")
    save_documents_to_json(all_documents, output_file)
    print(f"Saved {len(all_documents)} API doc chunks to {output_file}", flush=True)

if __name__ == "__main__":
    main()