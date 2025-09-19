# core/protocols/closing_strategy_protocol.py

from typing import Protocol, Optional
from playwright.sync_api import Browser, Page
# Importamos el otro protocolo porque este lo usa en la firma de su método
from core.protocols.browser_factory_protocol import BrowserFactory

class ClosingStrategy(Protocol):
    """
    Define el contrato para cualquier estrategia de cierre del navegador.
    Esto permite al BrowserManager delegar la lógica de cierre, cumpliendo SRP.
    """
    def close(self, browser: Optional[Browser], page: Optional[Page], factory: BrowserFactory):
        """
        Ejecuta la lógica de cierre específica de la estrategia.
        """
        ...