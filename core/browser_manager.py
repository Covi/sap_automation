# core/browser_manager.py
# Módulo para gestionar el navegador y la página con Playwright.

from playwright.sync_api import sync_playwright, Browser, Page

class BrowserManager:
    """
    Gestiona el ciclo de vida del navegador y la página con Playwright.
    Permite elegir el tipo de navegador y si se ejecuta en headless.
    """
    def __init__(self, browser_type: str = "firefox", headless: bool = True):
        self._playwright = None
        self._browser = None
        self._page = None
        self.headless = headless
        self.browser_type = browser_type  # "firefox", "chromium" o "webkit"

    def start_browser(self) -> Page:
        """
        Inicia Playwright, lanza el navegador elegido y crea una nueva página.
        """
        self._playwright = sync_playwright().start()

        if self.browser_type == "firefox":
            self._browser = self._playwright.firefox.launch(headless=self.headless)
        elif self.browser_type == "chromium":
            self._browser = self._playwright.chromium.launch(headless=self.headless)
        elif self.browser_type == "webkit":
            self._browser = self._playwright.webkit.launch(headless=self.headless)
        else:
            raise ValueError(f"Navegador desconocido: {self.browser_type}")

        self._page = self._browser.new_page()
        return self._page

    def close_browser(self):
        """
        Cierra la página y el navegador, y detiene Playwright.
        """
        if self._page and not self._page.is_closed():
            self._page.close()
        if self._browser and self._browser.is_connected():
            self._browser.close()
        if self._playwright:
            self._playwright.stop()
