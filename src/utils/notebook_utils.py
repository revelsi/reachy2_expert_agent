import json

from langchain.docstore.document import Document


def process_notebook(notebook_path, source_file):
    """
    Process a Jupyter notebook into meaningful chunks.
    Returns a list of Document objects.
    """
    with open(notebook_path, "r", encoding="utf-8") as f:
        nb = json.load(f)

    documents = []
    cell_number = 0
    current_section = "Start of Notebook"

    for cell in nb["cells"]:
        cell_number += 1
        cell_type = cell["cell_type"]
        source = "".join(cell["source"])

        if cell_type == "markdown":
            # Update current section if this is a header
            if source.startswith("#"):
                current_section = source.split("\n")[0].lstrip("#").strip()

            # Create document for markdown content
            if len(source.strip()) > 0:
                documents.append(
                    Document(
                        page_content=source,
                        metadata={
                            "source": source_file,
                            "type": "notebook_markdown",
                            "cell_number": cell_number,
                            "section": current_section,
                        },
                    )
                )

        elif cell_type == "code":
            # Skip empty code cells
            if len(source.strip()) == 0:
                continue

            # Create document for code content
            documents.append(
                Document(
                    page_content=source,
                    metadata={
                        "source": source_file,
                        "type": "notebook_code",
                        "cell_number": cell_number,
                        "section": current_section,
                    },
                )
            )

    return documents
