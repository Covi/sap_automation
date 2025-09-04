from playwright.sync_api import Locator
from utils.logger import log
# CAMBIO: Se importa la nueva clase base del componente.
from ..sap_component import SAPComponent
# Se importa la clase base de página para el type hinting
from pages.sap_page_base import SAPPageBase


class SAPMenuComponent(SAPComponent):
    """
    Gestiona la interacción con el menú de navegación superior estándar de SAP.
    Su única responsabilidad es navegar a través de una ruta de menú proporcionada.
    """
    def __init__(self, sap_page: SAPPageBase):
        # CAMBIO: Llama al constructor de la clase base.
        super().__init__(sap_page)

    def _get_menu_item(self, text: str) -> Locator:
        """
        Localiza un elemento de menú por su texto, priorizando roles semánticos.
        """
        # FIXME Hay que usar locators de archivos .toml y los providers
        locator_con_rol = self.playwright_page.get_by_role("cell", name=text, exact=True) \
            .or_(self.playwright_page.get_by_role("button", name=text, exact=True)) \
            .or_(self.playwright_page.get_by_role("menuitem", name=text, exact=True))

        return locator_con_rol.or_(self.playwright_page.get_by_text(text, exact=True))

    def navigate_to(self, *path: str):
        """
        Navega a través de una secuencia de clics en el menú.
        """
        log.info(f"Navegando por el menú: {' -> '.join(path)}")
        for item_text in path:
            menu_item = self._get_menu_item(item_text).first
            menu_item.click()
            log.debug(f"Clic en el menú: {item_text}")