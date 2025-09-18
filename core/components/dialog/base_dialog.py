# components/dialog/base_dialog.py

from core.components.sap_component import SAPComponent

class BaseDialog(SAPComponent):
    # La clase hija debe sobrescribir esta lista
    _specific_locators = []
    # Usamos un nombre agnóstico
    LOCATOR_SECTION = None 

    def __init__(self, sap_page):
        super().__init__(sap_page)
        provider = self._provider
        
        self.boton_continuar = self.playwright_page.locator(provider.get('common.continuar'))
        self.boton_ok = self.playwright_page.locator(provider.get('common.ok'))
        
        section_path = self._locator_section_name()
        for locator_name in self._specific_locators:
            full_locator_path = f"{section_path}.{locator_name}"
            locator_string = provider.get(full_locator_path)
            setattr(self, locator_name, self.playwright_page.locator(locator_string))

    def _locator_section_name(self) -> str:
        if not self.LOCATOR_SECTION:
            raise NotImplementedError("La clase hija debe definir un nombre de sección en LOCATOR_SECTION.")
        return self.LOCATOR_SECTION