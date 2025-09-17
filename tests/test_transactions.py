# Fichero: tests/test_transactions.py

import pytest
from pathlib import Path
import logging
from dataclasses import replace

# --- Imports del nuevo sistema de configuración ---
from config.settings import TRANSACTION_CONFIGS
from core.browser_manager import BrowserManager
from core.builders.generic_transaction_builder import GenericTransactionBuilder

log = logging.getLogger(__name__)

# ===================================================================
# 1. FIXTURE PARAMETRIZADA
#    Esta única fixture reemplaza a mb52_builder_and_page y iq09_builder_and_page.
#    pytest la ejecutará una vez por cada valor en "params".
# ===================================================================

@pytest.fixture(
    scope="function",
    params=["MB52", "IQ09", "ZSIN_ORDENES"] # Aquí defines para qué transacciones correrán los tests
)
def transaction_context(request):
    """
    Prepara un contexto completo para un test de transacción:
    - Inicia el navegador.
    - Obtiene el código de la transacción del parámetro del test (request.param).
    - Crea el builder para esa transacción.
    - Proporciona el objeto de configuración correspondiente.
    """
    transaction_code = request.param
    log.info(f"--- Preparando Fixture para la transacción: {transaction_code} ---")

    manager = BrowserManager(headless=True)
    page = manager.start_browser()
    
    builder = GenericTransactionBuilder(transaction_code)
    # Obtenemos la instancia de configuración correcta del diccionario que importamos
    config = TRANSACTION_CONFIGS[transaction_code]

    # 'yield' pasa estos tres objetos al test que use la fixture
    yield page, builder, config

    log.info(f"--- Cerrando Fixture para la transacción: {transaction_code} ---")
    manager.close_browser()

# ===================================================================
# 2. TESTS PARAMETRIZADOS
#    Cada test ahora recibe el contexto de la fixture y se ejecuta
#    para cada una de las transacciones definidas en `params`.
# ===================================================================

def test_run_service_with_defaults(transaction_context):
    """
    Prueba el flujo completo con valores por defecto para TODAS las transacciones.
    """
    page, builder, config = transaction_context
    log.info(f"Iniciando test con valores por defecto para [{config.transaction_code}]...")

    params = {}
    
    # Usamos el objeto 'config' que nos da la fixture para obtener las rutas
    downloads_dir = Path(config.download_dir)
    downloads_dir.mkdir(parents=True, exist_ok=True)
    expected_file = downloads_dir / config.export_filename

    if expected_file.exists():
        expected_file.unlink()

    try:
        service = builder.build_service(page)
        builder.run_service(service, params)
        assert expected_file.exists(), f"El fichero esperado {expected_file} no fue creado."
        log.info(f"Test [{config.transaction_code}] completado. Fichero creado: {expected_file}")
    finally:
        if expected_file.exists():
            expected_file.unlink()

def test_run_service_with_overrides(transaction_context):
    """
    Prueba el flujo con parámetros personalizados para TODAS las transacciones.
    """
    page, builder, config = transaction_context
    log.info(f"Iniciando test con overrides para [{config.transaction_code}]...")

    custom_filename = f"informe_{config.transaction_code.lower()}_personalizado.xlsx"
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
        service = builder.build_service(page)
        builder.run_service(service, params)
        assert expected_file.exists(), f"El fichero personalizado {expected_file} no fue creado."
        log.info(f"Test [{config.transaction_code}] completado. Fichero creado: {expected_file}")
    finally:
        if expected_file.exists():
            expected_file.unlink()

def test_run_service_with_temp_directory(transaction_context, monkeypatch, tmp_path):
    """
    Prueba con un directorio de descarga temporal para TODAS las transacciones.
    """
    page, builder, config = transaction_context
    log.info(f"Iniciando test con directorio temporal para [{config.transaction_code}]...")
    
    # La fixture tmp_path de pytest crea un directorio temporal único
    temp_dir = tmp_path
    expected_file = temp_dir / config.export_filename

    # --- NUEVA FORMA DE HACER MONKEYPATCH ---
    # Como la config es una dataclass inmutable (frozen=True), no podemos usar setattr.
    # En su lugar, creamos una COPIA de la config modificando solo el campo que queremos.
    modified_config = replace(config, download_dir=str(temp_dir))

    # Ahora, le decimos a monkeypatch que cuando el builder pida la configuración de,
    # por ejemplo, 'MB52', en lugar de devolver la original, devuelva nuestra copia modificada.
    monkeypatch.setitem(TRANSACTION_CONFIGS, config.transaction_code, modified_config)
    
    # El builder, al ejecutarse, usará la configuración que hemos "inyectado" temporalmente.
    service = builder.build_service(page)
    builder.run_service(service, {}) # params vacíos

    assert expected_file.exists(), f"El fichero {expected_file} no fue creado en el dir temporal."
    log.info(f"Test [{config.transaction_code}] completado. Fichero creado en: {expected_file}")