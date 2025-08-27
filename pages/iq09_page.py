# Fichero: pages/iq09_page.py
# Página para la transacción IQ09, especializada en la visualización de números de serie.

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

        # --- Mapa del Formulario ---
        # Asocia los nombres de campo del modelo de datos con los locators de la página
        self.form_map = {
            'centro': self.centro_input,
            'n_serie': self.n_serie_input,
            # Añade aquí otras asociaciones si tu modelo de datos crece
        }

    def rellenar_formulario(self, data: Iq09FormData):
        """
        Rellena el formulario de IQ09 con los datos proporcionados.
        """
        log.info("Rellenando el formulario de la transacción IQ09.")
        self._fill_form(self.form_map, data)

    def ejecutar_informe(self):
        """
        Pulsa el botón de ejecutar (F8) y espera a que aparezcan los resultados.
        """
        log.info("Ejecutando el informe de IQ09.")
        self.execute() # Método heredado que pulsa el botón común de ejecutar

        # Esta es la espera clave. Asume que tras ejecutar, debe aparecer una tabla.
        # Si el comportamiento de IQ09 es diferente, habría que ajustar esta línea.
        self.results_table.wait_for()
        log.info("Tabla de resultados de IQ09 visible.")

    def is_results_table_visible(self) -> bool:
        """Comprueba si la tabla de resultados del informe está visible."""
        return self.results_table.is_visible()

    # NOTA: He incluido un método de descarga genérico basado en el de MB52.
    # Si IQ09 no necesita descargas o el proceso es diferente, se puede modificar o eliminar.
    def descargar_informe(self, fichero_de_salida_nombre: str) -> Download:
        """
        Orquesta la interacción UI para iniciar la descarga y devuelve el objeto Download.
        Este método es un placeholder y puede necesitar ajustes para IQ09.
        """
        log.warning("El método de descarga para IQ09 es un placeholder y puede necesitar ajustes.")
        try:
            # Asumimos que los locators para la descarga son los mismos que en MB52 por ahora
            download_button = self.page.locator("[id='M0:48::btn[43]']") # Placeholder
            filename_input = self.page.locator("[id='M1:46:1::1:17']") # Placeholder
            ok_button = self.page.locator("[id='M1:49::btn[0]']") # Placeholder

            with self.page.expect_download() as download_info:
                download_button.click()
                filename_input.fill(fichero_de_salida_nombre)
                filename_input.press("Enter")
                # ... aquí podrían ir más pasos si el diálogo de IQ09 es más complejo ...
                ok_button.click()

            return download_info.value
        except (TimeoutError, Error) as e:
            log.error(f"El proceso de descarga para IQ09 ha fallado: {e}")
            raise