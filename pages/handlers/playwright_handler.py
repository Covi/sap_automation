# pages/handlers/playwright_handler.py

from protocols.page_handler_interface import PageHandlerInterface
from playwright.sync_api import Page

class PlaywrightHandler(PageHandlerInterface):
    def __init__(self, page: Page):
        self.page = page

    def goto(self, url: str):
        self.page.goto(url)
    
    def get_title(self) -> str:
        return self.page.title()

    def press_enter(self):
        self.page.keyboard.press("Enter")

    def pause(self):
        self.page.pause()
