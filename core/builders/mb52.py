# core/builders/mb52.py
# Construye y configura todo lo necesario para devolver un MB52Service listo para usar.

from playwright.sync_api import Page

from config import SAP_USERNAME, SAP_PASSWORD
from core.providers.composite_provider import CompositeLocatorProvider
from core.providers.toml_provider import TomlLocatorProvider
from pages.mb52_page import MB52Page
from pages.sap_easy_access_page import SAPEasyAccessPage
from pages.sap_login_page import SAPLoginPage
from services.login_service import LoginService
from services.mb52_service import MB52Service
from services.transaction_service import TransactionService

def build_mb52_service(page: Page) -> MB52Service:
    """
    Construye y configura todo lo necesario para devolver un MB52Service listo para usar.
    """
    # --- 1. Crear los proveedores simples que leen ficheros ---
    common_provider = TomlLocatorProvider("locators/common.toml")
    login_provider = TomlLocatorProvider("locators/login.toml")
    easy_access_provider = TomlLocatorProvider("locators/easy_access.toml")
    mb52_provider = TomlLocatorProvider("locators/mb52.toml")

    # --- 2. Crear los proveedores COMPUESTOS ---
    composite_easy_access = CompositeLocatorProvider([easy_access_provider, common_provider])
    composite_mb52 = CompositeLocatorProvider([mb52_provider, common_provider])

    # --- 3. Crear las Page Objects ---
    login_page = SAPLoginPage(page, locator_provider=login_provider)
    easy_access_page = SAPEasyAccessPage(page, locator_provider=composite_easy_access)
    mb52_page = MB52Page(page, locator_provider=composite_mb52)

    # --- 4. Crear los servicios ---
    login_service = LoginService(login_page, easy_access_page)
    transaction_service = TransactionService(easy_access_page)
    service = MB52Service(transaction_service, mb52_page)

    # --- 5. Ejecutar el setup (login) ---
    login_service.login(SAP_USERNAME, SAP_PASSWORD)
    
    return service