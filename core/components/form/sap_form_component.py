# core/components/form/sap_form_component.py

# Logging
import logging
log = logging.getLogger(__name__)

from pydantic import BaseModel
from ..sap_component import SAPComponent
from .sap_form_strategies import FormFillingStrategy

class SAPFormComponent(SAPComponent):
    """
    Gestiona el rellenado de campos de un formulario utilizando una estrategia.
    Hereda el contexto de la página (page y provider) de SAPComponent.
    """
    # Constructor del padre.
    def __init__(self, sap_page):
        super().__init__(sap_page)

    def fill_form(self, data: BaseModel, form_map: dict, strategy: FormFillingStrategy):
        log.info(f"Rellenando formulario con la estrategia: {strategy.__class__.__name__}")
        for field, value in data.model_dump(exclude_none=True).items():
            if field in form_map:
                # Usa self.sap_page, que se hereda de SAPComponent.
                strategy.fill(self.sap_page, form_map, field, value)