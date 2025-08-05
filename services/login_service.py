# services/login_service.py
# Servicio para gestionar el proceso de inicio de sesión en SAP

from pages.sap_login_page import SAPLoginPage
from pages.sap_easy_access_page import SAPEasyAccessPage

class LoginService:
    """
    Servicio para gestionar el proceso de inicio de sesión.
    """
    def __init__(self, login_page: SAPLoginPage, easy_access_page: SAPEasyAccessPage):
        self._login_page = login_page
        self._easy_access_page = easy_access_page

    def login(self, user: str, pss: str):
        """
        Orquesta el proceso completo de inicio de sesión.
        """
        self._login_page.navigate()
        self._login_page.fill_username(user)
        self._login_page.fill_password(pss)
        self._login_page.click_login_button()

        # Esta espera ahora funcionará porque el locator ya apunta dentro del iframe
        self._easy_access_page.transaction_input.wait_for()