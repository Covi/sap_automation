# core/components/form/sap_form_component.py

import logging
from typing import Dict
from ..sap_component import SAPComponent
from .sap_form_strategy_factory import SAPFormStrategyFactory
log = logging.getLogger(__name__)


class SAPFormComponent(SAPComponent):
    """
    Componente genérico que rellena un formulario SAP a partir de un diccionario simple.
    Está completamente desacoplado de los modelos de datos.
    """

    def __init__(self, sap_page):
        super().__init__(sap_page)

    def fill_form(self, payload: Dict, form_map: dict):
        """
        Rellena un formulario desde un payload (diccionario),
        seleccionando automáticamente la estrategia adecuada para cada campo.

        Args:
            payload: Diccionario simple con los datos a rellenar.
            form_map: Diccionario que mapea los nombres de campo con sus locators.
        """
        log.info("Iniciando proceso de rellenado de formulario con estrategias automáticas...")

        # --- PASO 1: Limpieza total de los campos ---
        for field_name, locator in form_map.items():
            try:
                # Soporte para campos con múltiples locators (listas)
                if isinstance(locator, list):
                    for loc in locator:
                        loc.clear()
                else:
                    locator.clear()
                log.debug(f"Campo '{field_name}' limpiado.")
            except Exception as e:
                log.warning(f"No se pudo limpiar el campo '{field_name}': {e}")

        # --- PASO 2: Rellenado dinámico con estrategia adecuada ---
        for field, value in payload.items():
            if field not in form_map:
                log.debug(f"Ignorando campo '{field}' (no mapeado en form_map).")
                continue

            if value is None or value == "":
                log.debug(f"Campo '{field}' vacío o nulo, se omite.")
                continue

            try:
                strategy = SAPFormStrategyFactory.get_strategy(value)
                strategy.fill(self.sap_page, form_map, field, value)
                log.debug(f"Campo '{field}' rellenado con valor '{value}' usando {strategy.__class__.__name__}.")
            except Exception as e:
                log.error(f"Error rellenando campo '{field}': {e}")

        log.info("Formulario completado con éxito.")
