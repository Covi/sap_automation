# core/factories/playwright_browser_factory.py

from typing import Optional
from playwright.sync_api import sync_playwright, Browser, Playwright
# Sugerencia 1: Hacemos explícito que implementamos este protocolo
from core.protocols.browser_factory_protocol import BrowserFactory

class PlaywrightBrowserFactory:
    """Fábrica concreta que lanza navegadores usando Playwright."""
    def __init__(self, browser_type: str = "firefox"):
        self.browser_type = browser_type
        self._playwright: Optional[Playwright] = None

    def create_browser(self, headless: bool) -> Browser:
        self._playwright = sync_playwright().start()
        browser_launcher = getattr(self._playwright, self.browser_type, None)

        # Sugerencia 2: Patrón "Guard Clause". Manejamos el error primero.
        if not browser_launcher:
            self.stop()
            raise ValueError(f"Navegador desconocido o no soportado: {self.browser_type}")

        # Si todo va bien, continuamos con el "camino feliz".
        return browser_launcher.launch(headless=headless)

    def stop(self):
        if self._playwright:
            self._playwright.stop()
            self._playwright = None