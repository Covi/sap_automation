# core/builders/generic_transaction_builder.py

import logging
from typing import Dict, Any
from pathlib import Path
from pydantic import ValidationError
from playwright.sync_api import Page

from core.builders.builder_protocol import BuilderProtocol
from core.providers.locator_provider_factory import LocatorProviderFactory
from pages.sap_easy_access_page import SAPEasyAccessPage
from services.transaction_service import TransactionService
from core.registry import TRANSACTION_REGISTRY

# Necesario para acceder a valores globales si no están en la config de la transacción
from config import settings 

log = logging.getLogger(__name__)

class GenericTransactionBuilder(BuilderProtocol):
    """
    Builder genérico capaz de construir y ejecutar cualquier servicio de transacción
    registrado en el TRANSACTION_REGISTRY.
    """
    def __init__(self, transaction_name: str):
        if transaction_name not in TRANSACTION_REGISTRY:
            raise ValueError(f"Transacción '{transaction_name}' no reconocida o no registrada.")
        
        self.recipe = TRANSACTION_REGISTRY[transaction_name]
        self.provider_factory = LocatorProviderFactory()
        
        # CAMBIO: Usamos .config (instancia) y .transaction_code (minúscula)
        log.info(f"Builder inicializado para la transacción: {self.recipe.config.transaction_code}")

    def build_service(self, page: Page) -> Any:
        """
        Construye el servicio inyectando configuración y dependencias.
        """
        easy_access_provider = self.provider_factory.create("easy_access.toml")
        
        # CAMBIO: Acceso correcto a la propiedad del objeto Pydantic
        trx_locator_filename = self.recipe.config.locator_file
        trx_provider = self.provider_factory.create(trx_locator_filename)

        easy_access_page = SAPEasyAccessPage(page, locator_provider=easy_access_provider)
        trx_page = self.recipe.page_class(page, locator_provider=trx_provider)

        transaction_service = TransactionService(easy_access_page)
        
        # CAMBIO: Inyección explícita de 'config' al constructor del servicio.
        # El servicio debe esperar este argumento.
        trx_service = self.recipe.service_class(
            transaction_service,
            trx_page,
            config=self.recipe.config, 
            **(self.recipe.extra_dependencies or {})
        )

        return trx_service

    def run_service(self, service: Any, params: Dict[str, Any]) -> None:
        """
        Ejecuta el servicio con los parámetros proporcionados por la CLI.
        """
        # Obtenemos la instancia de configuración específica (ej: Mb52Config)
        config_instance = self.recipe.config
        criteria_schema = self.recipe.criteria_schema
        options_schema = self.recipe.options_schema

        try:
            # Construcción de criterios. 
            # NOTA: 'default_centro' está en settings.general, no en la config de transacción específica
            # Si lo necesitas aquí, debes traerlo de settings.general
            default_data = {"centro": settings.general.default_centro}
            
            final_criteria_data = {k: v for k, v in default_data.items() if v is not None} | params
            criteria = criteria_schema(**final_criteria_data)

        except ValidationError as e:
            log.error(f"Error de validación en los parámetros de criterios: {e}")
            raise ValueError("Parámetros de entrada para criterios inválidos.") from e

        log.info(f"Iniciando {config_instance.transaction_code} con los criterios: {criteria.model_dump(exclude_none=True)}")

        # --- LÓGICA CONDICIONAL ---
        if options_schema:
            try:
                options_data = params.copy()
                
                # CAMBIO: Acceso a atributos en minúscula y uso de fallback a settings globales si es None
                # Prioridad: CLI > Config Transacción > Config General (si existiera)
                
                # Definimos el directorio de descarga
                dl_dir = config_instance.download_dir or settings.general.download_dir
                if dl_dir is None:
                     # Fallback final si no está configurado en ningún sitio
                     dl_dir = Path.cwd() / "downloads"
                
                options_data['output_path'] = dl_dir
                options_data['output_filename'] = params.get("output") or config_instance.export_filename

                options = options_schema(**options_data)
                
            except ValidationError as e:
                log.error(f"Error de validación en los parámetros de opciones: {e}")
                raise ValueError("Parámetros de entrada para opciones inválidos.") from e
            
            service.run(criteria=criteria, options=options)

        else:
            # Lógica para servicios simples (como MB52)
            
            dl_dir = config_instance.download_dir or settings.general.download_dir
            if dl_dir is None:
                 dl_dir = Path.cwd() / "downloads" # Fallback seguro
            
            # Aseguramos que sea Path
            if isinstance(dl_dir, str):
                dl_dir = Path(dl_dir)

            dl_dir.mkdir(parents=True, exist_ok=True)
            
            filename = params.get("output") or config_instance.export_filename
            path_fichero = dl_dir / filename
            
            # Llamada al servicio
            service.run(form_data=criteria, path=path_fichero, filename=filename)
        
        log.info(f"Proceso de {config_instance.transaction_code} completado.")