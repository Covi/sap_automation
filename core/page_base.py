# core/page_base.py
from config import SAP_BASE_URL
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.interfaces.browser_interfaces import IPage

class PageBase:
    """
    Clase base para todas las Page Objects.
    Combina tus métodos originales con utilidades adicionales.
    """
    def __init__(self, page: "IPage"):
        self.page = page
        self.base_url = SAP_BASE_URL

    # --- Tus métodos originales ---
    def navigate(self, path: str = ""):
        full_url = self.base_url + path
        self.page.goto(full_url)

    def get_title(self) -> str:
        return self.page.title()

    # --- Métodos adicionales útiles ---
    def wait_for_selector(self, selector: str, timeout: int = 5000):
        """
        Espera a que aparezca un selector en la página.
        """
        self.page.wait_for_selector(selector, timeout=timeout)

    def click(self, selector: str):
        """
        Hace clic en un elemento.
        """
        self.page.click(selector)

    def fill(self, selector: str, value: str):
        """
        Rellena un input.
        """
        self.page.fill(selector, value)
