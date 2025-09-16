import json
import logging
from typing import Optional, Dict, Any

from pages.sap_page_base import SAPPageBase, Locator
from ..sap_component import SAPComponent

log = logging.getLogger(__name__)


class SAPTableComponent(SAPComponent):
    """
    Componente de tabla base, CONCRETO y FUNCIONAL.
    Proporciona implementaciones básicas que funcionan en la mayoría de tablas
    (ej: contando elementos visibles del DOM). No es abstracta.
    """
    def __init__(self, sap_page: SAPPageBase, table_locator: Locator):
        super().__init__(sap_page)
        self.table_locator = table_locator

    def wait_for_table(self, timeout: float = 30000):
        """Implementación base: espera a que el contenedor sea visible."""
        log.debug("Esperando a que el contenedor de la tabla sea visible...")
        self.table_locator.wait_for(state="visible", timeout=timeout)
        log.debug("Contenedor de tabla visible.")

    def get_total_row_count(self) -> int:
        """Implementación base: cuenta las filas visibles en el DOM."""
        count = self.table_locator.locator("div[ct='ALT']").count()
        log.debug(f"(Método base) Se han encontrado {count} filas visibles.")
        return count

    def select_all(self):
        """Implementación base: no hace nada, ya que no hay un método universal."""
        log.warning("La operación 'select_all' no está soportada por la tabla base.")
        pass

    def click_toolbar_button(self, button_name: str, exact: bool = True):
        """Implementación base: no hace nada."""
        log.warning(f"La operación 'click_toolbar_button' para '{button_name}' no está soportada por la tabla base.")
        pass


class GridViewDecorator(SAPTableComponent):
    """
    DECORADOR: Envuelve un componente de tabla para añadirle las funcionalidades
    específicas del control 'GuiGridView' (leer metadatos, usar botones específicos).
    """
    def __init__(self, table_component: SAPTableComponent):
        # El decorador CONTIENE (envuelve) una instancia de la tabla base.
        super().__init__(table_component.sap_page, table_component.table_locator)
        self._component_wrapped = table_component
        
        # Lógica y selectores específicos de GridView
        self.select_all_button = self.table_locator.locator("[id$='-sa']")
        self._metadata_cache: Optional[Dict[str, Any]] = None

    def _get_metadata_object(self) -> Optional[Dict[str, Any]]:
        """Encuentra y cachea el objeto de metadatos 'GuiGridView' de la tabla."""
        if self._metadata_cache: return self._metadata_cache
        lsdata_str = self.table_locator.get_attribute("lsdata")
        if not lsdata_str: return None
        try:
            data = json.loads(lsdata_str)
            for value in data.values():
                if isinstance(value, dict) and value.get("Type") == "GuiGridView":
                    self._metadata_cache = value
                    return self._metadata_cache
            return None
        except json.JSONDecodeError:
            return None

    # --- MÉTODOS MEJORADOS (OVERRIDE) ---

    def wait_for_table(self, timeout: float = 30000):
        """Versión mejorada: espera a que una celda de datos sea visible."""
        log.debug("Esperando a que la tabla GuiGridView sea visible...")
        self.table_locator.wait_for(state="visible", timeout=timeout)
        self.table_locator.get_by_role("gridcell").first.wait_for(state="visible", timeout=timeout)
        log.debug("Tabla GuiGridView visible y con celdas.")

    def get_total_row_count(self) -> int:
        """
        Versión mejorada: intenta leer los metadatos. Si falla, delega
        la llamada al componente base que está envolviendo (fallback).
        """
        metadata = self._get_metadata_object()
        if metadata:
            total_rows = metadata.get("totalRows", 0)
            if total_rows > 0:
                log.debug(f"(Desde metadatos) La tabla reporta un total de {total_rows} filas.")
                return int(total_rows)
        
        # Fallback: si no hay metadatos, llama al método original del objeto envuelto
        log.warning("No se pudo obtener el total de filas desde metadatos, usando método base.")
        return self._component_wrapped.get_total_row_count()

    def select_all(self):
        """Versión mejorada: usa el selector específico de GuiGridView."""
        if self.select_all_button.is_visible():
            log.debug("Seleccionando todas las filas (método GuiGridView)...")
            self.select_all_button.click()
        else:
            # Fallback
            log.warning("Botón 'seleccionar todo' de GuiGridView no encontrado.")
            self._component_wrapped.select_all()

    def click_toolbar_button(self, button_name: str, exact: bool = True):
        """Versión mejorada: usa el selector de botones de GuiGridView."""
        try:
            button_locator = self.table_locator.get_by_role("button", name=button_name, exact=exact)
            button_locator.click()
            log.debug(f"Clic en el botón '{button_name}' realizado con éxito.")
        except Exception as e:
            log.error(f"No se pudo hacer clic en el botón '{button_name}': {e}")
            self._component_wrapped.click_toolbar_button(button_name, exact)