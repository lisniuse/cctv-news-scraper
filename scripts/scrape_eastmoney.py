#!/usr/bin/env python3
"""
Scrape today's CCTV Xinwen Lianbo (新闻联播) news summary from EastMoney.

Usage:
    python scrape_eastmoney.py [--date YYYY-MM-DD] [--headless]

Arguments:
    --date      Specify a date (default: today). Format: YYYY-MM-DD
    --headless  Run browser in headless mode (default: headed)

Output:
    Prints the HTML content of today's 新闻联播要闻集锦 article to stdout.

Requirements:
    pip install playwright
    playwright install chromium
"""

from playwright.sync_api import sync_playwright
import datetime
import sys
import argparse


def scrape_news(target_date=None, headless=False):
    """
    Scrape CCTV Xinwen Lianbo news summary from EastMoney.

    Args:
        target_date: datetime.date object for the target date (default: today)
        headless: Whether to run browser in headless mode

    Returns:
        str: The HTML content of the news article, or None if not found
    """
    if target_date is None:
        target_date = datetime.date.today()

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=headless,
            args=["--disable-blink-features=AutomationControlled"]
        )

        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720}
        )

        page = context.new_page()
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        url = "https://so.eastmoney.com/web/s?keyword=%E6%96%B0%E9%97%BB%E8%81%94%E6%92%AD"
        print(f"Opening {url}...", file=sys.stderr)
        page.goto(url)

        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            print("Network idle timeout, continuing...", file=sys.stderr)

        target_text = f"{target_date.month}月{target_date.day}日晚间央视新闻联播要闻集锦"
        print(f"Looking for: {target_text}", file=sys.stderr)

        target_href = None

        # Strategy 1: Find via div.news_item_t
        news_divs = page.locator("div.news_item_t")
        count = news_divs.count()

        if count == 0:
            # Strategy 2: Direct link text match
            link = page.locator(f"a:text-is('{target_text}')")
            if link.count() > 0:
                target_href = link.first.get_attribute("href")
            else:
                # Strategy 3: Partial match
                link = page.locator(f"a:has-text('{target_text}')")
                if link.count() > 0:
                    target_href = link.first.get_attribute("href")
        else:
            for i in range(count):
                div = news_divs.nth(i)
                a_tag = div.locator("a").first
                if a_tag.count() == 0:
                    continue
                text = a_tag.inner_text().strip()
                if text == target_text:
                    target_href = a_tag.get_attribute("href")
                    break

        if not target_href:
            print("Could not find the target link.", file=sys.stderr)
            browser.close()
            return None

        # Normalize href
        if not target_href.startswith("http"):
            if target_href.startswith("/"):
                target_href = "https://www.eastmoney.com" + target_href
            else:
                target_href = "https://www.eastmoney.com/" + target_href

        print(f"Navigating to {target_href}...", file=sys.stderr)
        page.goto(target_href)
        page.wait_for_load_state("domcontentloaded")

        # Extract article content
        content_div = page.locator("div#ContentBody.txtinfos")
        result = None

        if content_div.count() > 0:
            html_content = content_div.evaluate("""element => {
                const videos = element.querySelectorAll('video');
                videos.forEach(v => v.remove());

                const all = element.querySelectorAll('*');
                for (const el of all) {
                    const allowedAttrs = ['src', 'href', 'colspan', 'rowspan', 'title', 'alt'];
                    const attrsToRemove = [];
                    for (const attr of el.attributes) {
                        if (!allowedAttrs.includes(attr.name)) {
                            attrsToRemove.push(attr.name);
                        }
                    }
                    attrsToRemove.forEach(name => el.removeAttribute(name));
                }
                return element.innerHTML;
            }""")

            parts = html_content.split("<!--文章主体-->")
            if len(parts) >= 2:
                result = parts[1]
            else:
                result = html_content
        else:
            print("Could not find content div (div#ContentBody.txtinfos)", file=sys.stderr)

        browser.close()
        return result


def main():
    parser = argparse.ArgumentParser(description="Scrape CCTV Xinwen Lianbo news from EastMoney")
    parser.add_argument("--date", type=str, default=None, help="Target date in YYYY-MM-DD format (default: today)")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode")
    args = parser.parse_args()

    target_date = None
    if args.date:
        target_date = datetime.date.fromisoformat(args.date)

    content = scrape_news(target_date=target_date, headless=args.headless)

    if content:
        print(content)
    else:
        print("Failed to retrieve news content.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
