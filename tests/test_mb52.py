# tests/test_mb52.py
# Test funcional para MB52 utilizando el builder unificado y respetando la arquitectura actual

import pytest
from pathlib import Path
from config import Mb52Config
from core.browser_manager import BrowserManager
from core.builders.mb52_builder import builder
from data_models.mb52_models import Mb52FormData
from utils.logger import log

@pytest.fixture(scope="module")
def entorno_mb52():
    manager = BrowserManager(headless=True)
    page = manager.start_browser()

    service = builder.build_service(page)  # Le pasas el page correctamente

    yield page, service

    manager.close_browser()

def test_generar_informe_mb52(entorno_mb52):
    page, mb52_service = entorno_mb52
    log.info("Iniciando la tarea de generación de informe MB52...")

    datos_informe = Mb52FormData(centro=Mb52Config.DEFAULT_CENTRO)

    downloads_dir = Path(Mb52Config.DOWNLOAD_DIR)
    downloads_dir.mkdir(parents=True, exist_ok=True)

    nombre_fichero = Mb52Config.EXPORT_FILENAME or f"mb52_{datos_informe.centro}.xlsx"
    path_fichero = downloads_dir / nombre_fichero

    mb52_service.generar_informe(datos_informe)
    assert page.title() == "Visualizar stocks en almacén por material"

    mb52_service.descargar_informe(str(path_fichero), nombre_fichero)
    assert path_fichero.exists()

    log.info(f"Informe MB52 descargado correctamente en {path_fichero}")