# Token Ring Network Simulator

## Project Description
This project simulates a token ring network protocol in Python. Each node in the ring passes a token to its neighbor, enabling controlled data transmission and coordination. The codebase is modular, making it easy to maintain, extend, and understand.

## Folder and File Structure

```
token/
├── config.py       # Configuration constants and protocol settings
├── utils.py        # Utility functions for packing/unpacking messages
├── models.py       # Data models (e.g., for received data)
├── network.py      # Network input/output and socket handling
├── token_ring.py   # Core business logic (TokenRingNode class)
├── main.py         # Main entry point to run a node
└── __init__.py     # Package marker (empty)
```

- **config.py**: Stores configuration constants and protocol parameters.
- **utils.py**: Contains helper functions for message formatting and parsing.
- **models.py**: Defines data structures used for message handling.
- **network.py**: Handles socket creation and data transmission.
- **token_ring.py**: Implements the TokenRingNode class and core logic.
- **main.py**: Entry point for running a node in the token ring.
- **__init__.py**: Marks the directory as a Python package.

## Installation Instructions

1. **Clone the repository** (if not already):
   ```sh
   git clone <your-repo-url>
   cd token
   ```

2. **Install Python 3.7 or higher** (if not already installed).

3. **(Optional) Create a virtual environment:**
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install dependencies:**
   
   This project uses only Python's standard library. No additional packages are required.

## How to Run the Project

From the `token` directory, run:

```sh
python main.py
```

This will start a node in the token ring network with the default configuration (Node 1 in a 3-node ring). You can modify the parameters in `main.py` to simulate different nodes or network topologies.

## Usage Example

When you run the program, you should see output similar to:

```
[12:00:00] Node1: Node started – press Ctrl-C to quit
[12:00:02] Node1: TOKEN created for node2 (seq=1)
[12:00:02] Node1: TOKEN forwarded to node2 (seq=1)
...
```

Each node will log token passing and data transmission events.

## Future Improvements / Known Issues

- Add support for dynamic node joining and leaving.
- Implement more robust error handling and logging.
- Add unit tests and integration tests.
- Provide a configuration file or CLI for easier setup.
- Support for running multiple nodes on different machines.

---

For any questions or contributions, please open an issue or submit a pull request. 