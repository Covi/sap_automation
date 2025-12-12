# services/zsin_ordenes/service.py

# 1. LIBRERÍA ESTÁNDAR
import logging
from typing import Callable, Dict, Optional

# 2. LIBRERÍAS DE TERCEROS
# (Sin cambios)

# 3. MÓDULOS LOCALES (Tu Proyecto)
from config.settings import ZsinOrdenesConfig
from core.builders.sap_payload_builder import SapPayloadBuilder
from core.protocols import FileHandlerProtocol, PrintServiceProtocol
from pages.zsin_ordenes_page import ZsinOrdenesPage
from schemas.zsin_ordenes import ZsinOrdenesCriteria, ZsinOrdenesExecutionOptions
from services.transaction_service import TransactionService
from .envio_action import EnvioOrdenesService
from .impresion_action import ImpresionOrdenesService


log = logging.getLogger(__name__)

class ZsinOrdenesService:
    """
    Servicio para la transacción ZSIN_ORDENES.
    Orquesta la ejecución, impresión y envío de órdenes basándose en una configuración inyectada.
    """
    # TIPADO: _impresion es opcional (depende de inyecciones externas). 
    # _envio es OBLIGATORIO (solo depende de Page/Log).
    _impresion: Optional[ImpresionOrdenesService] 
    _envio: EnvioOrdenesService 
    
    def __init__(
        self,
        transaction_service: TransactionService,
        page: ZsinOrdenesPage,
        config: ZsinOrdenesConfig,  # Inyección obligatoria de la configuración
        file_handler: Optional[FileHandlerProtocol] = None,
        print_service: Optional[PrintServiceProtocol] = None,
    ):
        self._transaction_service = transaction_service
        self._page = page
        self._config = config
        self._file_handler = file_handler
        self._print_service = print_service

        self._impresion = None
        
        # Inicialización de subservicios
        # Impresión: CONDICIONAL (depende de inyecciones opcionales)
        if file_handler and print_service:
            self._impresion = ImpresionOrdenesService(page, file_handler, print_service, log)
        
        # Envío: OBLIGATORIO (POM que solo depende de Page y Log)
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

    def _pause(self):
        """
        Pausa la ejecución de la página (solo en modo UI).
        """
        log.info("Pausa manual tras obtener resultados (solo modo UI).")
        self._page.pause()

    def _estabilizar_ui_post_accion(self, accion_anterior: str):
        """
        Protocolo para estabilizar la UI de SAP después de una acción que implica
        una llamada de red (reenvío, impresión, etc.) y evita el TimeoutError.
        """
        log.info(f"Servicio: Iniciando protocolo de estabilización de la UI tras la acción '{accion_anterior}'.")
        
        # 1. Desbloqueo de UI (La base se encarga de esperar el 'ur-loading-box')
        self._page.wait_for_page_to_be_ready(timeout=30000)
        
        # 2. Validación de Negocio (Comprobación de éxito en la barra de estado)
        # Esto confirma que la acción anterior se procesó correctamente.
        success_message = self._page.check_status_bar_for_message_type("Success")
        if not success_message:
            log.warning(f"Servicio: No se detectó mensaje de éxito en barra de estado post-{accion_anterior}.")
        else:
            log.info(f"Servicio: Acción '{accion_anterior}' confirmada por mensaje: '{success_message}'")
        
        # 3. Confirmación de Elemento (Aseguramos que la tabla de resultados sigue interactiva)
        self._page.results_table.is_visible(timeout=5000)
        
        log.info("Servicio: La UI está estable y lista para la siguiente acción.")

    def run(self, criteria: ZsinOrdenesCriteria, options: ZsinOrdenesExecutionOptions):
        """
        Orquesta el flujo completo de la transacción ZSIN_ORDENES.

        :param criteria: Criterios de búsqueda para el formulario.
        :param options: Opciones de ejecución (acciones, configuración de salida).
        """
        try:
            resultados: Dict[str, Dict[str, str]] = {}

            self._transaction_service.run_transaction(self._config.transaction_code)

            # Modelo
            payload = SapPayloadBuilder.build_payload(criteria)
            
            # Proceso UI
            self._page.esperar_formulario()
            self._page.rellenar_formulario(payload)
            self._page.ejecutar()
            self._page.esperar_resultados(60000)

            # --- Resultados y Salida Temprana ---
            total = self._page.obtener_resultados()

            if total < 1:
                log.warning("No se encontraron resultados para los criterios de búsqueda.")
                if options.wait_after_results:
                    self._pause()
                return 

            log.info(f"✅ Se encontraron {total} resultados.")

            # --- Reenviar (El uso sigue siendo condicional) ---
            envio_service = self._envio
            if options.reenviar and envio_service: 
                resultados["envio"] = self._ejecutar_seguro(
                    envio_service.ejecutar,
                    "Reenvío"
                )

                # *** Se llama al protocolo de estabilización después de Reenvío ***
                self._estabilizar_ui_post_accion("Reenvío")

            # --- FIXME Pausa DEBUG temporal ---
            if options.wait_after_results:
                self._pause()

            # --- Imprimir (Type Narrowing y Optional Check) ---
            impresion_service = self._impresion
            if options.imprimir and impresion_service:
                resultados["impresion"] = self._ejecutar_seguro(
                    lambda: impresion_service.ejecutar(
                        options.output_filename, options.output_path
                    ),
                    "Impresión"
                )
                # *** Si hubiera una acción después de Imprimir, se llamaría aquí ***
                # self._estabilizar_ui_post_accion("Impresión")

            # --- Pausa ---
            if options.wait_after_results:
                self._pause()

            return resultados

        except Exception as e:
            log.error(f"Error en {self._config.transaction_code}: {e}", exc_info=True)
            raise