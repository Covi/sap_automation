import logging
from typing import Optional

from pages.sap_page_base import SAPPageBase, Locator
from ..sap_component import SAPComponent

log = logging.getLogger(__name__)


class SAPTableComponent(SAPComponent):
    """
    Componente base que encapsula lógica genérica de una tabla SAP.
    NO está acoplado a GridView ni a otro renderizador.
    """

    def __init__(self, sap_page: SAPPageBase, table_locator: Locator):
        super().__init__(sap_page)
        self.table_locator = table_locator

    def is_visible(self, timeout: Optional[float] = 20000) -> bool:
        log.debug(f"Comprobando visibilidad de la tabla: {self.table_locator}")
        try:
            self.table_locator.wait_for(state="visible", timeout=timeout)
            log.debug("Tabla visible.")
            return True
        except Exception:
            log.warning("La tabla no se ha hecho visible en el tiempo esperado.")
            return False

    def get_visible_row_count(self) -> int:
        """
        Devuelve el número de filas visibles en el DOM (genérico).
        """
        count = self.table_locator.locator("role=row:has(role=gridcell)").count()
        log.debug(f"Se han encontrado {count} filas de datos visibles en el DOM.")
        return count

    def click_cell(self, row_index: int, col_index: int):
        """
        Clic en una celda concreta (fila/columna).
        """
        log.debug(f"Intentando hacer clic en la celda de la fila {row_index}, columna {col_index}.")
        try:
            row_locator = self.table_locator.locator("role=row:has(role=gridcell)").nth(row_index)
            cell_locator = row_locator.locator("role=gridcell").nth(col_index)
            cell_locator.click()
            log.debug("Clic en la celda realizado con éxito.")
        except Exception as e:
            log.error(f"No se pudo hacer clic en la celda ({row_index}, {col_index}): {e}")
            raise
