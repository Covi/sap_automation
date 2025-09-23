# Fichero: core/components/form/sap_form_component.py (Versión SOLID)

import logging
from typing import Dict
from ..sap_component import SAPComponent
from .sap_form_strategies import FormFillingStrategy

log = logging.getLogger(__name__)

class SAPFormComponent(SAPComponent):
    """
    Componente "tonto" que rellena un formulario a partir de un diccionario simple.
    Está completamente desacoplado de los modelos de datos.
    """

    def __init__(self, sap_page):
        super().__init__(sap_page)

    def fill_form(self, payload: Dict, form_map: dict, strategy: FormFillingStrategy):
        """
        Rellena un formulario desde un payload (diccionario).

        Args:
            payload: Diccionario simple con los datos a rellenar.
            form_map: Diccionario que mapea los campos a los locators.
            strategy: La estrategia de rellenado a utilizar.
        """
        log.info(f"Rellenando formulario con la estrategia: {strategy.__class__.__name__}")
        log.info("Asegurando estado limpio y rellenando formulario...")

        # --- PASO 1: Bucle de Limpieza Total ---
        # Itera sobre TODOS los campos que el Page Object conoce y los limpia.
        for field_name, locator in form_map.items():
            locator.clear()
            log.debug(f"Campo '{field_name}' limpiado.")

        # --- PASO 2: Bucle de Rellenado Inteligente ---
        # Itera directamente sobre el diccionario, filtrando valores nulos.
        for field, value in payload.items():
            if value is not None and field in form_map:
                strategy.fill(self.sap_page, form_map, field, value)