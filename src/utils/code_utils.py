import ast

from langchain.docstore.document import Document


class CodeVisitor(ast.NodeVisitor):
    def __init__(self, source_code, source_file):
        self.source_code = source_code
        self.source_file = source_file
        self.documents = []
        self.current_class = None

    def visit_ClassDef(self, node):
        # Store the current class context
        old_class = self.current_class
        self.current_class = node.name

        # Extract class docstring
        docstring = ast.get_docstring(node)
        if docstring:
            self.documents.append(
                Document(
                    page_content=docstring,
                    metadata={
                        "source": self.source_file,
                        "type": "class_docstring",
                        "class": node.name,
                    },
                )
            )

        # Get the class definition including decorators
        class_lines = self.source_code.split("\n")[node.lineno - 1 : node.end_lineno]
        class_def = "\n".join(class_lines)

        self.documents.append(
            Document(
                page_content=class_def,
                metadata={
                    "source": self.source_file,
                    "type": "class_definition",
                    "class": node.name,
                },
            )
        )

        # Visit all child nodes (methods, etc.)
        self.generic_visit(node)
        self.current_class = old_class

    def visit_FunctionDef(self, node):
        # Extract function docstring
        docstring = ast.get_docstring(node)
        if docstring:
            self.documents.append(
                Document(
                    page_content=docstring,
                    metadata={
                        "source": self.source_file,
                        "type": "function_docstring",
                        "function": node.name,
                        "class": self.current_class,
                    },
                )
            )

        # Get the function definition including decorators
        func_lines = self.source_code.split("\n")[node.lineno - 1 : node.end_lineno]
        func_def = "\n".join(func_lines)

        self.documents.append(
            Document(
                page_content=func_def,
                metadata={
                    "source": self.source_file,
                    "type": "function_definition",
                    "function": node.name,
                    "class": self.current_class,
                },
            )
        )


def process_python_file(file_path, source_file):
    """
    Process a Python file into meaningful chunks using AST.
    Returns a list of Document objects.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        source_code = f.read()

    try:
        # Parse the source code into an AST
        tree = ast.parse(source_code)

        # Create a visitor and walk the AST
        visitor = CodeVisitor(source_code, source_file)
        visitor.visit(tree)

        # Add the module docstring if it exists
        module_docstring = ast.get_docstring(tree)
        if module_docstring:
            visitor.documents.insert(
                0,
                Document(
                    page_content=module_docstring,
                    metadata={"source": source_file, "type": "module_docstring"},
                ),
            )

        return visitor.documents

    except SyntaxError:
        # If we can't parse the file, return it as a single document
        return [
            Document(
                page_content=source_code,
                metadata={"source": source_file, "type": "unparseable_python_file"},
            )
        ]
