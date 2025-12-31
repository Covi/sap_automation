# core/builders/generic_transaction_builder.py

import logging
from typing import Dict, Any, Optional
from pathlib import Path
from pydantic import ValidationError, BaseModel
from playwright.sync_api import Page

from core.builders.builder_protocol import BuilderProtocol
from core.providers.locator_provider_factory import LocatorProviderFactory
from pages.sap_easy_access_page import SAPEasyAccessPage
from services.transaction_service import TransactionService
from core.registry import TRANSACTION_REGISTRY
from core.builders.sap_payload_builder import SapPayloadBuilder
# NUEVOS IMPORTS PARA LA ABSTRACCIÓN
from core.builders.sap_command_builder import SapCommandBuilder
from core.builders.sap_url_builder import SapUrlBuilder

# Configuración global
from config import settings 

log = logging.getLogger(__name__)

class GenericTransactionBuilder(BuilderProtocol):
    """
    Builder genérico que orquesta la construcción y ejecución de servicios.
    Ahora decide entre el flujo clásico (formulario) o el rápido (URL Dynpro).
    """
    def __init__(self, transaction_name: str):
        if transaction_name not in TRANSACTION_REGISTRY:
            raise ValueError(f"Transacción '{transaction_name}' no reconocida.")
        
        self.recipe = TRANSACTION_REGISTRY[transaction_name]
        # FIXME esto tiene que cambiar porque queremos eliminar el LocatorProviderFactory y usar POM en cada página
        self.provider_factory = LocatorProviderFactory()
        log.info(f"Builder inicializado para: {self.recipe.config.transaction_code}")

    def build_service(self, page: Page) -> Any:
        """Construye el servicio inyectando dependencias."""
        easy_access_provider = self.provider_factory.create("easy_access.toml")
        trx_provider = self.provider_factory.create(self.recipe.config.locator_file)

        easy_access_page = SAPEasyAccessPage(page, locator_provider=easy_access_provider)
        trx_page = self.recipe.page_class(page, locator_provider=trx_provider)

        # El TransactionService ahora recibirá comandos limpios
        transaction_service = TransactionService(easy_access_page)
        
        return self.recipe.service_class(
            transaction_service,
            trx_page,
            config=self.recipe.config, 
            **(self.recipe.extra_dependencies or {})
        )

    def run_service(self, service: Any, params: Dict[str, Any]) -> None:
        """
        Orquesta la ejecución decidiendo el camino (Fast Path vs Classic).
        """
        config = self.recipe.config
        criteria_schema = self.recipe.criteria_schema
        options_schema = self.recipe.options_schema

        # 1. Preparación de Criterios
        try:
            # FIXME no me gusta hardcodear el centro por defecto si no viene en params
            default_data = {"centro": settings.general.default_centro}
            final_criteria_data = {k: v for k, v in default_data.items() if v is not None} | params
            criteria = criteria_schema(**final_criteria_data)
        except ValidationError as e:
            log.error(f"Error en validación de criterios: {e}")
            raise


        # 2. EJECUCIÓN FÍSICA: ¿URL Directa o Comando /n?
        # FIXME Todo esto lo veo muy hardcodeado, no sé si deberían venir "las cosas" inyectadas o por parámetro
        use_fast_path = getattr(config, 'use_fast_url', False)

        # FIXME No me gusta que cada opción haga una cosa
        if use_fast_path:
            log.info(f"Navegación directa por URL para {config.transaction_code}")
            # FÍSICAMENTE: El builder construye la URL y ordena el salto
            command = SapUrlBuilder.build_transaction_url(config.transaction_code, criteria)

            # FIXME No me gusta esto así.
            # XXX Accedemos a la instancia de page de Playwright a través del objeto page del servicio
            service._page.page.goto(command)
        else:
            log.info(f"Navegación clásica por comando para {config.transaction_code}")
            # FÍSICAMENTE: Se usa el cuadro de comandos de SAP (/nTRX)
            command = SapCommandBuilder.build_standard(config.transaction_code)

            # FIXME No me gusta esto así.
            # XXX Se usa por formulario
            service._transaction_service.run_transaction(command)

        # 3. Preparación de Opciones (Download paths, etc.)
        options = None
        if options_schema:
            options = self._build_options(options_schema, config, params)

        # 4. Lanzamiento del Service
        # El Service internamente sabrá si tiene que rellenar o no mirando su config
        if options:
            service.run(criteria=criteria, options=options)
        else:
            # Fallback para servicios sin schema de opciones (MB52 simple)
            service.run(form_data=criteria)

    def _build_options(self, schema: Any, config: Any, params: Dict[str, Any]) -> BaseModel:
        """Encapsula la lógica de creación de opciones de ejecución."""
        dl_dir = config.download_dir or settings.general.download_dir or (Path.cwd() / "downloads")
        if isinstance(dl_dir, str): dl_dir = Path(dl_dir)
        dl_dir.mkdir(parents=True, exist_ok=True)

        options_data = params.copy()
        options_data['output_path'] = dl_dir
        options_data['output_filename'] = params.get("output") or config.export_filename
        
        return schema(**options_data)