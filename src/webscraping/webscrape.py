import sys
from playwright.sync_api import sync_playwright

def run(playwright, url, take_screenshot=False):
    browser = playwright.chromium.launch()
    page = browser.new_page()
    page.goto(url)

    if take_screenshot:
        page.screenshot(path="screenshot.png", full_page=True)
        print("Screenshot saved as screenshot.png")

    browser.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python playwright.py <URL> [--screenshot]")
        sys.exit(1)

    url = sys.argv[1]
    take_screenshot = "--screenshot" in sys.argv

    with sync_playwright() as playwright:
        run(playwright, url, take_screenshot)