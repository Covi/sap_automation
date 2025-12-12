import logging
from typing import List, Optional
from pages.sap_page_base import SAPPageBase, Locator
from ..sap_component import SAPComponent
from ..interfaces.component_with_locator import ComponentWithLocator

log = logging.getLogger(__name__)


class SAPTableComponent(SAPComponent, ComponentWithLocator):
    """
    Componente genérico para representar una tabla SAP.
    Implementa ComponentWithLocator para poder ser decorado.
    """

    def __init__(self, sap_page: SAPPageBase, component_locator: Locator):
        super().__init__(sap_page)
        # CAMBIO: renombrado y unificación con la interfaz
        self._component_locator = component_locator  # antes _table_locator

        self.select_all_header = self._component_locator.get_by_role(
            "columnheader", name="Columna de selección de filas"
        )

    # --------------------
    # Propiedad de la interfaz
    # --------------------
    @property
    def component_locator(self) -> Locator:  # CAMBIO: ahora coincide con ComponentWithLocator
        return self._component_locator


    # ------------------------------------------------------
    # Métodos de lectura de datos

    def get_all_rows_data(self) -> List[List[str]]:
        """
        Recorre las filas visibles y extrae el texto limpio de cada celda.
        
        FIX CRÍTICO: 
        1. Se usa 'hpn' (Content Pan Mode) para ir al contenedor de datos.
        2. Se elimina la restricción [role='row'] del 'tr' porque en SAP WebGUI 
           las filas de datos a veces son 'tr' simples sin rol ARIA explícito.
        """
        # Selector relajado: Cualquier TR dentro del div de datos que tenga celdas gridcell
        rows_locator = self._component_locator.locator("div[hpn='none'] tr:has([role='gridcell'])")

        # Obtenemos snapshot de elementos para iterar
        rows = rows_locator.all()
        table_data = []

        log.debug(f"Iniciando extracción de datos de {len(rows)} filas visibles (Tabla Principal)...")

        for row in rows:
            row_data = []
            # Obtenemos las celdas de la fila actual
            cells = row.locator("[role='gridcell']").all()

            for cell in cells:
                # ESTRATEGIA HÍBRIDA:
                # El dato limpio suele estar en un span interno con role="textbox" (inputs/readonly)
                sap_textbox = cell.locator("span[role='textbox']")

                if sap_textbox.count() > 0:
                    # Caso 1: Estructura compleja (input simulado), sacamos el texto de ahí.
                    text_value = sap_textbox.first.inner_text()
                else:
                    # Caso 2: Celda simple, icono o texto plano sin wrapper.
                    text_value = cell.inner_text()

                # Limpiamos espacios extra que SAP suele meter
                row_data.append(text_value.strip())

            table_data.append(row_data)

        return table_data

    def get_visible_row_count(self) -> int:
        count = self._component_locator.locator("role=row:has(role=gridcell)").count()
        log.debug(f"Se han encontrado {count} filas de datos visibles en el DOM.")
        return count



    # ------------------------------------------------------
    # Métodos de acciones o actuación sobre elementos
    # FIXME Posiblemente estoc no deba ir aquí, es decir, el cómo actuar sobre algo

    def is_visible(self, timeout: Optional[int] = 30000) -> bool:
        try:
            self._component_locator.wait_for(state="visible", timeout=timeout)
            log.debug("Tabla visible.")
            return True
        except Exception:
            segundos = timeout / 1000 if timeout else "indefinido"
            log.warning(f"La tabla no se ha hecho visible en el tiempo esperado: {segundos} segundos.")
            return False

    def click_cell(self, row_index: int, col_index: int):
        try:
            row_locator = self._component_locator.locator("role=row:has(role=gridcell)").nth(row_index)
            cell_locator = row_locator.locator("role=gridcell").nth(col_index)
            cell_locator.click()
            log.debug("Clic en la celda realizado con éxito.")
        except Exception as e:
            log.error(f"No se pudo hacer clic en la celda ({row_index}, {col_index}): {e}")
            raise

    def select_all(self):
        if self.select_all_header.is_visible():
            log.debug("Seleccionando todas las filas de la tabla...")
            self.select_all_header.click()
        else:
            log.warning("El botón para seleccionar todas las filas no está visible.")

    def click_toolbar_button(self, button_name: str, exact: bool = True):
        try:
            button_locator = self._component_locator.get_by_role("button", name=button_name, exact=exact)
            button_locator.click()
            log.debug(f"Clic en el botón '{button_name}' realizado con éxito.")
        except Exception as e:
            log.error(f"No se pudo hacer clic en el botón '{button_name}': {e}")
            raise