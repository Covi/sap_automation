# utils/file_handler.py

import os
import time
import shutil
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Any


class FileHandler:
    @staticmethod
    def save_with_timestamp(file_bytes: bytes, destino: Path, filename: str) -> Path:
        """Guarda un fichero en destino añadiendo timestamp al nombre."""
        destino.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        final_name = f"{Path(filename).stem}_{timestamp}.pdf"
        final_path = destino / final_name

        with open(final_path, "wb") as f:
            f.write(file_bytes)

        return final_path

    @staticmethod
    def save_from_download(download: Any, destino: Path, filename: str) -> Path:
        """Mueve un fichero descargado por navegador a destino con nombre fijo."""
        destino.mkdir(parents=True, exist_ok=True)
        temp_file_path = Path(tempfile.gettempdir()) / download.suggested_filename
        download.save_as(str(temp_file_path))

        final_path = destino / filename
        if final_path.exists():
            os.remove(final_path)

        shutil.move(str(temp_file_path), str(final_path))
        return final_path

    @staticmethod
    def is_file_recent(file_path: Path, seconds: int = 10) -> bool:
        """Comprueba si un archivo se ha modificado en los últimos `seconds` segundos."""
        return file_path.exists() and (time.time() - file_path.stat().st_mtime) < seconds
