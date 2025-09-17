# Fichero: tests/test_transactions.py

import pytest
from pathlib import Path
import logging
from dataclasses import replace

# ## XXX CAMBIO 1: Importamos todas las dependencias necesarias para el builder.
from config.settings import TRANSACTION_CONFIGS
from core.registry import TRANSACTION_REGISTRY
from core.providers.locator_provider_factory import LocatorProviderFactory
from core.browser_manager import BrowserManager
from core.builders.generic_transaction_builder import GenericTransactionBuilder

log = logging.getLogger(__name__)

@pytest.fixture(
    scope="function",
    params=["MB52", "IQ09", "ZSIN_ORDENES"]
)
def transaction_context(request):
    """
    Prepara un contexto completo para un test de transacción.
    Ahora crea el builder "puro" inyectando sus dependencias.
    """
    transaction_code = request.param
    log.info(f"--- Preparando Fixture para la transacción: {transaction_code} ---")

    manager = BrowserManager(headless=True)
    page = manager.start_browser()
    
    # ## XXX CAMBIO 2: Se crea el builder con la nueva firma, inyectando dependencias.
    builder = GenericTransactionBuilder(
        registry=TRANSACTION_REGISTRY,
        configs=TRANSACTION_CONFIGS,
        provider_factory=LocatorProviderFactory()
    )
    
    config = TRANSACTION_CONFIGS[transaction_code]

    # ## XXX CAMBIO 3: 'yield' ahora también pasa el transaction_code.
    # Los tests lo necesitarán para llamar a los métodos del builder.
    yield page, builder, config, transaction_code

    log.info(f"--- Cerrando Fixture para la transacción: {transaction_code} ---")
    manager.close_browser()


def test_run_service_with_defaults(transaction_context):
    """
    Prueba el flujo completo con valores por defecto para TODAS las transacciones.
    """
    # ## XXX CAMBIO 4: Desempaquetamos también el transaction_code.
    page, builder, config, transaction_code = transaction_context
    log.info(f"Iniciando test con valores por defecto para [{transaction_code}]...")

    params = {}
    
    downloads_dir = Path(config.download_dir)
    downloads_dir.mkdir(parents=True, exist_ok=True)
    expected_file = downloads_dir / config.export_filename

    if expected_file.exists():
        expected_file.unlink()

    try:
        # ## XXX CAMBIO 5: Se pasa el transaction_code a los métodos del builder.
        service = builder.build_service(transaction_code, page)
        builder.run_service(service, transaction_code, params)
        assert expected_file.exists(), f"El fichero esperado {expected_file} no fue creado."
        log.info(f"Test [{transaction_code}] completado. Fichero creado: {expected_file}")
    finally:
        if expected_file.exists():
            expected_file.unlink()

def test_run_service_with_overrides(transaction_context):
    """
    Prueba el flujo con parámetros personalizados para TODAS las transacciones.
    """
    page, builder, config, transaction_code = transaction_context
    log.info(f"Iniciando test con overrides para [{transaction_code}]...")

    custom_filename = f"informe_{transaction_code.lower()}_personalizado.xlsx"
    params = {
        "centro": config.default_centro,
        "output": custom_filename
    }

    downloads_dir = Path(config.download_dir)
    downloads_dir.mkdir(parents=True, exist_ok=True)
    expected_file = downloads_dir / custom_filename

    if expected_file.exists():
        expected_file.unlink()

    try:
        service = builder.build_service(transaction_code, page)
        builder.run_service(service, transaction_code, params)
        assert expected_file.exists(), f"El fichero personalizado {expected_file} no fue creado."
        log.info(f"Test [{transaction_code}] completado. Fichero creado: {expected_file}")
    finally:
        if expected_file.exists():
            expected_file.unlink()

def test_run_service_with_temp_directory(transaction_context, monkeypatch, tmp_path):
    """
    Prueba con un directorio de descarga temporal para TODAS las transacciones.
    """
    page, builder, config, transaction_code = transaction_context
    log.info(f"Iniciando test con directorio temporal para [{transaction_code}]...")
    
    temp_dir = tmp_path
    expected_file = temp_dir / config.export_filename

    modified_config = replace(config, download_dir=str(temp_dir))
    monkeypatch.setitem(TRANSACTION_CONFIGS, transaction_code, modified_config)
    
    # El builder usará la config parcheada porque se le inyectó el diccionario TRANSACTION_CONFIGS
    service = builder.build_service(transaction_code, page)
    builder.run_service(service, transaction_code, {}) # params vacíos

    assert expected_file.exists(), f"El fichero {expected_file} no fue creado en el dir temporal."
    log.info(f"Test [{transaction_code}] completado. Fichero creado en: {expected_file}")