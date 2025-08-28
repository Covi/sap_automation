# Fichero: core/adapters.py
from playwright.sync_api import Browser as PWBrowser, Page as PWPage
from core.interfaces.browser_interfaces import IBrowser, IPage

class PlaywrightPageAdapter(IPage):
    def __init__(self, page: PWPage):
        self._page = page

    def goto(self, url: str) -> None:
        self._page.goto(url)

    def close(self) -> None:
        if not self._page.is_closed():
            self._page.close()


class PlaywrightBrowserAdapter(IBrowser):
    def __init__(self, browser: PWBrowser):
        self._browser = browser

    def new_page(self) -> IPage:
        return PlaywrightPageAdapter(self._browser.new_page())

    def close(self) -> None:
        if self._browser.is_connected():
            self._browser.close()
