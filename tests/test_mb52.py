# tests/test_mb52.py
# Tests funcionales para MB52 utilizando el GenericTransactionBuilder.

import pytest
from pathlib import Path

# --- Imports necesarios ---
from config import Mb52Config
from core.browser_manager import BrowserManager
# 1. Importa la CLASE del builder, no una instancia
from core.builders.generic_builder import GenericTransactionBuilder
from utils.logger import log

# La fixture ahora prepara el builder para "mb52"
@pytest.fixture(scope="function")

# TEST FIXTURE
def mb52_builder_and_page():
    """
    Prepara el entorno de prueba: inicia el navegador y crea una instancia
    del GenericTransactionBuilder configurada para 'mb52'.
    """
    manager = BrowserManager(headless=True)
    page = manager.start_browser()
    
    # Crea la instancia del builder que quieres probar
    builder = GenericTransactionBuilder("mb52")

    yield page, builder

    log.info("Cerrando el navegador al finalizar los tests del módulo.")
    manager.close_browser()


# TEST CON VALORES POR DEFECTO
def test_run_service_with_defaults(mb52_builder_and_page):
    """
    Prueba el flujo completo con valores por defecto.
    Verifica que al ejecutar run_service sin parámetros, se crea el fichero esperado.
    """
    page, builder = mb52_builder_and_page
    log.info("Iniciando test de MB52 con valores por defecto...")

    # 3. Define los inputs (en este caso, ninguno para probar los defaults)
    params = {}

    # Define el fichero de salida esperado
    downloads_dir = Path(Mb52Config.DOWNLOAD_DIR)
    downloads_dir.mkdir(parents=True, exist_ok=True)
    expected_file = downloads_dir / Mb52Config.EXPORT_FILENAME

    # Limpia el fichero si existía de una ejecución anterior
    if expected_file.exists():
        expected_file.unlink()

    # 4. Ejecuta el builder, que orquesta todo el proceso
    try:
        service = builder.build_service(page)
        builder.run_service(service, params)

        # 5. Comprueba el resultado final
        assert expected_file.exists(), f"El fichero esperado {expected_file} no fue creado."
        log.info(f"Test completado. Fichero por defecto creado en: {expected_file}")

    finally:
        # Limpia el fichero creado para no afectar otros tests
        if expected_file.exists():
            expected_file.unlink()

# TEST SOBREESCRIBIENDO PARÁMETROS
def test_run_service_with_overrides(mb52_builder_and_page):
    """
    Prueba el flujo completo pasando parámetros personalizados.
    Verifica que al ejecutar run_service con un 'output' específico, se crea ese fichero.
    """
    page, builder = mb52_builder_and_page
    log.info("Iniciando test de MB52 con parámetros personalizados...")

    # Define los inputs personalizados
    custom_filename = "informe_personalizado.xlsx"
    params = {
        # CAMBIO: Usa un centro que sepas que tiene datos para asegurar un resultado exitoso
        "centro": Mb52Config.DEFAULT_CENTRO, # o E086 
        # Mantenemos el 'output' personalizado para probar que el override funciona
        "output": custom_filename
    }

    # Define el fichero de salida esperado
    downloads_dir = Path(Mb52Config.DOWNLOAD_DIR)
    downloads_dir.mkdir(parents=True, exist_ok=True)
    expected_file = downloads_dir / custom_filename

    if expected_file.exists():
        expected_file.unlink()

    # Ejecuta el builder con los parámetros personalizados
    try:
        service = builder.build_service(page)
        builder.run_service(service, params)

        # Comprueba que el fichero con el nombre personalizado existe
        assert expected_file.exists(), f"El fichero personalizado {expected_file} no fue creado."
        log.info(f"Test completado. Fichero personalizado creado en: {expected_file}")

    finally:
        if expected_file.exists():
            expected_file.unlink()


# --- TEST USANDO MONKEYPATCH ---
def test_run_service_with_temp_directory(mb52_builder_and_page, monkeypatch, tmp_path):
    """
    Prueba que el fichero se descarga en un directorio temporal y personalizado.
    """
    page, builder = mb52_builder_and_page
    log.info("Iniciando test de MB52 con directorio de descarga temporal...")
    
    # tmp_path es otra fixture de pytest que crea un directorio temporal único para el test
    temp_dir = tmp_path
    log.info(f"Usando directorio temporal: {temp_dir}")

    # Esta es la "nota adhesiva":
    # Le decimos a monkeypatch que "parchee" el atributo 'DOWNLOAD_DIR' de la clase 'Mb52Config'
    # con el valor de nuestro directorio temporal.
    monkeypatch.setattr(Mb52Config, 'DOWNLOAD_DIR', str(temp_dir))
    
    params = {} # Usamos parámetros por defecto
    expected_file = temp_dir / Mb52Config.EXPORT_FILENAME

    # No hace falta limpiar el fichero antes porque tmp_path siempre está vacío
    
    # El builder, al ejecutarse, leerá la ruta parcheada por monkeypatch
    service = builder.build_service(page)
    builder.run_service(service, params)

    # La aserción comprueba que el fichero se creó en el directorio temporal
    assert expected_file.exists(), f"El fichero {expected_file} no fue creado en el dir temporal."
    log.info(f"Test completado. Fichero creado en el directorio temporal: {expected_file}")