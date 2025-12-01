# Fichero: services/zsin_ordenes/service.py (Organizado según PEP 8)

# 1. LIBRERÍA ESTÁNDAR
import logging
from typing import Callable, Dict, Optional # Ordenado alfabéticamente

# 2. LIBRERÍAS DE TERCEROS (Asumimos que estas no son externas/terceras en este ejemplo)
# Si tuvieras 'requests' o algo similar, iría aquí.

# 3. MÓDULOS LOCALES (Tu Proyecto)
from config import ZsinOrdenesConfig
from core.builders.sap_payload_builder import SapPayloadBuilder
from core.protocols import FileHandlerProtocol, PrintServiceProtocol
from pages.zsin_ordenes_page import ZsinOrdenesPage
from schemas.zsin_ordenes import ZsinOrdenesCriteria, ZsinOrdenesExecutionOptions
from services.transaction_service import TransactionService

# 4. IMPORTACIONES RELATIVAS (Dentro del paquete 'zsin_ordenes')
from .envio_action import EnvioOrdenesService
from .impresion_action import ImpresionOrdenesService


log = logging.getLogger(__name__)

class ZsinOrdenesService:
    """
    Servicio para la transacción ZSIN_ORDENES.

    :param transaction_service: Servicio genérico de transacciones SAP.
    :param page: Página de la transacción ZSIN_ORDENES.
    :param file_handler: Servicio opcional para manejo de ficheros.
    :param print_service: Servicio opcional para impresión.
    """
    def __init__(
        self,
        transaction_service: TransactionService,
        page: ZsinOrdenesPage,
        file_handler: Optional[FileHandlerProtocol] = None,
        print_service: Optional[PrintServiceProtocol] = None,
    ):
        self._transaction_service = transaction_service
        self._page = page
        self._config = ZsinOrdenesConfig()
        self._file_handler = file_handler
        self._print_service = print_service

        # Inyección de subservicios especializados
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

    # --- La firma y la lógica del método 'run' se actualizan ---
    def run(self, criteria: ZsinOrdenesCriteria, options: ZsinOrdenesExecutionOptions):
        """
        Orquesta el flujo completo de la transacción ZSIN_ORDENES.

        :param criteria: Criterios de búsqueda para el formulario.
        :param options: Opciones de ejecución (acciones, configuración de salida).
        """
        try:
            resultados: Dict[str, Dict[str, str]] = {}

            self._transaction_service.run_transaction(self._config.TRANSACTION_CODE)

            # Modelo
            payload = SapPayloadBuilder.build_payload(criteria)
            # Recuperar la espera del formulario antes de rellenarlo
            self._page.esperar_formulario()
            self._page.rellenar_formulario(payload)
            # FIXME Pausa con resultados
            # log.info("Pausa manual para ver el formulario (solo modo UI).")
            # self._page.pause()
            self._page.ejecutar()
            self._page.esperar_resultados(60000)

            # --- Resultados ---
            total = self._page.obtener_resultados()

            # FIXME Pausa con resultados
            # log.info("Pausa manual para ver los resultados (solo modo UI).")
            # self._page.pause()

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

            # FIXME No está pausando
            # Espera manual tras resultados si está configurada
            # No hace falta getattr porque wait_after_results es pydantic y está en ZsinOrdenesExecutionOptions
            if options.wait_after_results:
                log.info("Pausa manual tras obtener resultados (solo modo UI).")
                self._page.pause()

            # --- Fin, return ---
            return resultados

        except Exception as e:
            log.error(f"Error en ZSIN_ORDENES: {e}", exc_info=True)
            raise
