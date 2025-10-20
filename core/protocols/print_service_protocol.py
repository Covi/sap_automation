from pathlib import Path
from typing import Protocol

class PrintServiceProtocol(Protocol):
    def imprimir_fichero(self, ruta_fichero: Path) -> None: ...