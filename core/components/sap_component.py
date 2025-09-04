# core/components/sap_component.py

from pages.sap_page_base import SAPPageBase

class SAPComponent:
    """
    Clase base para todos los componentes de SAP.
    Proporciona acceso común al contexto de la página (incluyendo el objeto
    Page de Playwright) y al proveedor de localizadores.
    """
    def __init__(self, sap_page: SAPPageBase):
        # 1. Guardamos una referencia a la página SAP completa con un nombre claro.
        self.sap_page = sap_page
        
        # 2. Usamos la @property para obtener el objeto de Playwright de forma segura.
        self.playwright_page = sap_page.playwright_page
        
        # 3. Obtenemos el provider.
        self._provider = sap_page._provider