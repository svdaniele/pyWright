from playwright.sync_api import sync_playwright


class PlaywrightHelper:
    def __init__(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=False)
        self.page = self.browser.new_page()

    def close(self):
        self.browser.close()
        self.playwright.stop()
