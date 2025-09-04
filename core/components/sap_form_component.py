# Fichero: core/components/sap_form_component.py

from playwright.sync_api import Page
from pydantic import BaseModel
from core.providers.locators.base_locator_provider import BaseLocatorProvider
from .sap_form_strategies import FormFillingStrategy
from utils.logger import log

class SAPFormComponent:
    def __init__(self, page: Page, locator_provider: BaseLocatorProvider):
        self.page = page
        self.locator_provider = locator_provider

    def fill_form(self, data: BaseModel, form_map: dict, strategy: FormFillingStrategy):
        log.info(f"Rellenando formulario con la estrategia: {strategy.__class__.__name__}")
        for field, value in data.model_dump(exclude_none=True).items():
            if field in form_map:
                strategy.fill(self.page, self.locator_provider, form_map, field, value)