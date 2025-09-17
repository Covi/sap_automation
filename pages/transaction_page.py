# Fichero: pages/transaction_page.py

from .sap_page_base import SAPPageBase

class TransactionPage(SAPPageBase):
    """
    Representa la pantalla de una transacción DESPUÉS de que ha cargado.
    Hereda todos los elementos y métodos comunes de SAPPageBase.
    """
    def __init__(self, page, locator_provider):
        # Llama al constructor de la clase padre (SAPPageBase) para inicializar
        # el provider, la barra de estado, el indicador de carga, etc.
        super().__init__(page, locator_provider)

    def wait_for_load(self):
        """
        Espera a que la página de la transacción cargue completamente.
        Reutiliza el método robusto de la clase padre.
        """
        # Este método ahora es mucho más simple y legible.
        self._loading_disappear()
        
        # Opcional: podrías añadir una comprobación extra si es necesario
        # self.status_bar.wait_for(state="visible")
        
        return self

    # Aquí es donde añadirías los métodos para interactuar con la pantalla
    # de la transacción una vez que ha cargado. Por ejemplo:
    # def fill_centro_field(self, centro_code: str):
    #     ...