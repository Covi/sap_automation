# Fichero: pages/sap_login_page.py

from typing import Any
from playwright.sync_api import Page
from pages.sap_page_base import SAPPageBase

class SAPLoginPage(SAPPageBase):
    """
    Page Object para la página de inicio de sesión de SAP.
    Hereda la gestión del provider y elementos comunes de SAPPageBase.
    """
    def __init__(self, page: Page, locator_provider: Any):
        super().__init__(page, locator_provider)
        
        # Los locators usan self._provider, heredado del padre.
        self.username_input = page.locator(self._provider.get('input_user'))
        self.password_input = page.locator(self._provider.get('input_password'))
        self.login_button   = page.locator(self._provider.get('input_login'))

    def fill_username(self, username: str):
        self.username_input.fill(username)

    def fill_password(self, password: str):
        self.password_input.fill(password)

    def click_login_button(self):
        self.login_button.click()