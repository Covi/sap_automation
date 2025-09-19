# core/strategies/browser_closing_strategies.py

import logging
from typing import Optional
from playwright.sync_api import Browser, Page
from core.protocols.browser_factory_protocol import BrowserFactory

log = logging.getLogger(__name__)

class TransientClosingStrategy:
    """
    Estrategia que cierra todo: página, navegador y fábrica.
    Para ejecuciones que no necesitan persistencia.
    """
    def close(self, browser: Optional[Browser], page: Optional[Page], factory: BrowserFactory):
        log.info("Estrategia Transitoria: Cerrando todos los recursos...")
        if page and not page.is_closed():
            page.close()
        if browser and browser.is_connected():
            browser.close()
        factory.stop()

class PersistentClosingStrategy:
    """
    Estrategia que mantiene el navegador y la fábrica abiertos.
    Ideal para depuración o ejecuciones manuales rápidas.
    """
    def close(self, browser: Optional[Browser], page: Optional[Page], factory: BrowserFactory):
        log.info("Estrategia Persistente: El navegador y la fábrica permanecerán abiertos.")
        if page and not page.is_closed():
            page.close() # Opcional: podrías querer cerrar solo la página