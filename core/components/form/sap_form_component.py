# core/components/sap_form_component.py

from pydantic import BaseModel
# CAMBIO: Se importa la nueva clase base.
from .sap_component import SAPComponent
from .sap_form_strategies import FormFillingStrategy
from utils.logger import log

# CAMBIO: Ahora hereda de SAPComponent.
class SAPFormComponent(SAPComponent):
    """
    Gestiona el rellenado de campos de un formulario utilizando una estrategia.
    Hereda el contexto de la página (page y provider) de SAPComponent.
    """
    # CAMBIO: El constructor se vuelve trivial.
    def __init__(self, sap_page):
        super().__init__(sap_page)

    def fill_form(self, data: BaseModel, form_map: dict, strategy: FormFillingStrategy):
        log.info(f"Rellenando formulario con la estrategia: {strategy.__class__.__name__}")
        for field, value in data.model_dump(exclude_none=True).items():
            if field in form_map:
                # No hay cambios aquí. Usa self.sap_page, que se hereda de SAPComponent.
                strategy.fill(self.sap_page, form_map, field, value)