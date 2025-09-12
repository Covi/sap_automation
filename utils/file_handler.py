import os
import time
import shutil
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Any, Tuple

class FileHandler:
    @staticmethod
    def _prepare_destination(destino: Path, filename: str) -> Tuple[Path, str]:
        """
        Prepara el destino creando el directorio y limpiando el nombre del fichero.
        Esto centraliza la lógica común y evita la repetición (DRY).
        """
        destino.mkdir(parents=True, exist_ok=True)
        # BUG FIX: Se extrae solo el nombre para evitar crear subdirectorios.
        clean_filename = Path(filename).name
        return destino, clean_filename

    @staticmethod
    def save_with_timestamp(file_bytes: bytes, destino: Path, filename: str) -> Path:
        """
        Guarda un fichero en destino añadiendo timestamp al nombre.
        No crea subdirectorios si filename viene con rutas.
        """
        destino, clean_filename = FileHandler._prepare_destination(destino, filename)

        base_name = Path(clean_filename).stem
        ext = Path(clean_filename).suffix
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        final_name = f"{base_name}_{timestamp}{ext}"

        final_path = destino / final_name

        with open(final_path, "wb") as f:
            f.write(file_bytes)

        return final_path

    @staticmethod
    def save_from_download(download: Any, destino: Path, filename: str) -> Path:
        """Mueve un fichero descargado por navegador a destino con nombre fijo."""
        destino, clean_filename = FileHandler._prepare_destination(destino, filename)
        
        temp_file_path = Path(tempfile.gettempdir()) / download.suggested_filename
        download.save_as(str(temp_file_path))

        final_path = destino / clean_filename
        
        # shutil.move sobreescribe, por lo que el `if/remove` puede ser redundante,
        # pero se mantiene por seguridad en todos los casos.
        if final_path.exists():
            os.remove(final_path)

        shutil.move(str(temp_file_path), str(final_path))
        return final_path

    @staticmethod
    def is_file_recent(file_path: Path, seconds: int = 10) -> bool:
        """Comprueba si un archivo se ha modificado en los últimos `seconds` segundos."""
        return file_path.exists() and (time.time() - file_path.stat().st_mtime) < seconds