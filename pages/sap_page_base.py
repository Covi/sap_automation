# pages/sap_page_base.py

import logging
from .page_base import PageBase, Locator, PlaywrightTimeoutError
from core.providers.locators.base_locator_provider import BaseLocatorProvider

log = logging.getLogger(__name__)

class SAPPageBase(PageBase):
    """
    Clase base especializada para páginas de SAP.
    Introduce la dependencia del locator_provider y define elementos/métodos comunes de SAP.
    """
    def __init__(self, page, locator_provider: BaseLocatorProvider):
        super().__init__(page)
        self._provider = locator_provider

        # ==========================================================
        # LOCATORS

        # Elementos comunes específicos de la UI de SAP
        self.status_bar = self.playwright_page.locator(self._provider.get('common.status_bar'))
        self.execute_button = self.playwright_page.locator(self._provider.get('common.ejecutar'))
        self.trx_code_input = self.playwright_page.locator(self._provider.get('common.trx_code_input'))

        # Indicador de carga (loading box) que aparece en muchas pantallas SAP
        self.load_indicator = self.playwright_page.locator(self._provider.get('common.cargando'))

        # Formulario principal de prácticamente todas las pantallas SAP
        self.form = self.playwright_page.locator(self._provider.get('common.form_principal'))
        # ==========================================================


    # --- Métodos de Acción Específicos de SAP ---
    
    def get_status_bar_text(self) -> str:
        """Espera y devuelve el texto de la barra de estado de SAP."""
        self.status_bar.wait_for(state="visible")
        return self.status_bar.inner_text()

    def execute(self):
        """Hace clic en el botón 'Ejecutar' (F8) de SAP."""
        self.execute_button.click()

    def wait_for_page_to_be_ready(self, timeout: int = 30000):
        """
        Espera a que el indicador de carga principal de SAP desaparezca.
        Esto indica que la página ha terminado de cargar y está interactiva.
        FIXME Esto no está funcionando bien en todas las pantallas.
        """
        log.info("Esperando a que la página esté completamente cargada y sin bloqueos...")
        try:
            # Esperamos a que el bloqueador aparezca primero (puede ser instantáneo)
            self.load_indicator.wait_for(state='visible', timeout=2000)
            log.debug("Indicador de carga detectado, esperando a que desaparezca.")
        except Exception:
            # Si no aparece en 2s, asumimos que la página ya estaba lista.
            log.debug("No se detectó indicador de carga, la página parece estar lista.")
            return

        # Ahora esperamos a que desaparezca
        self.load_indicator.wait_for(state='hidden', timeout=timeout)
        log.info("Indicador de carga ha desaparecido. La página está lista.")

    def wait_for_form(self, timeout: int = 10000):
        """
        Espera a que el formulario principal esté visible.
        Úsalo solo si la página realmente tiene formulario.
        """
        # FIXME Aquí self.form no es un locator sino nuestro objeto SAPFormComponent, 
        # porque se hereda desde sap_report_page.py. Hay que solucionarlo.
        log.info(f"Esperando a que el formulario principal esté visible... {self.form}")
        try:
            self.form.wait_for(state="visible", timeout=timeout)
            log.info("Formulario principal visible.")
        except Exception as e:
            log.warning(f"No se encontró el formulario principal: {e}")