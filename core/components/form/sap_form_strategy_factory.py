# core/components/form/form_strategy_factory.py

from core.components.form.sap_form_strategies import (
    SimpleFillStrategy,
    RangeFillStrategy,
    ListFillStrategy,
    FormFillingStrategy
)

class SAPFormStrategyFactory:
    """
    Factory responsable de devolver la estrategia adecuada según el valor recibido.
    Permite aplicar el principio Open/Closed (OCP) fácilmente.
    """
    @staticmethod
    def get_strategy(value) -> FormFillingStrategy:
        """
        Retorna la estrategia apropiada basándose en el formato del valor.
        """
        if isinstance(value, list):
            return ListFillStrategy()
        if isinstance(value, str) and ',' in value:
            return RangeFillStrategy()
        return SimpleFillStrategy()
