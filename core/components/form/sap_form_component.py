# core/components/form/sap_form_component.py

import logging
from typing import Dict, Any, Optional
from ..sap_component import SAPComponent
from .sap_form_strategy_factory import SAPFormStrategyFactory
from .sap_form_strategies import FormFillingStrategy

log = logging.getLogger(__name__)

class SAPFormComponent(SAPComponent):
    """
    Componente agnóstico para rellenar formularios SAP desde un diccionario.
    Funciona con estrategias simples, rangos y listas.
    """

    def __init__(self, sap_page):
        super().__init__(sap_page)

    def fill_form(self, payload: Dict[str, Any], form_map: dict, strategy: Optional[FormFillingStrategy] = None):
        """
        Rellena un formulario usando la estrategia proporcionada o la factory.

        Args:
            payload: Diccionario con los valores a rellenar.
            form_map: Diccionario que mapea nombres de campos a locators.
            strategy: Estrategia opcional. Si es None, se determina por cada valor.
        """
        log.info("Asegurando estado limpio y rellenando formulario...")

        # --- Limpieza de todos los locators ---
        for field_name, locators in form_map.items():
            if isinstance(locators, list):
                for loc in locators:
                    loc.clear()
            else:
                locators.clear()
            log.debug(f"Campo '{field_name}' limpiado.")

        # --- Rellenado ---
        for field, value in payload.items():
            if value is None or field not in form_map:
                continue

            # Determinar la estrategia: la pasada o por factory
            s: FormFillingStrategy = strategy or SAPFormStrategyFactory.get_strategy(value)
            s.fill(form_map, field, value)
