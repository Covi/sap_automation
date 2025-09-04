# tests/test_iq09.py
# Tests funcionales para IQ09 utilizando el GenericTransactionBuilder.

import pytest
from pathlib import Path

# --- Imports necesarios ---
from config import Iq09Config # <-- Cambio a Iq09Config
from core.browser_manager import BrowserManager
from core.builders.generic_transaction_builder import GenericTransactionBuilder
from utils.logger import log

# La fixture ahora prepara el builder para "iq09"
@pytest.fixture(scope="function")
def iq09_builder_and_page(): # <-- Renombramos la fixture
    """
    Prepara el entorno de prueba: inicia el navegador y crea una instancia
    del GenericTransactionBuilder configurada para 'iq09'.
    """
    manager = BrowserManager(headless=True)
    page = manager.start_browser()
    
    # Crea la instancia del builder para la transacción 'iq09'
    builder = GenericTransactionBuilder("iq09") # <-- Cambio a "iq09"

    yield page, builder

    log.info("Cerrando el navegador al finalizar los tests del módulo.")
    manager.close_browser()


# TEST CON VALORES POR DEFECTO
def test_run_service_with_defaults(iq09_builder_and_page): # <-- Usamos la nueva fixture
    """
    Prueba el flujo completo con valores por defecto.
    Verifica que al ejecutar run_service sin parámetros, se crea el fichero esperado.
    """
    page, builder = iq09_builder_and_page
    log.info("Iniciando test de IQ09 con valores por defecto...")

    params = {}

    # Define el fichero de salida esperado usando Iq09Config
    downloads_dir = Path(Iq09Config.DOWNLOAD_DIR) # <-- Cambio a Iq09Config
    downloads_dir.mkdir(parents=True, exist_ok=True)
    expected_file = downloads_dir / Iq09Config.EXPORT_FILENAME # <-- Cambio a Iq09Config

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


# TEST SOBREESCRIBIENDO PARÁMETROS
def test_run_service_with_overrides(iq09_builder_and_page): # <-- Usamos la nueva fixture
    """
    Prueba el flujo completo pasando parámetros personalizados.
    Verifica que al ejecutar run_service con un 'output' específico, se crea ese fichero.
    """
    page, builder = iq09_builder_and_page
    log.info("Iniciando test de IQ09 con parámetros personalizados...")

    custom_filename = "informe_iq09_personalizado.xlsx"
    params = {
        "centro": Iq09Config.DEFAULT_CENTRO, # <-- Usamos la config de IQ09
        "output": custom_filename
    }

    downloads_dir = Path(Iq09Config.DOWNLOAD_DIR) # <-- Cambio a Iq09Config
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


# TEST USANDO MONKEYPATCH
def test_run_service_with_temp_directory(iq09_builder_and_page, monkeypatch, tmp_path): # <-- Usamos la nueva fixture
    """
    Prueba que el fichero se descarga en un directorio temporal y personalizado.
    """
    page, builder = iq09_builder_and_page
    log.info("Iniciando test de IQ09 con directorio de descarga temporal...")
    
    temp_dir = tmp_path
    log.info(f"Usando directorio temporal: {temp_dir}")

    # Parcheamos el atributo 'DOWNLOAD_DIR' de la clase 'Iq09Config'
    monkeypatch.setattr(Iq09Config, 'DOWNLOAD_DIR', str(temp_dir)) # <-- Cambio a Iq09Config
    
    params = {}
    expected_file = temp_dir / Iq09Config.EXPORT_FILENAME # <-- Cambio a Iq09Config
    
    service = builder.build_service(page)
    builder.run_service(service, params)

    assert expected_file.exists(), f"El fichero {expected_file} no fue creado en el dir temporal."
    log.info(f"Test completado. Fichero creado en el directorio temporal: {expected_file}")