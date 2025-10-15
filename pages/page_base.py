import logging
from playwright.sync_api import expect, Page, Locator, TimeoutError as PlaywrightTimeoutError
from config import BASE_URL

log = logging.getLogger(__name__)

class PageBase:
    """
    Clase base para TODAS las Page Objects. Proporciona una envoltura
    robusta sobre el objeto Page de Playwright y métodos de utilidad genéricos.
    """
    def __init__(self, page: Page):
        if not isinstance(page, Page):
            raise TypeError("Se esperaba un objeto Page de Playwright.")
        self.page = page
        self.base_url = BASE_URL

    @property
    def playwright_page(self) -> Page:
        """Propiedad que expone de forma segura el objeto Page de Playwright."""
        return self.page

    # --- Métodos Genéricos de Interacción ---

    def navigate(self, path: str = ""):
        """Navega a la URL base más la ruta específica."""
        full_url = self.base_url + path
        log.info(f"Navegando a: {full_url}")
        self.playwright_page.goto(full_url)

    def get_title(self) -> str:
        """Devuelve el título de la página actual (<title> del head)."""
        return self.playwright_page.title()

    def pause(self):
        """Pausa la ejecución para debugging con el inspector de Playwright."""
        log.debug("Pausando la ejecución...")
        self.playwright_page.pause()

    # --- Métodos de Interacción Mejorados ---

    def robust_click(self, locator: Locator, timeout: int = 5000):
        """
        Realiza un clic de forma segura, esperando primero a que el elemento
        sea visible y esté habilitado para recibir eventos de clic.
        """
        expect(locator).to_be_visible(timeout=timeout)
        expect(locator).to_be_enabled(timeout=timeout)
        locator.click()

    def clear_and_fill(self, locator: Locator, text: str, timeout: int = 5000):
        """
        Limpia un campo de texto y luego escribe en él, asegurando que no
        queden valores residuales.
        """
        expect(locator).to_be_editable(timeout=timeout)
        locator.clear()
        locator.fill(text)

    def press_key(self, key: str):
        """
        Presiona una tecla del teclado (ej: "Enter", "Escape", "ArrowDown").
        """
        log.debug(f"Pulsando la tecla: {key}")
        self.playwright_page.keyboard.press(key)

    def scroll_to_element(self, locator: Locator):
        """
        Hace scroll hasta que un elemento sea visible en la pantalla.
        """
        locator.scroll_into_view_if_needed()

    # --- Métodos de Verificación de Estado (Aserciones) ---

    def is_element_visible(self, locator: Locator, timeout: int = 3000) -> bool:
        """
        Comprueba si un elemento es visible en la página, esperando un corto periodo.
        """
        try:
            locator.wait_for(state="visible", timeout=timeout)
            return True
        except PlaywrightTimeoutError:
            return False

    def verify_text_in_element(self, locator: Locator, expected_text: str, timeout: int = 5000):
        """
        Verifica que un elemento contiene exactamente el texto esperado.
        """
        expect(locator).to_have_text(expected_text, timeout=timeout)
        log.info(f"Verificación de texto exitosa. Encontrado: '{expected_text}'.")
        
    def get_element_text(self, locator: Locator) -> str:
        """
        Obtiene el texto de un elemento, esperando primero a que sea visible.
        """
        expect(locator).to_be_visible()
        return locator.inner_text()