import pytest
from pathlib import Path
from config import Mb52Config, BROWSER
from core.browser_manager import BrowserManager
from core.builders.generic_builder import GenericTransactionBuilder
from infra.playwright_browser_factory import PlaywrightBrowserFactory
from utils.logger import log


@pytest.fixture(scope="function")
def mb52_builder_and_page():
    """
    Prepara el entorno de prueba:
    - Crea la factoría de navegador.
    - Inicializa BrowserManager.
    - Devuelve page y builder listos para usar.
    """
    factory = PlaywrightBrowserFactory(browser_type=BROWSER, headless=True)
    manager = BrowserManager(factory)
    page = manager.start_browser()
    builder = GenericTransactionBuilder("mb52")

    yield page, builder

    log.info("Cerrando el navegador al finalizar los tests del módulo.")
    manager.close_browser()


def test_run_service_with_defaults(mb52_builder_and_page):
    page, builder = mb52_builder_and_page
    log.info("Iniciando test de MB52 con valores por defecto...")

    params = {}
    downloads_dir = Path(Mb52Config.DOWNLOAD_DIR)
    downloads_dir.mkdir(parents=True, exist_ok=True)
    expected_file = downloads_dir / Mb52Config.EXPORT_FILENAME

    if expected_file.exists():
        expected_file.unlink()

    try:
        service = builder.build_service(page)
        builder.run_service(service, params)
        assert expected_file.exists(), f"El fichero esperado {expected_file} no fue creado."
        log.info(f"Test completado. Fichero por defecto creado en: {expected_file}")
    finally:
        if expected_file.exists():
            expected_file.unlink()


def test_run_service_with_overrides(mb52_builder_and_page):
    page, builder = mb52_builder_and_page
    log.info("Iniciando test de MB52 con parámetros personalizados...")

    custom_filename = "informe_personalizado.xlsx"
    params = {
        "centro": Mb52Config.DEFAULT_CENTRO,
        "output": custom_filename
    }

    downloads_dir = Path(Mb52Config.DOWNLOAD_DIR)
    downloads_dir.mkdir(parents=True, exist_ok=True)
    expected_file = downloads_dir / custom_filename

    if expected_file.exists():
        expected_file.unlink()

    try:
        service = builder.build_service(page)
        builder.run_service(service, params)
        assert expected_file.exists(), f"El fichero personalizado {expected_file} no fue creado."
        log.info(f"Test completado. Fichero personalizado creado en: {expected_file}")
    finally:
        if expected_file.exists():
            expected_file.unlink()


def test_run_service_with_temp_directory(mb52_builder_and_page, monkeypatch, tmp_path):
    page, builder = mb52_builder_and_page
    log.info("Iniciando test de MB52 con directorio de descarga temporal...")

    temp_dir = tmp_path
    log.info(f"Usando directorio temporal: {temp_dir}")

    # Monkeypatch de la ruta de descarga
    monkeypatch.setattr(Mb52Config, 'DOWNLOAD_DIR', str(temp_dir))

    params = {}
    expected_file = temp_dir / Mb52Config.EXPORT_FILENAME

    service = builder.build_service(page)
    builder.run_service(service, params)

    assert expected_file.exists(), f"El fichero {expected_file} no fue creado en el dir temporal."
    log.info(f"Test completado. Fichero creado en el directorio temporal: {expected_file}")
