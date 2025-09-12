from typing import Tuple, Optional

class RangeParser:
    """
    Utilidad con la responsabilidad única de parsear la sintaxis de un rango.
    Es agnóstico al tipo de dato que contiene el rango.
    """
    @staticmethod
    def parse(rango_str: Optional[str], separador: str = ',') -> Tuple[Optional[str], Optional[str]]:
        """
        Toma un string de rango y lo divide en una tupla de dos strings.

        Ejemplos:
        - "val1,val2" -> ("val1", "val2")
        - ",val2"     -> ("", "val2")
        - "val1,"     -> ("val1", "")
        - "val1"      -> ("val1", None)  (Maneja el caso de un solo valor)
        - None        -> (None, None)

        Args:
            rango_str: El string de entrada a parsear.
            separador: El carácter que delimita los valores del rango.

        Returns:
            Una tupla con los dos valores del rango.
        """
        if rango_str is None:
            return (None, None)

        partes = rango_str.split(separador, 1)
        
        desde = partes[0].strip()
        
        # Si no había separador, la parte "hasta" no existe.
        hasta = partes[1].strip() if len(partes) > 1 else None

        return (desde, hasta)
