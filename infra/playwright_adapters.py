from playwright.sync_api import Browser, Page

from core.interfaces.browser_interfaces import IPage, IBrowser

class PlaywrightPageAdapter(IPage):
    def __init__(self, page: Page):
        self._page = page

    def close(self) -> None:
        self._page.close()

    def is_closed(self) -> bool:
        return self._page.is_closed()

class PlaywrightBrowserAdapter(IBrowser):
    def __init__(self, browser: Browser):
        self._browser = browser

    def new_page(self) -> IPage:
        return PlaywrightPageAdapter(self._browser.new_page())

    def close(self) -> None:
        self._browser.close()

    def is_connected(self) -> bool:
        return self._browser.is_connected()
