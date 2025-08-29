import calendar, locale
from datetime import datetime, timedelta
from typing import Optional

class DateUtils:
    @staticmethod
    def calcular_fecha_limite(dias: int = 0, formato: str = "%d.%m.%Y") -> str:
        """
        Calcula una fecha sumando un número de días a la fecha actual y la devuelve en el formato especificado.

        Args:
            dias (int): Número de días a sumar a la fecha actual. Si es 0, retorna una cadena vacía.
            formato (str): Formato en el que se devolverá la fecha. Por defecto es "%d.%m.%Y".

        Returns:
            str: Fecha resultante en el formato especificado o una cadena vacía si dias es 0.
        """
        if dias == 0:
            return ""
        fecha_limite = datetime.now() + timedelta(days=dias)
        return fecha_limite.strftime(formato)

    @staticmethod
    def calcular_fecha_limite_new(dias: int = 0) -> Optional[datetime]:
        """
        Calcula una fecha sumando un número de días a la fecha actual y la devuelve como un objeto datetime.

        Args:
            dias (int): Número de días a sumar a la fecha actual. Si es 0, devuelve None.

        Returns:
            datetime: Fecha resultante como un objeto datetime, o None si dias es 0.
        """
        if dias == 0:
            return None
        fecha_limite = datetime.now() + timedelta(days=dias)
        return fecha_limite

    @staticmethod
    def ultimo_dia_del_mes(nombre_mes, año=datetime.now().year, idioma='es_ES.UTF-8'):
        """
        Calcula el último día del mes dado el nombre del mes y el año.
        Devuelve un objeto datetime con la fecha del último día del mes.
        """
        try:
            # Intentamos configurar el locale
            locale.setlocale(locale.LC_TIME, idioma)
        except locale.Error as e:
            # Si falla, mostramos un mensaje y usamos el locale por defecto en España
            print(f"Advertencia: No se pudo configurar el locale '{idioma}'. Usando 'es_ES.UTF-8'.")
            print(f"Error: {e}")
            idioma = 'es_ES.UTF-8'  # Aseguramos que el locale por defecto sea 'es_ES.UTF-8'
            locale.setlocale(locale.LC_TIME, idioma)

        # Buscar el número del mes
        for mes_num in range(1, 13):
            if nombre_mes.lower() == calendar.month_name[mes_num].lower():
                _, ultimo_dia = calendar.monthrange(año, mes_num)
                # Devolvemos un objeto datetime para representar el último día
                return datetime(año, mes_num, ultimo_dia)

        return None  # Mes no válido

    @staticmethod
    def parsear_fecha(input_str: str, base_date: datetime = None, formato: str = "%d.%m.%Y") -> datetime:
        """
        Convierte una cadena en una fecha. Si la cadena empieza por '+' o '-', se interpreta como
        un offset en días respecto a base_date (por defecto, la fecha actual). Si la cadena no tiene signo,
        se considera un número positivo. En caso contrario, se espera que la cadena esté en el formato especificado.

        Args:
            input_str (str): Cadena que representa la fecha o el offset.
            base_date (datetime, optional): Fecha base para calcular el offset. Por defecto es la fecha actual.
            formato (str): Formato en el que se debe interpretar la fecha (por defecto "%d.%m.%Y").

        Returns:
            datetime: Objeto datetime resultante.
        """
        if not input_str:
            return None
        if base_date is None:
            base_date = datetime.now()

        # Si la cadena empieza por '+' o '-', se interpreta como un offset en días
        if input_str.startswith('+') or input_str.startswith('-'):
            try:
                offset = int(input_str)
                return base_date + timedelta(days=offset)
            except ValueError:
                raise ValueError(f"El offset debe ser un entero válido: {input_str}")
        else:
            # Si no tiene signo, se considera un número positivo o una fecha
            try:
                # Si la cadena es un número, la tratamos como un offset
                offset = int(input_str)
                return base_date + timedelta(days=offset)
            except ValueError:
                # Si no es un número, tratamos de convertirlo como fecha
                try:
                    return datetime.strptime(input_str, formato)
                except ValueError:
                    raise ValueError(f"El formato de fecha debe ser '{formato}': {input_str}")