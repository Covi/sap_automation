# Fichero: pages/iq09_page.py

from playwright.sync_api import Download, TimeoutError, Error
from core.sap_page_base import SAPPageBase
from core.providers.base_provider import BaseLocatorProvider
from data_models.iq09_models import Iq09FormData
from utils.logger import log

# 1. Se importan los dos componentes que vamos a usar
from core.components.sap_menu_component import SAPMenuComponent
from core.components.sap_menu_export_dialog import SAPMenuExportDialog

class Iq09Page(SAPPageBase):
    def __init__(self, page, locator_provider: BaseLocatorProvider):
        super().__init__(page, locator_provider)

        # --- Locators propios de la página (sin cambios) ---
        self.centro_input = page.locator(locator_provider.get('form.centro'))
        self.n_serie_input = page.locator(locator_provider.get('form.n_serie'))
        self.results_table = page.locator(locator_provider.get('results.tabla_resultados'))

        # --- 2. Se instancian los componentes expertos ---
        self.menu = SAPMenuComponent(self.page)
        self.export_dialog = SAPMenuExportDialog(self.page, locator_provider)

        # --- Mapa del Formulario (sin cambios) ---
        self.form_map = {
            'centro': self.centro_input,
            'n_serie': self.n_serie_input,
        }

    # Los métodos rellenar_formulario, ejecutar_informe, y is_results_table_visible
    # se quedan exactamente igual.
    def rellenar_formulario(self, data: Iq09FormData):
        log.info("Rellenando el formulario de la transacción IQ09.")
        self._fill_form(self.form_map, data)

    def ejecutar_informe(self):
        log.info("Ejecutando el informe de IQ09.")
        self.execute()
        self.results_table.wait_for()
        log.debug("Tabla de resultados de IQ09 visible.")

    def is_results_table_visible(self) -> bool:
        return self.results_table.is_visible()

    def descargar_informe(self) -> Download:
        """
        3. El método de descarga ahora orquesta los componentes para realizar el trabajo.
        """
        log.info("Iniciando descarga para IQ09 a través del menú SAP...")
        try:
            # Primero, usamos el componente de menú para navegar y abrir el diálogo.
            # La ruta la sacamos del 'record' que nos diste.
            self.menu.navigate_to("Menú", "Lista", "Grabar", "Fichero...")
            
            # Segundo, usamos el componente de diálogo para gestionar la exportación.
            # Este método ya se encarga de esperar la descarga y devolverla.
            return self.export_dialog.exportar_como_spreadsheet()
            
        except (TimeoutError, Error) as e:
            log.error(f"El proceso de descarga para IQ09 ha fallado: {e}")
            raise