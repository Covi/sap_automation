# pages/sap_login_page.py
# Page Object para la página de inicio de sesión de SAP

from playwright.sync_api import Page
from core.page_base import PageBase
from core.providers.base_provider import BaseLocatorProvider

class SAPLoginPage(PageBase):
    """
    Page Object para la página de inicio de sesión de SAP.
    """
    # La dependencia es obligatoria
    def __init__(self, page: Page, locator_provider: BaseLocatorProvider):
        super().__init__(page)
        
        # Versión explícita, clara y segura
        self.username_input = page.locator(locator_provider.get('input_user'))
        self.password_input = page.locator(locator_provider.get('input_password'))
        self.login_button   = page.locator(locator_provider.get('input_login'))

    def fill_username(self, username: str):
        self.username_input.fill(username)

    def fill_password(self, password: str):
        self.password_input.fill(password)

    def click_login_button(self):
        self.login_button.click()