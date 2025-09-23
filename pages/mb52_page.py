import logging
from typing import Any, Dict, Optional

from playwright.sync_api import Download, TimeoutError, Error

from pages.sap_report_page import SAPReportPage

# Componentes y Estrategias
from core.components.form.sap_form_strategies import SimpleFillStrategy, FormFillingStrategy
from core.components.dialog.sap_export_dialog import SAPExportDialog

log = logging.getLogger(__name__)

class MB52Page(SAPReportPage):
    """
    Page Object Model para la transacción MB52 de SAP.
    Hereda la lógica común de informes de SAPReportPage.
    """
    def __init__(self, page, locator_provider: Any):
        """
        Inicializa la página, sus componentes y los locators específicos.
        """
        super().__init__(page, locator_provider)

        # --- Definición de componentes y locators específicos de MB52 ---
        self.results_table = self.playwright_page.locator(self._provider.get('results.tabla_resultados'))
        self.download_button = self.playwright_page.locator(self._provider.get('buttons.descargar_hoja'))
        
        # Locator para el botón 'Continuar' que puede aparecer en pop-ups
        self.continuar_button = self.playwright_page.locator(self._provider.get('common.continuar'))
        
        # Locator específico y robusto para la barra de estado de SAP
        self.error_bar_selector = self.playwright_page.locator("#wnd\\[0\\]\\/sbar_msg")

        # Componente para gestionar el diálogo de exportación
        self.export_dialog = SAPExportDialog(self)

    # --- Implementación de las propiedades abstractas obligatorias ---

    @property
    def form_locators(self) -> Dict[str, Any]:
        """Provee el mapa de locators del formulario para la clase base."""
        return {
            'material': self.playwright_page.locator(self._provider.get('form.material')),
            'centro': self.playwright_page.locator(self._provider.get('form.centro')),
            'almacen': self.playwright_page.locator(self._provider.get('form.almacen'))
        }

    @property
    def fill_strategy(self) -> FormFillingStrategy:
        """Provee la estrategia de rellenado para la clase base."""
        return SimpleFillStrategy()

    # --- Implementación de los métodos abstractos obligatorios ---

    def esperar_resultados(self, timeout: int = 30000):
        """
        Implementa la lógica de espera específica de MB52.
        La responsabilidad de este método es pausar la ejecución hasta que la
        tabla de resultados esté visible, o fallar si se excede el timeout.
        """
        self.results_table.wait_for(state="visible", timeout=timeout)

    def is_results_table_visible(self) -> bool:
        """
        Comprueba de forma instantánea si la tabla de resultados del informe está visible.
        Devuelve True o False sin esperar.
        """
        return self.results_table.is_visible()

    # --- Métodos específicos de la página ---

    def descargar_hoja_calculo(self, fichero_de_salida_nombre: str) -> Download:
        """
        Orquesta la descarga abriendo el diálogo y delegando su gestión al componente.
        """
        try:
            with self.playwright_page.expect_download() as download_info:
                self.download_button.click()
                self.export_dialog.completar_dialogo(fichero_de_salida_nombre)
            return download_info.value
        except (TimeoutError, Error) as e:
            log.error(f"El proceso de descarga para MB52 ha fallado: {e}")
            raise

    def gestionar_posible_popup_continuar(self):
        """
        Método guardián. Busca un pop-up de 'Continuar' y hace clic si existe.
        No falla si no lo encuentra, permitiendo un flujo robusto.
        """
        try:
            # Intentamos hacer clic con un timeout muy bajo para no bloquear el script.
            self.continuar_button.click(timeout=1500)
            log.info("Pop-up 'Continuar' detectado y gestionado.")
        except TimeoutError:
            # Esto es lo esperado si el pop-up no aparece. No es un error.
            log.debug("No se encontró pop-up de 'Continuar', se sigue el flujo normal.")
            pass # Silenciamos el error de timeout y continuamos

    def obtener_error_de_status_bar(self) -> Optional[str]:
        """
        Busca un mensaje de validación en la barra de estado de SAP.
        Devuelve el texto del error o None si no se encuentra ninguno.
        """
        try:
            # Esperamos un momento corto por si el mensaje tarda en aparecer
            error_element = self.error_bar_selector
            error_element.wait_for(state="visible", timeout=2500)

            # El texto completo del error suele estar en el atributo 'title'
            error_text = error_element.get_attribute("title")
            if error_text:
                log.warning(f"Detectado error de SAP en la status bar: '{error_text}'")
                return error_text
            
            return "Se detectó un error en la barra de estado, pero no se pudo extraer el texto."

        except TimeoutError:
            log.debug("No se encontraron mensajes de error en la status bar.")
            return None