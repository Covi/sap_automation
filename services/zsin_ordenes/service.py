# services/zsin_ordenes/service.py

# 1. LIBRERÍA ESTÁNDAR
import logging
from typing import Callable, Dict, Optional

# 2. LIBRERÍAS DE TERCEROS
# (Sin cambios)

# 3. MÓDULOS LOCALES (Tu Proyecto)
# CAMBIO: Importamos la CLASE de configuración específica para el Type Hinting desde el SSOT
from config.settings import ZsinOrdenesConfig
from core.builders.sap_payload_builder import SapPayloadBuilder
from core.protocols import FileHandlerProtocol, PrintServiceProtocol
from pages.zsin_ordenes_page import ZsinOrdenesPage
from schemas.zsin_ordenes import ZsinOrdenesCriteria, ZsinOrdenesExecutionOptions
from services.transaction_service import TransactionService

# 4. IMPORTACIONES RELATIVAS
from .envio_action import EnvioOrdenesService
from .impresion_action import ImpresionOrdenesService


log = logging.getLogger(__name__)

class ZsinOrdenesService:
    """
    Servicio para la transacción ZSIN_ORDENES.
    Orquesta la ejecución, impresión y envío de órdenes basándose en una configuración inyectada.
    """
    def __init__(
        self,
        transaction_service: TransactionService,
        page: ZsinOrdenesPage,
        config: ZsinOrdenesConfig,  # <--- CAMBIO: Inyección obligatoria de la configuración
        file_handler: Optional[FileHandlerProtocol] = None,
        print_service: Optional[PrintServiceProtocol] = None,
    ):
        self._transaction_service = transaction_service
        self._page = page
        self._config = config  # <--- CAMBIO: Usamos la instancia inyectada, no creamos una nueva
        self._file_handler = file_handler
        self._print_service = print_service

        # Inyección de subservicios especializados
        # NOTA: En un futuro refactor estricto, estos también podrían ser inyectados (Factories),
        # pero por ahora mantenemos la creación interna controlada.
        self._impresion = None
        self._envio = None

        if file_handler and print_service:
            self._impresion = ImpresionOrdenesService(page, file_handler, print_service, log)
        
        self._envio = EnvioOrdenesService(page, log)

    def _ejecutar_seguro(self, funcion: Callable, nombre_accion: str) -> Dict[str, str]:
        """
        Ejecuta una acción y captura posibles errores, devolviendo un dict con estado.
        """
        try:
            funcion()
            log.info(f"{nombre_accion} completada con éxito.")
            return {"status": "ok"}
        except Exception as e:
            log.error(f"Error en {nombre_accion}: {e}", exc_info=True)
            return {"status": "error", "error": str(e)} 

    def run(self, criteria: ZsinOrdenesCriteria, options: ZsinOrdenesExecutionOptions):
        """
        Orquesta el flujo completo de la transacción ZSIN_ORDENES.

        :param criteria: Criterios de búsqueda para el formulario.
        :param options: Opciones de ejecución (acciones, configuración de salida).
        """
        try:
            resultados: Dict[str, Dict[str, str]] = {}

            # CAMBIO: Acceso al atributo en minúscula (propiedad del modelo Pydantic)
            self._transaction_service.run_transaction(self._config.transaction_code)

            # Modelo
            payload = SapPayloadBuilder.build_payload(criteria)
            
            # Recuperar la espera del formulario antes de rellenarlo
            self._page.esperar_formulario()
            self._page.rellenar_formulario(payload)
            
            # self._page.pause() # Debug UI
            
            self._page.ejecutar()
            self._page.esperar_resultados(60000)

            # --- Resultados ---
            total = self._page.obtener_resultados()

            # self._page.pause() # Debug UI

            if total < 1:
                log.warning("No se encontraron resultados para los criterios de búsqueda.")
                return
            log.info(f"✅ Se encontraron {total} resultados.")

            # --- Reenviar ---
            if options.reenviar and self._envio:
                resultados["envio"] = self._ejecutar_seguro(
                    self._envio.ejecutar,
                    "Reenvío"
                )

            # --- Imprimir ---
            if options.imprimir and self._impresion:
                resultados["impresion"] = self._ejecutar_seguro(
                    lambda: self._impresion.ejecutar(
                        options.output_filename, options.output_path
                    ),
                    "Impresión"
                )

            # Espera manual tras resultados si está configurada en las opciones de ejecución
            if options.wait_after_results:
                log.info("Pausa manual tras obtener resultados (solo modo UI).")
                self._page.pause()

            return resultados

        except Exception as e:
            # CAMBIO: Uso de config para loguear el código de transacción dinámicamente
            log.error(f"Error en {self._config.transaction_code}: {e}", exc_info=True)
            raise