# config.py

TOKEN_HOLD_MIN = 0.1       # Minimum time to hold token (seconds)
TOKEN_TIMEOUT = 1          # Timeout for token regeneration (seconds)
DEBUG_MODE = False         # Set to True to enable debug messages
 
# Message types
DATA_HEADER = 0x10
DATA_CHUNK = 0x11
DATA_END = 0x12
DATA_CHUNK_SIZE = 7 