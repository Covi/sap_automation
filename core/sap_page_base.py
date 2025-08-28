# pages/sap_page_base.py
from typing import TYPE_CHECKING
from .page_base import PageBase
from .providers.base_provider import BaseLocatorProvider

if TYPE_CHECKING:
    from core.interfaces.browser_interfaces import IPage, ILocator

class SAPPageBase(PageBase):
    """
    Clase base para todas las páginas SAP.
    Proporciona acceso y métodos para interactuar con elementos comunes de SAP.
    """
    def __init__(self, page: "IPage", locator_provider: BaseLocatorProvider):
        super().__init__(page)
        self._provider = locator_provider

        # --- Elementos comunes de SAP ---
        self.status_bar: "ILocator" = page.locator(self._provider.get('common.status_bar'))
        self.execute_button: "ILocator" = page.locator(self._provider.get('common.ejecutar'))

    # --- Métodos de acción comunes ---
    def get_status_bar_text(self) -> str:
        self.status_bar.wait_for(state="visible")
        return self.status_bar.inner_text()

    def accept(self):
        self.page.keyboard.press("Enter")

    def execute(self):
        self.execute_button.click()

    def _fill_form(self, form_locators_map: dict, form_data: object):
        """
        Rellena un formulario según un mapa de locators y un objeto de datos.
        """
        for field_name, field_value in vars(form_data).items():
            if field_value is not None and field_name in form_locators_map:
                locator: "ILocator" = form_locators_map[field_name]
                locator.fill(str(field_value))
