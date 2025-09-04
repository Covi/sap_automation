# pages/iq09_page.py

from typing import Any
from playwright.sync_api import Download, TimeoutError, Error
# El import de la clase base es correcto.
from .sap_page_base import SAPPageBase
from data_models.iq09_models import Iq09FormData
from utils.logger import log

# Componentes
from core.components.sap_form_component import SAPFormComponent
from core.components.sap_form_strategies import SimpleFillStrategy
from core.components.sap_menu_component import SAPMenuComponent
from core.components.sap_menu_export_dialog import SAPMenuExportDialog

class Iq09Page(SAPPageBase):
    def __init__(self, page, locator_provider: Any):
        # La llamada al constructor padre sigue siendo necesaria y correcta.
        super().__init__(page, locator_provider)

        # --- Locators propios de la página ---
        # CAMBIO: Usamos la propiedad heredada 'self.playwright_page' para crear
        # locators, igual que hicimos en la clase base. Más consistente.
        self.centro_input = self.playwright_page.locator(self._provider.get('form.centro'))
        self.n_serie_input = self.playwright_page.locator(self._provider.get('form.n_serie'))
        self.results_table = self.playwright_page.locator(self._provider.get('results.tabla_resultados'))

        # --- Componentes ---
        # CAMBIO CLAVE: La instanciación de componentes ahora es mucho más limpia.
        # Simplemente les pasamos 'self' (la propia instancia de Iq09Page) como contexto.
        self.form = SAPFormComponent(self)
        self.menu = SAPMenuComponent(self)
        self.export_dialog = SAPMenuExportDialog(self)

        # --- Mapa del Formulario ---
        self.form_map = {
            'centro': self.centro_input,
            'n_serie': self.n_serie_input,
        }

    def rellenar_formulario(self, data: Iq09FormData):
        # Este método no necesita cambios, ya que delega en el componente 'form'.
        self.form.fill_form(data, self.form_map, strategy=SimpleFillStrategy())

    def ejecutar_informe(self):
        # Este método no necesita cambios, ya que usa 'execute' heredado.
        log.info("Ejecutando el informe de IQ09.")
        self.execute()
        self.results_table.wait_for()
        log.debug("Tabla de resultados de IQ09 visible.")

    def is_results_table_visible(self) -> bool:
        # Este método no necesita cambios.
        return self.results_table.is_visible()

    def descargar_informe(self) -> Download:
        # Este método no necesita cambios, ya que delega en los componentes.
        log.info("Iniciando descarga para IQ09 a través del menú SAP...")
        try:
            self.menu.navigate_to("Menú", "Lista", "Grabar", "Fichero...")
            return self.export_dialog.exportar_como_spreadsheet()
        except (TimeoutError, Error) as e:
            log.error(f"El proceso de descarga para IQ09 ha fallado: {e}")
            raise