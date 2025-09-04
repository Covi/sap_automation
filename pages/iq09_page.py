from typing import Any
from playwright.sync_api import Download, TimeoutError, Error

# El import de la clase base es correcto.
from .sap_page_base import SAPPageBase
from data_models.iq09_models import Iq09FormData
from utils.logger import log

# Componentes
from core.components.form.sap_form_component import SAPFormComponent
from core.components.form.sap_form_strategies import SimpleFillStrategy
from core.components.menu.sap_menu_component import SAPMenuComponent
from core.components.dialog.sap_menu_export_dialog import SAPMenuExportDialog

class Iq09Page(SAPPageBase):
    def __init__(self, page, locator_provider: Any):
        # La llamada al constructor padre sigue siendo necesaria y correcta.
        super().__init__(page, locator_provider)

        # --- Locators propios de la página ---
        # Ahora el locator de la tabla de resultados se crea aquí,
        # pero los otros se inyectan en los componentes.
        # FIXME estamos usando playwright_page directamente, hay que usar el provider
        self.results_table = self.playwright_page.locator(self._provider.get('results.tabla_resultados'))

        # --- Componentes ---
        # CAMBIO CLAVE: La instanciación de componentes ahora es mucho más limpia.
        # Simplemente les pasamos 'self' (la propia instancia de Iq09Page) como contexto.
        self.form = SAPFormComponent(self)
        self.menu = SAPMenuComponent(self)
        self.export_dialog = SAPMenuExportDialog(self)

        # --- Mapa del Formulario ---
        # El mapa ahora usa las referencias a los locators, que se crearán
        # cuando se acceda a las propiedades del componente 'form'.
        self.form_map = {
            'centro': self.playwright_page.locator(self._provider.get('form.centro')),
            'n_serie': self.playwright_page.locator(self._provider.get('form.n_serie')),
        }

    def rellenar_formulario(self, data: Iq09FormData):
        # Este método no necesita cambios, ya que delega en el componente 'form'.
        self.form.fill_form(data, self.form_map, strategy=SimpleFillStrategy())

    def ejecutar_informe(self):
        # Este método ahora usa el componente de formulario para ejecutar la acción,
        # en lugar de heredarla directamente de SAPPageBase.
        log.info("Ejecutando el informe de IQ09.")
        # Usa el método heredado de SAPPageBase.
        super().execute() 
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