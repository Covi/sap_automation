# --- infra/playwright_browser_factory.py ---
from playwright.sync_api import sync_playwright
from core.interfaces.browser_interfaces import IBrowserFactory, IBrowser
from .playwright_adapters import PlaywrightBrowserAdapter

class PlaywrightBrowserFactory(IBrowserFactory):
    def __init__(self, browser_type: str = "firefox", headless: bool = True):
        self.browser_type = browser_type
        self.headless = headless
        self._playwright = None

    def create_browser(self) -> IBrowser:
        self._playwright = sync_playwright().start()
        if self.browser_type == "chromium":
            browser = self._playwright.chromium.launch(headless=self.headless)
        elif self.browser_type == "webkit":
            browser = self._playwright.webkit.launch(headless=self.headless)
        else:
            browser = self._playwright.firefox.launch(headless=self.headless)
        return PlaywrightBrowserAdapter(browser)

    def stop(self):
        if self._playwright:
            self._playwright.stop()
