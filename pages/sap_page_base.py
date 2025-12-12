# pages/sap_page_base.py (ACTUALIZADO CON MEJOR DEPURACIÓN)

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

        # Locator específico y robusto para la barra de estado de SAP
        self.status_bar_old = self.playwright_page.locator(self._provider.get('common.status_bar'))
        # Aseguramos el uso del locator robusto
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
        """
        log.info("Esperando a que la página esté completamente cargada y sin bloqueos...")
        
        # 1. FASE DE DETECCIÓN (T1): Esperamos a que el bloqueador aparezca.
        # Este timeout es de detección (lo hemos aumentado a 10s para evitar el error de 2s)
        DETECTION_TIMEOUT = 10000 
        try:
            self.load_indicator.wait_for(state='visible', timeout=DETECTION_TIMEOUT) 
            log.debug("Indicador de carga detectado, esperando a que desaparezca.")
            
        # Utilizamos la excepción específica para ser robustos.
        except PlaywrightTimeoutError: 
            # Si no aparece en 10s, asumimos que la página ya estaba lista.
            log.debug(f"No se detectó indicador de carga en {DETECTION_TIMEOUT/1000}s, la página parece estar lista.")
            return

        # 2. FASE DE EJECUCIÓN (T2): Esperamos a que desaparezca.
        # Aquí sí usamos el 'timeout' que pasa la función (el timeout total de la transacción).
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


    def gestionar_dialogo_emergente(self, button_text: str, timeout: int = 3000):
        """
        Método guardián GENÉRICO que busca un diálogo emergente y hace clic en un
        botón con el texto especificado. No falla si no lo encuentra.

        Args:
            button_text: El texto exacto del botón en el que hacer clic (ej: "Continuar", "Aceptar", "Cancelar").
            timeout: Tiempo máximo de espera para el botón.
        TODO ¿Se está usando???
        """
        try:
            # El selector ahora es DINÁMICO. Construye el locator usando
            # el texto del botón que le pasas como parámetro.
            locator = self.playwright_page.locator(f"role=dialog >> role=button[name='{button_text}']")
            
            locator.click(timeout=timeout)
            log.info(f"Diálogo emergente con botón '{button_text}' detectado y gestionado.")
        except PlaywrightTimeoutError:
            log.debug(f"No se encontró diálogo emergente con botón '{button_text}'.")
            pass

    # ==========================================================
    # MÉTODOS DE LA BARRA DE ESTADO (Status Bar)
    # ==========================================================

    def get_status_bar_message(self) -> Optional[str]:
        """
        ÁTOMO 1: Obtiene el mensaje completo de la barra de estado.
        Gestiona la espera (wait_for) y la extracción del atributo 'title' (texto completo).
        """
        try:
            # Centralizamos aquí el timeout y la espera de visibilidad
            self.status_bar.wait_for(state="visible", timeout=2500)
            
            # Devolvemos el title, que en SAP contiene el texto completo sin cortar
            return self.status_bar.get_attribute("title")
        except PlaywrightTimeoutError:
            # Si falla la espera, asumimos que no hay mensaje
            return None

    def check_status_bar_for_message_type(self, 
        message_type: Literal["Error", "Warning", "Success", "Info"]
    ) -> Optional[str]:
        """
        COMPOSICIÓN: Usa 'get_status_bar_message' para obtener el texto y luego
        valida si el tipo (color/clase) coincide con lo esperado.
        """
        # 1. REUTILIZACIÓN: Llamamos al átomo para obtener el texto y gestionar la espera.
        message_text = self.get_status_bar_message()

        # Si el átomo devolvió None (timeout o no visible), salimos inmediatamente.
        if message_text is None:
            return None

        # 2. Lógica específica de ESTE método: Validar la clase CSS (el tipo de mensaje)
        # Como get_status_bar_message ya aseguró que es visible, podemos pedir el atributo class directamente.
        # Obtenemos datos para validación y debug
        class_attribute = self.status_bar.get_attribute("class") or ""
        message_text = self.get_status_bar_message() # Aquí obtenemos el texto y se espera 2.5s

        # Debug completo reutilizando el texto que ya obtuvimos
        log.debug(f"Status Bar -> Clase: '{class_attribute}' | Mensaje: '{message_text}'")

        # 3. Verificación
        if f"--{message_type}" in class_attribute:
            log.info(f"Mensaje '{message_type}' confirmado: {message_text}")
            return message_text

        return None

    # OPCIONAL: Si quieres mantener este método por compatibilidad, 
    # redefínelo para que use también el método bueno y evites el bug de 'inner_text'
    def get_status_bar_text(self) -> str:
        """Alias o wrapper simple. Si falla, devuelve cadena vacía para no romper tipos."""
        val = self.get_status_bar_message()
        return val if val else ""