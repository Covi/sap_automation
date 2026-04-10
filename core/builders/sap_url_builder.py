# core/builders/sap_url_builder.py

from typing import Any, List
from pydantic import BaseModel
from config import settings

class SapUrlBuilder:
    """
    Constructor de URLs para la ejecución de transacciones en SAP WebGUI.
    
    Esta clase permite generar enlaces directos con parámetros pre-rellenados,
    optimizando la navegación mediante el uso de Fast-Path.
    """

    @classmethod
    def build_transaction_url(cls, tx_code: str, criteria: BaseModel, config: Any) -> str:
        """
        Genera una URL completa para una transacción de SAP con parámetros.

        Args:
            tx_code: Código de la transacción (ej. 'IQ09').
            criteria: Objeto Pydantic con los datos del formulario.
            config: Configuración específica de la transacción (mapeos y flags).

        Returns:
            str: URL codificada para acceso directo vía WebGUI.
        """
        mapping = config.url_field_mapping
        params_list: List[str] = []
        
        # model_dump extrae solo los campos informados para evitar basura en la URL
        data = criteria.model_dump(exclude_none=True)
        
        for py_name, value in data.items():
            if py_name in mapping:
                # Se utiliza cls para llamar al método estático de formateo
                params_list.extend(cls._format_low_high(mapping[py_name], value))
        
        # Construcción de la query string
        params_str = ";".join(params_list) + ";" if params_list else ""
        
        # El prefijo '*' en SAP indica ejecución inmediata (Fast-Path)
        prefix = "*" if getattr(config, 'execute_immediately', True) else ""
        base_url = settings.general.base_url.rstrip('/')
        
        return f"{base_url}?~transaction={prefix}{tx_code} {params_str}DYNP_OKCODE=ONLI"

    @staticmethod
    def _format_low_high(sap_name: str, value: Any) -> List[str]:
        """
        Formatea pares campo-valor para el motor de parámetros de SAP.

        Maneja tanto campos simples como rangos (LOW/HIGH) cuando el valor
        es una estructura de tipo secuencia.

        Args:
            sap_name: Nombre técnico del campo en SAP.
            value: Valor o conjunto de valores a asignar.

        Returns:
            List[str]: Lista de strings con el formato 'CAMPO=VALOR'.
        """
        # Caso de rango: Si el valor es una tupla o lista de 2 elementos (ej. fechas)
        if isinstance(value, (tuple, list)) and len(value) == 2:
            # Normalizamos la base del nombre técnico para evitar duplicidad de sufijos
            base = sap_name.split('-')[0] 
            v_low, v_high = value
            res = []
            
            if v_low: 
                res.append(f"{base}-LOW={v_low}")
            if v_high: 
                res.append(f"{base}-HIGH={v_high}")
                
            return res

        # Caso único: Asignación directa según el nombre técnico definido en la configuración
        return [f"{sap_name}={value}"]