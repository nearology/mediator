# utils.py

import struct
from config import DATA_HEADER, DATA_CHUNK, DATA_END, DATA_CHUNK_SIZE

def pack_data_header(origin: int, seq: int, dst: int, total_len: int) -> bytes:
    """Build DATA_HEADER: type|origin|seq|dst|total_len|r|r|r"""
    return bytes([
        DATA_HEADER,
        origin & 0xFF,
        (seq >> 8) & 0xFF,
        seq & 0xFF,
        dst & 0xFF,
        total_len & 0xFF,
        0, 0
    ])

def pack_data_chunk(chunk: bytes) -> bytes:
    """Build DATA_CHUNK: type|data[0:7]"""
    chunk = chunk.ljust(DATA_CHUNK_SIZE, b'\x00')[:DATA_CHUNK_SIZE]
    return bytes([DATA_CHUNK]) + chunk

def pack_data_end(origin: int, seq: int, dst: int) -> bytes:
    """Build DATA_END message"""
    return bytes([
        DATA_END,
        origin & 0xFF,
        (seq >> 8) & 0xFF,
        seq & 0xFF,
        dst & 0xFF,
        0, 0, 0
    ])

def pack_token(origin: int, seq: int, dst: int) -> bytes:
    """Pack token using 64-bit integer"""
    token_type = 0
    value = (token_type << 56) | (origin << 48) | (seq << 16) | (dst << 8)
    return struct.pack('>Q', value)

def unpack_token(data: bytes) -> dict:
    """Unpack 64-bit token"""
    if len(data) != 8:
        raise ValueError(f"Invalid token length: {len(data)}, expected 8")
    value = struct.unpack('>Q', data)[0]
    token_type = (value >> 56) & 0xFF
    origin = (value >> 48) & 0xFF
    seq = (value >> 16) & 0xFFFFFFFF
    dst = (value >> 8) & 0xFF
    return {
        "type": "TOKEN" if token_type == 0 else "UNKNOWN",
        "origin": origin,
        "seq": seq,
        "dst": dst
    }

def unpack_data_header(msg: bytes):
    """Extract fields from DATA_HEADER message (8 bytes)"""
    if len(msg) != 8 or msg[0] != DATA_HEADER:
        raise ValueError("Invalid DATA_HEADER message")
    return {
        "type": msg[0],
        "origin": msg[1],
        "seq": (msg[2]<<8) | msg[3],
        "dst": msg[4],
        "total_len": msg[5]
    }

def unpack_data_chunk(msg: bytes):
    """Extract data (7 bytes) from DATA_CHUNK message"""
    if len(msg) != 8 or msg[0] != DATA_CHUNK:
        raise ValueError("Invalid DATA_CHUNK message")
    return {
        "type": msg[0],
        "data": msg[1:8]
    }

def unpack_data_end(msg: bytes):
    """Extract fields from DATA_END message (8 bytes)"""
    if len(msg) != 8 or msg[0] != DATA_END:
        raise ValueError("Invalid DATA_END message")
    return {
        "type": msg[0],
        "origin": msg[1],
        "seq": (msg[2]<<8) | msg[3],
        "dst": msg[4]
    } 