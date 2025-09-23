# pages/sap_page_base.py

import logging
from typing import Any, Literal, Optional
from .page_base import expect, PageBase, Locator, PlaywrightTimeoutError
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
        # Elementos comunes específicos de la UI de SAP

        # TODO ¿Meter un try except y lanzar un error si no encuentra el locator?

        # Locator específico y robusto para la barra de estado de SAP
        self.status_bar_old = self.playwright_page.locator(self._provider.get('common.status_bar'))
        self.status_bar = self.playwright_page.locator("#wnd\\[0\\]\\/sbar_msg")

        self.execute_button = self.playwright_page.locator(self._provider.get('common.ejecutar'))
        self.trx_code_input = self.playwright_page.locator(self._provider.get('common.trx_code_input'))

        # Indicador de carga (loading box) que aparece en muchas pantallas SAP
        self.load_indicator = self.playwright_page.locator(self._provider.get('common.cargando'))

        # Formulario principal de prácticamente todas las pantallas SAP
        self.form = self.playwright_page.locator(self._provider.get('common.form_principal'))

        # Barra de comandos (command bar) donde se introduce el código de transacción
        self.command_bar = self.playwright_page.get_by_role("combobox", name="Indicar código de transacción")

    # --- MÉTODO MOVIDO AQUÍ ---
    def wait_for_command_bar(self, timeout: int = 5000):
        """
        Espera de forma robusta a que la barra de comandos esté visible y habilitada.
        """
        log.debug("Esperando a que la barra de comandos esté lista...")
        
        # Usamos 'expect' que espera automáticamente a que la condición se cumpla.
        expect(self.command_bar).to_be_visible(timeout=timeout)
        expect(self.command_bar).to_be_editable(timeout=timeout)
        
        log.debug("Barra de comandos lista.")

    def execute(self):
        """Hace clic en el botón 'Ejecutar' (F8) de SAP."""
        self.execute_button.click()

    def wait_for_page_to_be_ready(self, timeout: int = 30000):
        """
        Espera a que el indicador de carga principal de SAP desaparezca.
        Esto indica que la página ha terminado de cargar y está interactiva.
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
        log.info("Esperando a que el formulario principal esté visible...")
        try:
            self.form.wait_for(state="visible", timeout=timeout)
            log.info("Formulario principal visible.")
        except Exception as e:
            log.warning(f"No se encontró el formulario principal: {e}")


    def gestionar_dialogo_emergente(self, button_text: str, timeout: int = 3000):
        """
        Método guardián GENÉRICO que busca un diálogo emergente y hace clic en un
        botón con el texto especificado. No falla si no lo encuentra.

        Args:
            button_text: El texto exacto del botón en el que hacer clic (ej: "Continuar", "Aceptar", "Cancelar").
            timeout: Tiempo máximo de espera para el botón.
        """
        try:
            # El selector ahora es DINÁMICO. Construye el locator usando
            # el texto del botón que le pasas como parámetro.
            locator = self.playwright_page.locator(f"role=dialog >> role=button[name='{button_text}']")
            
            locator.click(timeout=timeout)
            log.info(f"Diálogo emergente con botón '{button_text}' detectado y gestionado.")
        except TimeoutError:
            log.debug(f"No se encontró diálogo emergente con botón '{button_text}'.")
            pass

    # ==========================================================
    # MÉTODOS DE LA BARRA DE ESTADO (Status Bar)
    # ==========================================================

    def get_status_bar_text(self) -> str:
        """Espera y devuelve el texto de la barra de estado de SAP."""
        self.status_bar.wait_for(state="visible")
        return self.status_bar.inner_text()

    def get_status_bar_message(self) -> Optional[str]:
        """
        Espera a que aparezca un mensaje en la barra de estado y devuelve su texto.
        Devuelve None si no aparece ningún mensaje en el tiempo de espera.
        """
        try:
            # Usamos el locator que apunta a la barra de estado
            self.status_bar.wait_for(state="visible", timeout=2500)
            
            # El texto completo suele estar en el atributo 'title'
            return self.status_bar.get_attribute("title")
        except PlaywrightTimeoutError:
            log.debug("No se encontraron mensajes en la status bar.")
            return None

    def check_status_bar_for_message_type(self, 
        message_type: Literal["Error", "Warning", "Success", "Info"]
    ) -> Optional[str]:
        """
        Comprueba si la barra de estado muestra un mensaje de un tipo específico.
        Devuelve el texto del mensaje si coincide, si no, devuelve None.

        Args:
            message_type: El tipo de mensaje a buscar ('Error', 'Warning', etc.).
        """
        try:
            status_bar = self.playwright_page.locator("#wnd\\[0\\]\\/sbar_msg")
            status_bar.wait_for(state="visible", timeout=2500)

            class_attribute = status_bar.get_attribute("class") or ""
            
            # Comprobamos si la clase del elemento contiene el tipo de mensaje
            if f"--{message_type}" in class_attribute:
                message_text = status_bar.get_attribute("title")
                log.info(f"Detectado mensaje de tipo '{message_type}': '{message_text}'")
                return message_text
            
            return None
        except PlaywrightTimeoutError:
            return None