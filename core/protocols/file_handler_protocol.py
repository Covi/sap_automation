from pathlib import Path
from typing import Protocol

class FileHandlerProtocol(Protocol):
    def save_with_timestamp(self, data: bytes, path: Path, filename: str) -> Path: ...