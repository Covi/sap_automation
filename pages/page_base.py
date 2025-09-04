# core/PageBase.py
# Page Object base class for Playwright

from playwright.sync_api import Page
from config import SAP_BASE_URL

class PageBase:
    """
    Clase base para todas las Page Objects.
    """
    def __init__(self, page: Page):
        if not isinstance(page, Page):
            raise TypeError("Se esperaba un objeto Page de Playwright.")
        self.page = page
        self.base_url = SAP_BASE_URL

    def navigate(self, path: str = ""):
        """
        Navega a la URL base más la ruta específica.
        """
        full_url = self.base_url + path
        self.page.goto(full_url)

    def get_title(self) -> str:
        """
        Devuelve el título de la página actual.
        """
        return self.page.title()