import sys 
import asyncio
from playwright.async_api import async_playwright
import re

# combining webscrape.py and practice_async.py, multiple webscraping takes long, so we use async to speed it up 
# information (as in urls) are all stored in a csv file, should provide the path to the csv file as an argument
# or maybe just provide all the urls as an argument? like [xxx, xxx, xxx]

async def process_url(browser, url, take_screenshot):
    page = await browser.new_page()
    await page.goto(url, wait_until="domcontentloaded", timeout=90000) # 90 seconds timeout
    if take_screenshot:
        await capture_screenshot(page)
    else:
        await save_page_text(page, "main article", url)

async def run(playwright, urls, take_screenshot=False):
    browser = await playwright.chromium.launch(headless=False)

    sem = asyncio.Semaphore(4) # limit concurrent tasks to 4

    async def process_url_with_semaphore(url):
        async with sem:
            await process_url(browser, url, take_screenshot)
    tasks = [
        process_url_with_semaphore(url) for url in urls
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)
    await browser.close()

    #report which ones failed
    for url, result in zip(urls, results):
        if isinstance(result, Exception):
            print(f"Failed to process {url}: {result}")
        
async def main(urls, take_screenshot):
    async with async_playwright() as playwright:
        await run(playwright, urls, take_screenshot)

async def capture_screenshot(page):
    title = await page.title()
    filename = create_safe_filename(title).with_suffix(".png")
    await page.screenshot(path=filename, full_page=True)
    print(f"Screenshot saved as {filename}")

other_selectors = ["div.article__content", "div[itemprop='articleBody']", "article", "main"]

async def save_page_text(page, selector, url):
    title = await page.title()
    content = await page.query_selector(selector)
    if not content:
        for item in other_selectors:
            content = await page.query_selector(item)
            if content: break # Fallback to body if selector not found
    text = (
        await content.inner_text() if content else "No requested selector found."
    )
    filename = create_safe_filename(title)

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"URL: {url}\n")
        f.write(f"Title: {title}\n\n")
        f.write(text)
    print(f"Data saved as {filename}")

from pathlib import Path
save_directory = Path(__file__).parent / "scraped_data"
save_directory.mkdir(parents=True, exist_ok=True)
def create_safe_filename(title):
    safe_title = re.sub(r"[^\w\s-]", "", title).strip().replace(" ", "_")
    #dont make titles too long
    safe_title = safe_title[:100] or "untitled"
    return save_directory / f"{safe_title}.txt"

# def read_urls_from_csv(csv_file):
    #urls = []
    #with open(csv_file, "r", encoding="utf-8") as f:
        #for line in f:
            #url = line.strip()
            #if url:
                #urls.append(url)
    #return urls

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python playwright.py <URL> [--screenshot]")
        sys.exit(1)

    urls = sys.argv[1:]
    take_screenshot = "--screenshot" in urls
    urls = [url for url in urls if url != "--screenshot"]

    asyncio.run(main(urls, take_screenshot))
