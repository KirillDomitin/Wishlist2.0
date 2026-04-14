import json
import re
from decimal import Decimal, InvalidOperation
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

try:
    from playwright.async_api import async_playwright
    from playwright.async_api import TimeoutError as PlaywrightTimeout
    _PLAYWRIGHT_AVAILABLE = True
except ImportError:
    _PLAYWRIGHT_AVAILABLE = False

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
}
_TIMEOUT = 10.0
_BROWSER_TIMEOUT = 30_000  # ms


def _clean_price(raw: str) -> Decimal | None:
    """Extract a numeric price from a string like '1 299 ₽', '12.99', '1,299.00'."""
    cleaned = re.sub(r"[^\d.,]", "", raw).replace(",", ".")
    parts = cleaned.split(".")
    if len(parts) > 2:
        cleaned = "".join(parts[:-1]) + "." + parts[-1]
    try:
        value = Decimal(cleaned)
        return value if value > 0 else None
    except InvalidOperation:
        return None


# ── Wildberries (Playwright) ──────────────────────────────────────────────────

def _extract_wb_sku(url: str) -> str | None:
    match = re.search(r"/catalog/(\d+)/", url)
    return match.group(1) if match else None


async def _fetch_wb_meta(url: str) -> dict:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        try:
            ctx = await browser.new_context(
                locale="ru-RU",
                user_agent=_HEADERS["User-Agent"],
            )
            page = await ctx.new_page()
            await page.goto(url, wait_until="domcontentloaded", timeout=_BROWSER_TIMEOUT)

            # Wait for price to appear (signals JS has rendered)
            try:
                await page.wait_for_selector(".price-block__final-price, ins.price-block__final-price", timeout=10_000)
            except PlaywrightTimeout:
                pass

            title = await page.evaluate(
                "document.querySelector('h1.product-page__title')?.textContent?.trim() "
                "|| document.querySelector('meta[property=\"og:title\"]')?.content"
            )
            image_url = await page.evaluate(
                "document.querySelector('meta[property=\"og:image\"]')?.content"
            )
            price_text = await page.evaluate(
                """
                (() => {
                    const el = document.querySelector('ins.price-block__final-price')
                              || document.querySelector('.price-block__final-price');
                    return el?.textContent?.trim() ?? null;
                })()
                """
            )

            return {
                "title": title or None,
                "price": _clean_price(price_text) if price_text else None,
                "image_url": image_url or None,
            }
        finally:
            await browser.close()


# ── Ozon (Playwright) ─────────────────────────────────────────────────────────

async def _fetch_ozon_meta(url: str) -> dict:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        try:
            ctx = await browser.new_context(
                locale="ru-RU",
                user_agent=_HEADERS["User-Agent"],
            )
            page = await ctx.new_page()
            await page.goto(url, wait_until="domcontentloaded", timeout=_BROWSER_TIMEOUT)

            # Wait for the main product heading to appear
            try:
                await page.wait_for_selector("h1", timeout=10_000)
            except PlaywrightTimeout:
                pass

            title = await page.evaluate(
                "document.querySelector('meta[property=\"og:title\"]')?.content "
                "|| document.querySelector('h1')?.textContent?.trim()"
            )
            image_url = await page.evaluate(
                "document.querySelector('meta[property=\"og:image\"]')?.content"
            )
            price_text = await page.evaluate(
                """
                (() => {
                    // Ozon renders prices in spans inside the price widget
                    const candidates = [
                        document.querySelector('[data-widget=\"webPrice\"] span'),
                        document.querySelector('.price-number'),
                        document.querySelector('meta[property=\"product:price:amount\"]'),
                    ];
                    for (const el of candidates) {
                        if (!el) continue;
                        const val = el.tagName === 'META' ? el.content : el.textContent;
                        if (val) return val.trim();
                    }
                    return null;
                })()
                """
            )

            return {
                "title": title or None,
                "price": _clean_price(price_text) if price_text else None,
                "image_url": image_url or None,
            }
        finally:
            await browser.close()


# ── Generic HTML scraping (httpx + BeautifulSoup) ────────────────────────────

def _extract_price(soup: BeautifulSoup) -> Decimal | None:
    for prop in ("product:price:amount", "og:price:amount"):
        tag = soup.find("meta", property=prop)
        if tag and tag.get("content"):
            p = _clean_price(tag["content"])
            if p:
                return p

    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "")
            items = data if isinstance(data, list) else [data]
            for item in items:
                offers = item.get("offers") or item.get("Offers")
                if isinstance(offers, dict):
                    price = offers.get("price") or offers.get("lowPrice")
                    if price:
                        p = _clean_price(str(price))
                        if p:
                            return p
                elif isinstance(offers, list) and offers:
                    price = offers[0].get("price")
                    if price:
                        p = _clean_price(str(price))
                        if p:
                            return p
        except (json.JSONDecodeError, AttributeError):
            continue

    for name in ("price", "twitter:data1"):
        tag = soup.find("meta", attrs={"name": name})
        if tag and tag.get("content"):
            p = _clean_price(tag["content"])
            if p:
                return p

    return None


def _extract_image(soup: BeautifulSoup) -> str | None:
    for prop in ("og:image", "og:image:url", "twitter:image"):
        tag = soup.find("meta", property=prop) or soup.find("meta", attrs={"name": prop})
        if tag and tag.get("content"):
            return tag["content"]
    return None


def _extract_title(soup: BeautifulSoup) -> str | None:
    tag = soup.find("meta", property="og:title")
    if tag and tag.get("content"):
        return tag["content"].strip()
    if soup.title and soup.title.string:
        return soup.title.string.strip()
    return None


async def _fetch_generic_meta(url: str) -> dict:
    async with httpx.AsyncClient(headers=_HEADERS, timeout=_TIMEOUT, follow_redirects=True) as client:
        response = await client.get(url)
        response.raise_for_status()
    soup = BeautifulSoup(response.text, "lxml")
    return {
        "title": _extract_title(soup),
        "price": _extract_price(soup),
        "image_url": _extract_image(soup),
    }


# ── Public entry point ────────────────────────────────────────────────────────

async def fetch_url_meta(url: str) -> dict:
    """Fetch a product URL and return {title, price, image_url}."""
    hostname = urlparse(url).hostname or ""

    if _PLAYWRIGHT_AVAILABLE:
        if "wildberries.ru" in hostname or "wb.ru" in hostname:
            return await _fetch_wb_meta(url)
        if "ozon.ru" in hostname:
            return await _fetch_ozon_meta(url)

    return await _fetch_generic_meta(url)
