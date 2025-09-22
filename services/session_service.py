# Fichero: services/session_service.py

import logging
from pages.sap_easy_access_page import SAPEasyAccessPage

log = logging.getLogger(__name__)

class SessionService:
    """
    Servicio para gestionar comprobaciones relacionadas con la sesión de usuario.
    """
    def __init__(self, easy_access_page: SAPEasyAccessPage):
        """
        Inicializa el servicio inyectando su dependencia, la página principal.
        """
        self._easy_access_page = easy_access_page

    def is_session_active(self) -> bool:
        """
        Orquesta la comprobación para ver si hay una sesión de usuario activa.
        Delega la comprobación física en el Page Object correspondiente.
        """
        log.debug("Comprobando sesión activa...")

        try:
            # PASO CLAVE: Antes de buscar nada, esperamos a que la página
            # termine de cargar y desaparezca cualquier overlay.
            self._easy_access_page.wait_for_page_to_be_ready()
            # Ahora la comprobación es mucho más fiable
            result = self._easy_access_page.is_logged_in()
            log.debug(f"Resultado de is_logged_in(): {result}")
            return result
        except Exception as e:
            # Esta excepción ahora capturaría un timeout de wait_for_page_to_be_ready
            # o del propio is_logged_in, dándonos más información.
            log.error(f"Error comprobando sesión (posiblemente la página no cargó a tiempo): {e}", exc_info=True)
            return False