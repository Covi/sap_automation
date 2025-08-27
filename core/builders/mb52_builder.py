# Fichero: core/builders/mb52_builder.py
# Construye y configura todo lo necesario para devolver un MB52Service listo para usar.

from pathlib import Path
from typing import Dict, Any

from pydantic import ValidationError

from core.builders.builder_protocol import BuilderProtocol

from core.providers.toml_provider import TomlLocatorProvider
from core.providers.composite_provider import CompositeLocatorProvider

from pages.sap_login_page import SAPLoginPage
from pages.sap_easy_access_page import SAPEasyAccessPage
from pages.mb52_page import MB52Page

from services.login_service import LoginService
from services.transaction_service import TransactionService
from services.mb52_service import MB52Service

from config import SAP_USERNAME, SAP_PASSWORD, Mb52Config
from data_models.mb52_models import Mb52FormData
from utils.logger import log


class MB52Builder(BuilderProtocol):
    def build_service(self, page) -> MB52Service:
        # --- Este método no necesita cambios ---
        common_provider = TomlLocatorProvider("locators/common.toml")
        login_provider = TomlLocatorProvider("locators/login.toml")
        easy_access_provider = TomlLocatorProvider("locators/easy_access.toml")
        mb52_provider = TomlLocatorProvider("locators/mb52.toml")

        composite_easy_access = CompositeLocatorProvider([easy_access_provider, common_provider])
        composite_mb52 = CompositeLocatorProvider([mb52_provider, common_provider])

        login_page = SAPLoginPage(page, locator_provider=login_provider)
        easy_access_page = SAPEasyAccessPage(page, locator_provider=composite_easy_access)
        mb52_page = MB52Page(page, locator_provider=composite_mb52)

        login_service = LoginService(login_page, easy_access_page)
        transaction_service = TransactionService(easy_access_page)
        mb52_service = MB52Service(transaction_service, mb52_page)

        login_service.login(SAP_USERNAME, SAP_PASSWORD)

        return mb52_service

    def run_service(self, service: MB52Service, params: Dict[str, Any]) -> None:
        ### --- LÓGICA DE DATOS MEJORADA (SOLID) --- ###

        try:
            # 1. Prepara un diccionario con los valores por defecto de la config.
            default_data = {
                "centro": Mb52Config.DEFAULT_CENTRO
            }

            # 2. Une los defaults con los params del usuario. El valor en 'params' tiene prioridad.
            final_data = default_data | params

            # 3. Crea el modelo Pydantic. Si 'centro' no vino en 'params',
            #    ahora tendrá el valor por defecto de la configuración.
            datos = Mb52FormData(**final_data)

        except ValidationError as e:
            log.error(f"Error de validación en los parámetros para MB52: {e}")
            raise ValueError("Parámetros inválidos.") from e

        ### --- LÓGICA DE EJECUCIÓN (SIN CAMBIOS) --- ###

        downloads_dir = Path(Mb52Config.DOWNLOAD_DIR)
        downloads_dir.mkdir(parents=True, exist_ok=True)

        # Usamos 'datos.centro' que es el valor ya validado y con el default aplicado
        filename = params.get("output") or Mb52Config.EXPORT_FILENAME or f"mb52_{datos.centro}.xlsx"
        path_fichero = downloads_dir / filename

        log.info(f"Iniciando generación de informe MB52 para centro {datos.centro}")

        service.generar_informe(datos)
        service.descargar_informe(str(path_fichero), filename)

        log.info(f"Informe MB52 generado y descargado en: {path_fichero}")


# Exportamos una instancia para usar desde main.py
builder = MB52Builder()