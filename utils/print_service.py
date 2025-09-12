# services/print_service.py
import logging
import subprocess
from pathlib import Path

log = logging.getLogger(__name__)

class PrintService:
    def imprimir_fichero(self, ruta_fichero: Path):
        """Envía un fichero a la cola de impresión del sistema."""
        if not ruta_fichero.exists():
            log.error(f"El fichero {ruta_fichero} no existe. No se puede imprimir.")
            return

        try:
            log.debug(f"Enviando '{ruta_fichero.name}' a la cola de impresión...")
            subprocess.run(['lp', str(ruta_fichero)], check=True, capture_output=True, text=True)
            log.debug("✅ El fichero se ha enviado a la cola de impresión correctamente.")
        except FileNotFoundError:
            log.error("El comando 'lp' no se encontró. Asegúrate de estar en un sistema compatible (Linux/macOS) o tener CUPS instalado.")
        except subprocess.CalledProcessError as e:
            log.error(f"Error al ejecutar el comando de impresión 'lp': {e.stderr}")