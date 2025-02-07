# Reachy2 Expert Agent

An intelligent documentation-aware assistant for the Reachy2 robot platform. This agent helps developers and users by providing accurate, context-aware responses about robot control, programming, and usage.

## Features

- 🤖 **Intelligent Query Processing**: Breaks down complex queries into manageable sub-tasks
- 📚 **Multi-Source Documentation**: Integrates API docs, tutorials, and code examples
- 🔍 **Context-Aware Responses**: Provides relevant code snippets and explanations
- 🛠️ **Comprehensive Coverage**: Covers SDK, Vision module, and tutorials
- 🔄 **Regular Updates**: Stays current with the latest documentation

## Project Structure

```
.
├── scripts/                 # Core processing scripts
│   ├── scrape_*.py         # Documentation scrapers
│   ├── chunk_documents.py  # Document processing
│   ├── update_vectordb.py  # Database management
│   ├── chatbot.py         # Main interface
│   └── evaluate_*.py      # Evaluation tools
├── utils/                 # Utility modules
│   ├── rag_utils.py      # RAG pipeline components
│   ├── db_utils.py       # Vector store management
│   ├── embedding_utils.py # Embedding generation
│   └── config.py         # Configuration
├── raw_docs/             # Raw documentation
├── external_docs/        # Processed documents
├── vectorstore/         # Vector embeddings
└── tests/              # Test suite
```

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/reachy2_expert_agent.git
cd reachy2_expert_agent
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your API keys:
```
MISTRAL_API_KEY=your_key_here
DEBUG=false
```

## Usage

1. Initialize the documentation database:
```bash
make refresh
```

2. Start the chatbot interface:
```bash
python scripts/chatbot.py
```

3. Access the interface at `http://localhost:7860`

## Development Commands

- **Clean generated files**:
  ```bash
  make clean
  ```

- **Update documentation**:
  ```bash
  make scrape  # Fetch latest docs
  make chunk   # Process documents
  make update-db  # Update vector store
  ```

- **Run tests**:
  ```bash
  make test
  ```

- **Evaluate performance**:
  ```bash
  make evaluate
  ```

## Documentation Sources

1. **Reachy2 SDK**
   - Official API documentation
   - SDK examples and implementations
   - Function and class documentation

2. **Vision Module**
   - Vision API documentation
   - Camera integration guides
   - Computer vision examples

3. **Tutorials**
   - Interactive notebooks
   - Step-by-step guides
   - Best practices

## Query Types

The agent supports specialized handling for different query types:

- 🔧 **Code Queries**: Implementation examples and API usage
- 📖 **Concept Queries**: Architecture and design explanations
- ⚠️ **Error Handling**: Troubleshooting and debugging
- 🔌 **Setup Questions**: Installation and configuration
- 👁️ **Vision Queries**: Camera and vision system usage

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Pollen Robotics for the Reachy2 robot platform
- The open-source community for various tools and libraries

## Contact

For questions or support:
- Create an issue in the repository
- Contact the project maintainers

```
Copyright 2024 Pollen Robotics

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```
