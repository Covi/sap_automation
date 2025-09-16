import json
import logging
from typing import Optional, Dict, Any
from ..interfaces.component_with_locator import ComponentWithLocator

log = logging.getLogger(__name__)

class GridViewDecorator:
    """
    Decorador que añade capacidades de GridView a un componente que
    implementa ComponentWithLocator.
    """

    def __init__(self, component: ComponentWithLocator):
        self._component = component
        self._metadata_cache: Optional[Dict[str, Any]] = None

    def _get_metadata_object(self) -> Optional[Dict[str, Any]]:
        if self._metadata_cache:
            return self._metadata_cache

        lsdata_str = self._component.table_locator.get_attribute("lsdata")
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
        metadata = self._get_metadata_object()
        if metadata:
            total_rows = metadata.get("totalRows", 0)
            log.debug(f"GridView reporta un total de {total_rows} filas.")
            return int(total_rows)
        return 0

    def __getattr__(self, name):
        """Delegación automática al componente base."""
        return getattr(self._component, name)
