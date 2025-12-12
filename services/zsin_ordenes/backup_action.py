# services/zsin_ordenes/backup_action.py
import logging
import json
from pathlib import Path
from typing import List, Dict
from core.protocols import FileHandlerProtocol

class BackupOrdenesService:
    """
    Acción específica para persistir los datos de la tabla ZSIN_ORDENES en formato JSON.
    """
    def __init__(self, file_handler: FileHandlerProtocol, logger: logging.Logger):
        self._file_handler = file_handler
        self._log = logger

    def ejecutar(self, data: List[Dict[str, str]], base_path: Path, filename_prefix: str = "backup_resultados"):
        """
        Guarda los datos estructurados en un fichero JSON con timestamp.
        """
        self._log.info("Acción: Realizando backup de resultados...")
        
        if not data:
            self._log.warning("Backup: No hay datos para guardar.")
            return

        try:
            # Serializamos a JSON bytes conservando tildes (ensure_ascii=False)
            json_bytes = json.dumps(data, ensure_ascii=False, indent=4).encode('utf-8')
            
            # Usamos el file_handler existente
            saved_path = self._file_handler.save_with_timestamp(
                json_bytes, 
                base_path, 
                f"{filename_prefix}.json"
            )
            
            self._log.info(f"✅ Backup guardado correctamente en: {saved_path.name}")
            
        except Exception as e:
            # Logueamos error pero no interrumpimos el flujo principal
            self._log.error(f"❌ Error generando backup: {e}", exc_info=True)