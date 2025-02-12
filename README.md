# Reachy2 Expert Agent

An intelligent assistant for the Reachy2 robot platform that provides accurate, context-aware responses about robot control and programming.

## Features

- Context-aware responses using RAG (Retrieval-Augmented Generation)
- Real-time code generation and execution
- Safety-first approach with built-in guidelines
- Comprehensive documentation search
- Interactive chat interface

## Project Structure

```
reachy2_expert_agent/
├── src/                    # Source code
│   ├── chatbot.py         # Main chatbot application
│   └── utils/             # Core utilities
│       ├── config.py      # Configuration settings
│       ├── rag_utils.py   # RAG pipeline utilities
│       ├── db_utils.py    # Database operations
│       └── embedding_utils.py  # Embedding generation
├── tests/                 # Test suite
│   ├── integration/      # Integration tests
│   ├── unit/            # Unit tests
│   └── conftest.py      # Test configuration
├── tools/                # Utility scripts
│   ├── chunk_documents.py    # Document chunking
│   ├── update_vectordb.py    # Vector database updates
│   ├── scrape_sdk_docs.py    # SDK documentation scraper
│   ├── scrape_vision_docs.py # Vision documentation scraper
│   ├── scrape_tutorials.py   # Tutorials scraper
│   ├── scrape_reachy2_docs.py # Main documentation scraper
│   ├── analyze_coverage.py   # Coverage analysis
│   └── evaluate_retrieval.py # Retrieval evaluation
├── data/                 # Data directory
│   ├── raw_docs/        # Raw documentation
│   ├── external_docs/   # Processed documentation
│   ├── vectorstore/    # Vector database
│   └── cache/          # Cache directory
└── docs/               # Documentation
```

## Setup

1. Create a Python virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Unix/macOS
   # or
   .\venv\Scripts\activate  # On Windows
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

   > **Note**: The initial installation will download the InstructorXL model (~5GB). This may take some time depending on your internet connection and requires sufficient disk space.

   > **Note**: For vision-related functionality (camera, object detection, tracking), you'll need to manually install the pollen-vision package:
   > ```bash
   > pip install git+https://github.com/pollen-robotics/pollen-vision.git
   > ```

3. Install in development mode:
   ```bash
   make install-dev
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` to include your API keys:
   ```bash
   # Required API keys
   MISTRAL_API_KEY=your_mistral_api_key    # Get from https://console.mistral.ai/
   
   # Optional settings
   DEBUG=false                             # Enable for detailed logging
   ```
   
   > **Note**: The Mistral API key is required for the chatbot to function. You can obtain one by:
   > 1. Creating an account at [console.mistral.ai](https://console.mistral.ai)
   > 2. Generating an API key in your account settings
   > 3. Copying the key to your `.env` file

5. Initialize the vector database:
   ```bash
   make refresh
   ```

   > **Note**: While `make refresh-full` is available to include Reachy2 docs, it's recommended to use `make refresh` as it provides all the necessary documentation for the agent to function properly. The full refresh option is still experimental and may include incomplete documentation.
   >
   > If you encounter network issues during the refresh process, the system will automatically retry failed operations. You can also run individual scraping commands separately:
   > ```bash
   > make clean        # Clean existing data
   > make scrape      # Scrape documentation
   > make chunk       # Process documents
   > make update-db   # Update vector database
   > ```

## Development

1. Run tests:
   ```bash
   make test
   ```

2. Run code quality checks:
   ```bash
   make lint
   make format
   ```

3. Update documentation:
   ```bash
   make docs
   ```

4. Evaluate retrieval performance:
   ```bash
   make evaluate
   ```

## Usage

Run the chatbot:
```bash
python src/chatbot.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.

## Acknowledgments

- Pollen Robotics for the Reachy2 platform
- Contributors and maintainers

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
