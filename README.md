# Reachy2 Expert Safer

## Overview

Reachy2 Expert Safer is a project designed to centralize and streamline various resources and examples for the Reachy2 platform. The project gathers materials from different repositories to provide a one-stop-shop for:

- **Tutorials:** Notebook examples from the Reachy2 Tutorials repository, which guide users through various functionalities of Reachy2.
- **SDK Examples:** Code examples and scripts from the Reachy2 SDK repository, showing how to interface with and control Reachy2.
- **Vision Scripts:** Python scripts from the Pollen Vision repository, focusing on vision and image processing for Reachy2.

## How It Works

This project uses automated Python scripts located in the `scripts/` directory to manage the repositories:

1. **Cloning/Updating Repositories:** Each script checks if the respective repository is already cloned. If not, it clones the repository. If it exists, it pulls the latest changes.
2. **Refreshing Content:** The scripts copy notebooks and code files into the `external_docs/Codebase` directory. Running `make refresh` executes all these scripts in sequence.

## Setup

Follow these steps to get started:

1. **Set Up a Virtual Environment:**
   - On macOS/Linux:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Refresh the Repositories:**
   Run the following command to update all resources:
   ```bash
   make refresh
   ```

## Troubleshooting

- **Network Issues:** If you encounter errors during cloning (e.g., HTTP/2 RPC errors), retry the command or force Git to use HTTP/1.1 with:
  ```bash
  git config --global http.version HTTP/1.1
  ```

- **Repository Structure:** Ensure that the repository URLs and expected folder structures haven't changed. The scripts rely on folders like `src/examples` for the SDK repository.

## Contributing

Contributions are welcome! If you have suggestions or improvements, please open an issue or submit a pull request.

## License

[Specify your license here, e.g., MIT License]

## Contact

For more information, please contact the project maintainers.