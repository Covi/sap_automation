# core/components/decorators/gridview.py

import json, logging
from typing import Optional, Dict, Any
from pages.sap_page_base import Locator  # para type hint

log = logging.getLogger(__name__)

class GridViewDecorator:
    """
    Decorador que añade capacidades de GridView a un componente SAP.
    No asume que el componente base es una tabla: solo interpreta metadatos
    de tipo GuiGridView si están presentes en el atributo `lsdata`.
    """

    def __init__(self, component, locator: Locator):
        self._component = component
        self._locator = locator
        self._metadata_cache: Optional[Dict[str, Any]] = None

    def _get_metadata_object(self) -> Optional[Dict[str, Any]]:
        """Busca el objeto de metadatos GridView en `lsdata`."""
        if self._metadata_cache:
            return self._metadata_cache

        lsdata_str = self._locator.get_attribute("lsdata")
        if not lsdata_str:
            log.warning("El atributo 'lsdata' no fue encontrado en el componente.")
            return None

        try:
            data = json.loads(lsdata_str)
            for value in data.values():
                if isinstance(value, dict) and value.get("Type") == "GuiGridView":
                    log.debug("Objeto de metadatos GridView encontrado.")
                    self._metadata_cache = value
                    return self._metadata_cache
            log.warning("No se encontró un objeto GridView en 'lsdata'.")
        except json.JSONDecodeError:
            log.error("No se pudo decodificar el JSON de 'lsdata'.")
        return None

    def get_total_row_count(self) -> int:
        """Devuelve el número total de filas según los metadatos GridView."""
        metadata = self._get_metadata_object()
        if metadata:
            total_rows = metadata.get("totalRows", 0)
            log.debug(f"GridView reporta un total de {total_rows} filas.")
            return int(total_rows)
        return 0

    def __getattr__(self, name):
        """Delegación al componente original para no perder sus métodos."""
        return getattr(self._component, name)
