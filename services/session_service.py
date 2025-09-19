# services/session_service.py

from pages.sap_easy_access_page import SAPEasyAccessPage

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
        return self._easy_access_page.is_logged_in()