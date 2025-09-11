# core/components/table/sap_table_component.py
import logging
import json
from typing import Optional, Dict, Any

# Se importa la clase base de página para el type hinting y el componente base
from pages.sap_page_base import SAPPageBase, Locator
from ..sap_component import SAPComponent

log = logging.getLogger(__name__)

class SAPTableComponent(SAPComponent):
    """
    Componente genérico que encapsula la lógica de interacción con una tabla
    de resultados de SAP (específicamente un control GuiGridView).
    """

    def __init__(self, sap_page: SAPPageBase, table_locator: Locator):
        super().__init__(sap_page)
        self.table_locator = table_locator
        self.select_all_header = self.table_locator.get_by_role(
            "columnheader", name="Columna de selección de filas"
        )
        self._metadata_cache: Optional[Dict[str, Any]] = None

    def is_visible(self, timeout: Optional[float] = 20000) -> bool:
        log.info(f"Comprobando visibilidad de la tabla: {self.table_locator}")
        try:
            self.table_locator.wait_for(state="visible", timeout=timeout)
            log.info("Tabla visible.")
            return True
        except Exception:
            log.warning("La tabla no se ha hecho visible en el tiempo esperado.")
            return False

    def select_all(self):
        if self.select_all_header.is_visible():
            log.info("Seleccionando todas las filas de la tabla...")
            self.select_all_header.click()
        else:
            log.warning("El botón para seleccionar todas las filas no está visible.")

    def click_toolbar_button(self, button_name: str):
        log.info(f"Intentando hacer clic en el botón '{button_name}' de la barra de herramientas.")
        try:
            button_locator = self.table_locator.get_by_role("button", name=button_name, exact=True)
            button_locator.click()
            log.info(f"Clic en el botón '{button_name}' realizado con éxito.")
        except Exception as e:
            log.error(f"No se pudo hacer clic en el botón '{button_name}': {e}")
            raise

    def _get_metadata_object(self) -> Optional[Dict[str, Any]]:
        """
        Método privado para encontrar y cachear el objeto de metadatos de la tabla.
        Busca por su "firma" en lugar de por una clave fija.
        """
        if self._metadata_cache:
            return self._metadata_cache

        log.info("Buscando metadatos de la tabla en el atributo 'lsdata'.")
        lsdata_str = self.table_locator.get_attribute("lsdata")
        if not lsdata_str:
            log.warning("El atributo 'lsdata' no fue encontrado en la tabla.")
            return None

        try:
            data = json.loads(lsdata_str)
            for value in data.values():
                if isinstance(value, dict) and value.get("Type") == "GuiGridView":
                    log.info("Objeto de metadatos de GuiGridView encontrado.")
                    self._metadata_cache = value
                    return self._metadata_cache
            
            log.warning("No se encontró un objeto de metadatos de tipo 'GuiGridView' en 'lsdata'.")
            return None

        except json.JSONDecodeError:
            log.error("No se pudo decodificar el JSON del atributo 'lsdata'.")
            return None

    def get_total_row_count_robust(self) -> int:
        """
        (RECOMENDADO) Devuelve el número TOTAL de filas buscando los metadatos
        por su firma semántica ("Type": "GuiGridView").
        """
        metadata = self._get_metadata_object()
        if metadata:
            total_rows = metadata.get("totalRows", 0)
            log.info(f"[Robusto] La tabla reporta un total de {total_rows} filas.")
            return int(total_rows)
        
        log.warning("[Robusto] No se pudo determinar el número total de filas.")
        return 0

    def get_total_row_count_by_key(self, key: str = "34") -> int:
        """
        (FRÁGIL) Devuelve el número TOTAL de filas usando una clave 'mágica'
        hardcodeada (ej: "34"). Menos robusto, pero útil para comparar.
        """
        log.warning(f"Extrayendo metadatos de la tabla desde la clave '{key}'.")
        lsdata_str = self.table_locator.get_attribute("lsdata")
        if not lsdata_str: return 0

        try:
            data = json.loads(lsdata_str)
            metadata = data.get(key, {})
            total_rows = metadata.get("totalRows", 0)
            log.info(f"[Por Clave] La tabla reporta un total de {total_rows} filas.")
            return int(total_rows)
        except (json.JSONDecodeError, AttributeError):
            log.warning(f"[Por Clave] No se pudo determinar el número de filas usando la clave '{key}'.")
            return 0

    def get_visible_row_count(self) -> int:
        count = self.table_locator.locator("role=row:has(role=gridcell)").count()
        log.info(f"Se han encontrado {count} filas de datos visibles en el DOM.")
        return count

    def click_cell(self, row_index: int, col_index: int):
        log.info(f"Intentando hacer clic en la celda de la fila {row_index}, columna {col_index}.")
        try:
            row_locator = self.table_locator.locator("role=row:has(role=gridcell)").nth(row_index)
            cell_locator = row_locator.locator("role=gridcell").nth(col_index)
            cell_locator.click()
            log.info("Clic en la celda realizado con éxito.")
        except Exception as e:
            log.error(f"No se pudo hacer clic en la celda ({row_index}, {col_index}): {e}")
            raise