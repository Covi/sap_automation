# tests/test_mb52.py
# Pruebas para el informe MB52 utilizando el servicio y las páginas configuradas

import pytest
from pathlib import Path
from config import SAP_USERNAME, SAP_PASSWORD, Mb52Config
from utils.logger import log

from core.builders.mb52  import build_mb52_service # <-- Importamos nuestro builder

from core.browser_manager import BrowserManager
from core.providers.toml_provider import TomlLocatorProvider
from core.providers.composite_provider import CompositeLocatorProvider

from data_models.mb52_models import Mb52FormData

from pages.mb52_page import MB52Page
from pages.sap_easy_access_page import SAPEasyAccessPage
from pages.sap_login_page import SAPLoginPage

from services.login_service import LoginService
from services.mb52_service import MB52Service
from services.transaction_service import TransactionService

@pytest.fixture(scope="module")
def browser_manager():
    manager = BrowserManager(headless=True)
    yield manager
    manager.close_browser()

@pytest.fixture(scope="module")
def page(browser_manager):
    return browser_manager.start_browser()

@pytest.fixture(scope="module")
def mb52_service(page):
    """
    Fixture que construye el servicio MB52 delegando en el builder central.
    """
    return build_mb52_service(page)

# --- La Tarea ---
def test_generar_informe_mb52(mb52_service, page):
    """
    Tarea que genera y descarga un informe de stock con la transacción MB52.
    """

    log.info("Iniciando la tarea de generación de informe MB52...")

    # El test es el único que conoce la configuración
    datos_informe = Mb52FormData(centro=Mb52Config.DEFAULT_CENTRO)

    # [CAMBIO] Construir la ruta completa y el nombre del fichero
    downloads_dir = Path(Mb52Config.DOWNLOAD_DIR)
    downloads_dir.mkdir(parents=True, exist_ok=True)
    fichero_de_salida_nombre = Mb52Config.EXPORT_FILENAME or f"mb52_{datos_informe.centro}.xlsx"
    fichero_de_salida_path = downloads_dir / fichero_de_salida_nombre


    # El test inyecta la configuración en el servicio
    mb52_service.generar_informe(datos_informe)

    # Por esta, que es más precisa y coincide con el título real:
    assert page.title() == "Visualizar stocks en almacén por material"

    log.info(f"\nHoja de stock para el centro {datos_informe.centro} generada con éxito.")

    # [CAMBIO] Pasar la ruta completa y el nombre al servicio
    mb52_service.descargar_informe(str(fichero_de_salida_path), fichero_de_salida_nombre)

    log.info(f"\nHoja de stock para el centro {datos_informe.centro} descargado con éxito.")
    
    # [CAMBIO] Añadir una verificación de que el fichero existe
    assert fichero_de_salida_path.exists()