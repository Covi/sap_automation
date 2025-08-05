# utils/file_downloader.py

from pathlib import Path
import tempfile, shutil, os, time
from typing import Any

class FileDownloader:
    @staticmethod
    def handle_download(download: Any, destination: Path, filename: str) -> Path:
        try:
            temp_file_path = Path(tempfile.gettempdir()) / download.suggested_filename
            download.save_as(str(temp_file_path))

            final_file_path = destination / filename
            if final_file_path.exists():
                os.remove(final_file_path)

            shutil.move(str(temp_file_path), str(final_file_path))
            return final_file_path
        except Exception as e:
            raise RuntimeError(f"Error durante la descarga: {e}") from e

    @staticmethod
    def is_file_recent(file_path: Path, seconds: int = 10) -> bool:
        if not file_path.exists():
            return False
        return (time.time() - file_path.stat().st_mtime) < seconds
