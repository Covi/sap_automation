# core/browser_manager.py (VERSIÓN FINAL Y DEFINITIVA)

import logging
from typing import Optional
from playwright.sync_api import Browser, Page, BrowserContext

# Importaciones de los protocolos que hemos definido
from core.protocols.browser_factory_protocol import BrowserFactory
from core.protocols.closing_strategy_protocol import ClosingStrategy

log = logging.getLogger(__name__)

class BrowserManager:
    """
    Gestiona el ciclo de vida de un navegador y sus contextos.
    Usa el patrón Strategy para el cierre y permite la persistencia de sesión.
    """
    def __init__(
        self,
        factory: BrowserFactory,
        closing_strategy: ClosingStrategy,
        headless: bool = True
    ):
        self.factory = factory
        self.closing_strategy = closing_strategy
        self.headless = headless
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None

    def start_browser_with_session(self, storage_state_path: Optional[str] = None) -> Page:
        """
        Inicia el navegador y crea una página dentro de un contexto.
        Carga el estado de la sesión si se proporciona la ruta.
        """
        if not self._browser or not self._browser.is_connected():
            self._browser = self.factory.create_browser(self.headless)

        self._context = self._browser.new_context(storage_state=storage_state_path)
        self._page = self._context.new_page()
        
        return self._page

    def save_session(self, storage_state_path: str):
        """Guarda el estado de la sesión del contexto actual en un fichero."""
        if self._context:
            self._context.storage_state(path=storage_state_path)
            log.info(f"Estado de la sesión guardado en {storage_state_path}")
        else:
            log.warning("No hay un contexto activo para guardar la sesión.")

    def close_browser(self):
        """
        Delega la operación de cierre a la estrategia configurada.
        """
        self.closing_strategy.close(self._browser, self._page, self.factory)
        # Limpiamos referencias por si la estrategia persistente no las cierra.
        if self._browser and not self._browser.is_connected():
            self._browser = None
        if self._page and self._page.is_closed():
            self._page = None