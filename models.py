# models.py

from dataclasses import dataclass
from typing import List

@dataclass
class DataReceive:
    origin: int
    seq: int
    dst: int
    length: int
    chunks: List[bytes] 