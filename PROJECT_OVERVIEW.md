# Reachy2 Expert Agent Project Overview

## Project Description

The Reachy2 Expert Agent is an AI-powered documentation assistant designed to help users effectively work with the Reachy2 robot platform. It processes and indexes documentation from multiple sources to provide accurate and contextual responses to user queries about the Reachy2 SDK, Vision Module, and tutorials.

## Architecture

### Documentation Sources
1. **Reachy2 SDK Documentation**
   - API documentation extracted from source code
   - Code examples from the SDK repository
   - Function and class documentation
   
2. **Vision Module Documentation**
   - API documentation from the Pollen Vision module
   - Vision-specific examples and tutorials
   - Integration guides
   
3. **Tutorials**
   - Interactive Jupyter notebooks
   - Step-by-step guides
   - Practical examples and use cases

### Processing Pipeline

1. **Documentation Scraping**
   - `scrape_sdk_docs.py`: Extracts API documentation and examples from Reachy2 SDK
   - `scrape_vision_docs.py`: Processes Vision Module documentation and examples
   - `scrape_tutorials.py`: Collects and processes tutorial notebooks

2. **Document Chunking**
   - **API Documentation**:
     - Module-level documentation preserved as single chunks
     - Classes split into overview chunks and individual method chunks
     - Standalone functions with complete signatures and implementations
   - **Examples and Tutorials**:
     - Code blocks preserved with surrounding context
     - Natural breaks at markdown headers and code sections
     - Metadata tracking for code presence and relationships

3. **Vector Database**
   - Collections:
     - `api_docs_modules`: High-level module documentation
     - `api_docs_classes`: Class overviews and method documentation
     - `api_docs_functions`: Standalone function documentation
     - `reachy2_sdk`: SDK examples and implementation patterns
     - `vision_examples`: Vision-specific examples and guides
     - `reachy2_tutorials`: Interactive tutorials and guides

### Collection Structure

1. **api_docs_modules**
   - Module docstrings and purpose
   - Package organization
   - Module relationships

2. **api_docs_classes**
   - Class overview chunks with:
     - Class docstrings
     - Method summaries
     - Inheritance information
   - Method chunks with:
     - Complete signatures
     - Detailed documentation
     - Implementation code

3. **api_docs_functions**
   - Standalone function documentation
   - Complete signatures and parameters
   - Implementation details
   - Usage examples

4. **reachy2_sdk**
   - Complete working examples
   - Implementation patterns
   - Best practices
   - Integration examples

5. **vision_examples**
   - Camera integration examples
   - Vision processing code
   - Computer vision tutorials

6. **reachy2_tutorials**
   - Step-by-step guides
   - Interactive notebooks
   - Practical use cases
   - Code with explanations

### Query Processing

1. **User Input Processing**
   - Natural language query understanding
   - Context extraction and maintenance
   - Query type classification

2. **Document Retrieval**
   - Semantic search across relevant collections
   - Context-aware document ranking
   - Multi-collection query support

3. **Response Generation**
   - Context-aware response synthesis
   - Code example integration
   - Source attribution and references

## Current Status

### Completed Features
- Multi-source documentation processing pipeline
- Comprehensive API documentation extraction
- Example and tutorial integration
- Vector database implementation
- Basic query processing and response generation

### In Progress
- Enhanced context management
- Improved code example integration
- Advanced query understanding
- Response quality metrics

### Future Enhancements
- Real-time documentation updates
- Interactive code execution
- User feedback integration
- Custom tutorial generation
- Multi-language support

## Development Guidelines

### Documentation Processing
- Maintain clear separation between different documentation sources
- Ensure consistent metadata structure across collections
- Implement proper error handling and logging
- Regular validation of processed documents

### Code Quality
- Follow PEP 8 style guide
- Maintain comprehensive test coverage
- Document all major functions and classes
- Regular code reviews and updates

### Version Control
- Feature branches for new development
- Pull request reviews
- Semantic versioning
- Comprehensive commit messages

## Deployment

### Requirements
- Python 3.8+
- Required environment variables:
  - `MISTRAL_API_KEY`
  - Additional API keys as needed
- Sufficient storage for vector database
- Memory requirements based on collection size

### Monitoring
- Documentation processing metrics
- Query response times
- Error rates and types
- User feedback and satisfaction metrics

## Contributing

See `CONTRIBUTING.md` for detailed guidelines on:
- Code style and standards
- Pull request process
- Testing requirements
- Documentation updates

## License

This project is licensed under the Apache License 2.0 - see the `LICENSE` file for details.

## Contact

For questions or support:
- Project maintainers
- Issue tracker
- Community forums 