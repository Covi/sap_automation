from pathlib import Path
import time

class FileValidator:
    @staticmethod
    def is_file_recent(file_path: Path, seconds: int = 10) -> bool:
        """
        Verifica si un archivo es reciente.

        Args:
            file_path (Path): La ruta del archivo a validar.
            seconds (int): El número de segundos para considerar un archivo como reciente.

        Returns:
            bool: True si el archivo es reciente, False en caso contrario.
        """
        if not file_path.exists():
            return False
        
        # Comprueba si el tiempo transcurrido desde la última modificación es menor a `seconds`
        return (time.time() - file_path.stat().st_mtime) < seconds