# core/protocols/browser_factory_protocol.py

from typing import Protocol
from playwright.sync_api import Browser

class BrowserFactory(Protocol):
    """
    Protocolo para una fábrica de navegadores. Permite la inversión de dependencias.
    """
    def create_browser(self, headless: bool) -> Browser:
        ...

    def stop(self):
        """Detiene los recursos gestionados por la fábrica."""
        ...