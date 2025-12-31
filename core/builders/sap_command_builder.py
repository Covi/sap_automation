# core/builders/sap_command_builder.py

# FIXME ...me chirría, esto simplemente construye cadenas de texto..., 
# ha sido sacar el hardcodeo del TRX_Service y ponerlo en un builder y ya parece "builder", pero no lo es.
# Lo dejo para probar el sistema provisionalmente, pero hay que replantearlo luego.
class SapCommandBuilder:
    @staticmethod
    def build_standard(trx_code: str) -> str:
        """Comando de navegación limpia."""
        return f"/n{trx_code}"

    @staticmethod
    def build_fast_path(trx_code: str, url_params: str) -> str:
        """Comando de ejecución directa con parámetros."""
        # Aquí vive el asterisco y el OKCODE de ejecución
        return f"*{trx_code} {url_params}DYNP_OKCODE=ONLI"