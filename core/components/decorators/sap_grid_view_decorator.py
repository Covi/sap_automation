# core/components/decorators/sap_grid_view_decorator.py

import json
import logging
from typing import Optional, Dict, Any
from ..interfaces.component_with_locator import ComponentWithLocator

log = logging.getLogger(__name__)


class SAPGridViewDecorator:
    """
    Decorador específico para tablas SAP de tipo GridView.
    Proporciona acceso a la metadata interna ('lsdata') y funcionalidades adicionales.
    """

    def __init__(self, component: ComponentWithLocator):
        if component is None:
            raise ValueError("El componente no puede ser None.")
        if not isinstance(component, ComponentWithLocator):
            raise TypeError("SAPGridViewDecorator requiere un componente que implemente ComponentWithLocator.")
        if not hasattr(component, "component_locator"):
            raise ValueError("El componente no tiene un locator válido.")

        self._component = component
        self._metadata_cache: Optional[Dict[str, Any]] = None

    # --------------------
    # Métodos internos
    # --------------------
    def _get_lsdata_json(self) -> Optional[Dict[str, Any]]:
        """Obtiene y parsea el JSON de lsdata del componente."""
        lsdata_str = self._component.component_locator.get_attribute("lsdata")
        if not lsdata_str:
            log.warning("No se encontró 'lsdata' en el componente.")
            return None
        try:
            return json.loads(lsdata_str)
        except json.JSONDecodeError:
            log.error("No se pudo decodificar 'lsdata'.")
            return None

    def _extract_gridview_metadata(self, lsdata: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extrae el objeto GuiGridView del JSON de lsdata."""
        for value in lsdata.values():
            if isinstance(value, dict) and value.get("Type") == "GuiGridView":
                log.debug("Objeto de metadatos GridView encontrado.")
                return value
        log.warning("No se encontró un objeto GuiGridView en 'lsdata'.")
        return None

    def _get_metadata_object(self) -> Optional[Dict[str, Any]]:
        """Devuelve la metadata del GridView, cacheada si ya se obtuvo."""
        if self._metadata_cache:
            return self._metadata_cache

        lsdata_json = self._get_lsdata_json()
        if not lsdata_json:
            return None

        self._metadata_cache = self._extract_gridview_metadata(lsdata_json)
        return self._metadata_cache

    # --------------------
    # API pública
    # --------------------

    def get_column_names(self) -> list[str]:
        """
        Devuelve la lista de IDs técnicos de las columnas definidos en la metadata (lsdata).
        Es vital para mapear los valores extraídos con su campo real.
        
        Retorna:
            list[str]: Ejemplo ['ICON', 'NUMEROORDEN', 'STATUS', ...]
        """
        metadata = self._get_metadata_object()
        
        # Validación defensiva
        if not metadata:
            log.warning("No se pudo obtener metadata para extraer nombres de columnas.")
            return []
            
        # 'ColumnIDs' es la clave estándar en SAP WebGUI para GridViews
        # Verificado en el lsdata que proporcionaste.
        columns = metadata.get("ColumnIDs", [])
        
        if not columns:
            log.warning("La metadata existe pero no contiene 'ColumnIDs'.")
            return []
            
        log.debug(f"Columnas detectadas en metadata ({len(columns)}): {columns}")
        return columns

    def get_total_row_count(self, fallback: bool = True) -> int:
        """
        Devuelve el número total de filas según la metadata del GridView.
        Si fallback=True, intenta contar filas visibles si no hay metadata.
        """
        metadata = self._get_metadata_object()
        if metadata:
            total_rows = metadata.get("totalRows", 0)
            log.debug(f"GridView reporta un total de {total_rows} filas.")
            return int(total_rows)

        if fallback:
            try:
                rows = self._component.component_locator.locator("role=row").all()
                log.debug(f"Fallback: contando {len(rows)} filas visibles.")
                return len(rows)
            except Exception:
                log.warning("Fallback: no se pudieron contar filas visibles.")
        return 0

    def refresh_metadata(self):
        """Forzar la recarga de metadata desde lsdata."""
        self._metadata_cache = None
        self._get_metadata_object()

    # --------------------
    # Delegación automática
    # --------------------
    def __getattr__(self, name):
        """Delegación automática al componente base."""
        return getattr(self._component, name)
