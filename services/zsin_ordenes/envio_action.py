# services/zsin_ordenes/envio_action.py
import logging

# Asumo que 'pages' está al mismo nivel que 'services'
# Si no, ajusta esta importación
from pages.zsin_ordenes_page import ZsinOrdenesPage

class EnvioOrdenesService:
    def __init__(self, page: ZsinOrdenesPage, logger: logging.Logger):
        self._page = page
        self._log = logger

    def ejecutar(self):
        self._log.info("Acción: Reenviar órdenes.")
        self._page.seleccionar_todas_las_ordenes()
        self._page.reenviar_ordenes()
        self._log.info("✅ Reenvío completado correctamente.")