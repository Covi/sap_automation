# core/builders/sap_url_builder.py

from typing import Any, List
from pydantic import BaseModel
from config import settings

class SapUrlBuilder:
    @classmethod
    def build_transaction_url(cls, tx_code: str, criteria: BaseModel, config: Any) -> str:
        mapping = config.url_field_mapping
        params_list: List[str] = []
        data = criteria.model_dump(exclude_none=True)
        
        for py_name, value in data.items():
            if py_name in mapping:
                # Extraemos los strings formateados y los metemos a la lista
                params_list.extend(cls._format_low_high(mapping[py_name], value))
        
        # Construcción de la cadena final
        params_str = ";".join(params_list) + ";" if params_list else ""
        prefix = "*" if getattr(config, 'execute_immediately', True) else ""
        base_url = settings.general.base_url.rstrip('/')
        
        return f"{base_url}?~transaction={prefix}{tx_code} {params_str}DYNP_OKCODE=ONLI"

    @staticmethod
    def _format_low_high(sap_name: str, value: Any) -> List[str]:
        """
        Toma el nombre de la hoja y el valor. 
        Si hay dos valores (tupla), usa la base para -LOW y -HIGH.
        Si hay uno, usa el nombre de la hoja TAL CUAL.
        """
        # CASO RANGO: Si CliHandler nos da una tupla (ej. de una coma)
        if isinstance(value, (tuple, list)) and len(value) == 2:
            # Quitamos cualquier sufijo que traiga la hoja para no duplicar (SO_FECH-LOW -> SO_FECH)
            base = sap_name.split('-')[0] 
            v_low, v_high = value
            res = []
            if v_low: res.append(f"{base}-LOW={v_low}")
            if v_high: res.append(f"{base}-HIGH={v_high}")
            return res

        # CASO ÚNICO: Se usa el nombre de la hoja EXACTO (Settings)
        # Si en settings pusiste SO_STAT-LOW, saldrá SO_STAT-LOW=valor
        # Si pusiste P_VARI, saldrá P_VARI=valor
        return [f"{sap_name}={value}"]