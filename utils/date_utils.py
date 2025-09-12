import calendar
import locale
from datetime import datetime, timedelta, date
from typing import Optional

class DateUtils:
    @staticmethod
    def parsear_fecha(input_str: Optional[str], base_date: Optional[date] = None) -> Optional[date]:
        """
        Convierte un string en un objeto date.
        - "+N" o "-N" → offset de días respecto a base_date (por defecto, hoy)
        - Fechas absolutas: "12.09.2025", "12/09/2025", "2025-09-12"
        """
        if not input_str or not input_str.strip():
            return None

        valor = input_str.strip()
        base_date = base_date or date.today()

        # Offset con signo
        if valor.startswith(("+", "-")):
            try:
                return base_date + timedelta(days=int(valor))
            except ValueError:
                raise ValueError(f"Offset inválido: {valor}")

        # Offset positivo sin signo
        try:
            return base_date + timedelta(days=int(valor))
        except ValueError:
            pass

        # Formatos de fecha
        formatos = ["%d.%m.%Y", "%d/%m/%Y", "%Y-%m-%d"]
        for fmt in formatos:
            try:
                return datetime.strptime(valor, fmt).date()
            except ValueError:
                continue

        raise ValueError(f"Formato de fecha no válido: '{valor}'")

    @staticmethod
    def formatear_fecha(fecha: Optional[date], formato: str = "%d.%m.%Y") -> Optional[str]:
        """Convierte un date a string en el formato indicado (para SAP)."""
        if not fecha:
            return None
        return fecha.strftime(formato)
