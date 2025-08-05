# core/browser_manager.py
# Módulo para gestionar el navegador y la página con Playwright.

from playwright.sync_api import sync_playwright, Browser, Page

class BrowserManager:
    """
    Gestiona el ciclo de vida del navegador y la página con Playwright.
    """
    def __init__(self, headless: bool = True):
        self._playwright = None
        self._browser = None
        self._page = None
        self.headless = headless

    def start_browser(self) -> Page:
        """
        Inicia Playwright, lanza un navegador y crea una nueva página.
        """
        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch(headless=self.headless)
        self._page = self._browser.new_page()
        return self._page

    def close_browser(self):
        """
        Cierra el navegador y detiene Playwright si están activos.
        """
        if self._page and not self._page.is_closed():
            self._page.close()
        if self._browser and self._browser.is_connected():
            self._browser.close()
        if self._playwright:
            self._playwright.stop()