# pages/page_base.py

# FIXME Debemos abstraernos de Playwright?
# por type hiting los no usados
from playwright.sync_api import Page, Locator, TimeoutError as PlaywrightTimeoutError
from config import BASE_URL

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

    # FIXME Debemos abstraernos de Playwright?
    @property
    def playwright_page(self) -> Page:
        """Propiedad que expone de forma segura el objeto Page de Playwright."""
        return self.page

    # --- Métodos Genéricos de Interacción ---
    # FIXME Debemos abstraernos de Playwright?
    def navigate(self, path: str = ""):
        """Navega a la URL base más la ruta específica."""
        full_url = self.base_url + path
        self.playwright_page.goto(full_url)

    def get_title(self) -> str:
        """Devuelve el título de la página actual."""
        return self.playwright_page.title()

    def accept(self):
        """Teclea Enter. Es una acción genérica."""
        self.playwright_page.keyboard.press("Enter")

    def pause(self):
        """Pausa la ejecución. Es una utilidad de debugging genérica."""
        self.playwright_page.pause()