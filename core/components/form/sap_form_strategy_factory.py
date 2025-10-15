# core/components/form/form_strategy_factory.py

from typing import Any
from .sap_form_strategies import SimpleFillStrategy, RangeFillStrategy, ListFillStrategy, FormFillingStrategy

class SAPFormStrategyFactory:
    """
    Factory que devuelve la estrategia adecuada según el valor recibido.
    """

    @staticmethod
    def get_strategy(value: Any) -> FormFillingStrategy:
        """
        Retorna la estrategia apropiada basándose en el tipo/formato del valor.

        - Si es lista → ListFillStrategy
        - Si es string con coma → RangeFillStrategy
        - Si es cualquier otro valor → SimpleFillStrategy
        """
        if isinstance(value, list):
            return ListFillStrategy()
        if isinstance(value, str) and ',' in value:
            return RangeFillStrategy()
        return SimpleFillStrategy()
