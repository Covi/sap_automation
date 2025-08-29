# Fichero: pages/iq09_page.py

from playwright.sync_api import Download, TimeoutError, Error
from core.sap_page_base import SAPPageBase
from core.providers.base_provider import BaseLocatorProvider
from data_models.iq09_models import Iq09FormData
from utils.logger import log

class Iq09Page(SAPPageBase):
    def __init__(self, page, locator_provider: BaseLocatorProvider):
        super().__init__(page, locator_provider)

        # --- Carga de locators específicos para IQ09 ---
        self.centro_input = page.locator(locator_provider.get('form.centro'))
        self.n_serie_input = page.locator(locator_provider.get('form.n_serie'))
        self.results_table = page.locator(locator_provider.get('results.tabla_resultados'))

        # Locators para la descarga (si aplica)
        # self.download_button = page.locator(locator_provider.get('buttons.descargar_hoja'))
        # self.filename_dialog_input = page.locator(locator_provider.get('dialogs.filename_input'))
        # self.exportar_a_button = page.locator(locator_provider.get('dialogs.exportar_a'))
        # self.ok_button = page.locator(locator_provider.get('dialogs.ok_button'))

        # --- Mapa del Formulario ---
        self.form_map = {
            'centro': self.centro_input,
            'n_serie': self.n_serie_input,
        }

    def rellenar_formulario(self, data: Iq09FormData):
        log.info("Rellenando el formulario de la transacción IQ09.")
        self._fill_form(self.form_map, data)

    def ejecutar_informe(self):
        log.info("Ejecutando el informe de IQ09.")
        self.execute()
        self.results_table.wait_for()
        log.info("Tabla de resultados de IQ09 visible.")
        self.pause()  # FIXME DEBUG: Pausa para inspección manual

    def is_results_table_visible(self) -> bool:
        return self.results_table.is_visible()

    def descargar_informe(self, fichero_de_salida_nombre: str) -> Download:
        """
        Orquesta la interacción UI para iniciar la descarga usando los locators correctos.
        """
        log.info("Iniciando descarga para IQ09...")

        # try:
        #     with self.page.expect_download() as download_info:
        #         ### CAMBIO: Usamos los atributos de la clase, no strings hardcodeados ###
        #         self.download_button.click()
        #         self.filename_dialog_input.fill(fichero_de_salida_nombre)
        #         # La secuencia puede variar, aquí un ejemplo genérico
        #         # self.filename_dialog_input.press("Enter")
        #         self.exportar_a_button.click()
        #         self.ok_button.click()

        #     return download_info.value
        # except (TimeoutError, Error) as e:
        #     log.error(f"El proceso de descarga para IQ09 ha fallado: {e}")
        #     raise