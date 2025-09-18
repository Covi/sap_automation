from typing import Protocol, Any, Dict
from playwright.sync_api import Page

class BuilderProtocol(Protocol):
    def build_service(self, page: Page) -> Any:
        """Construye y devuelve el servicio listo para usar."""
        ...

    def run_service(self, service: Any, params: Dict[str, Any]) -> None:
        """Ejecuta la lógica principal de la transacción."""
        ...
