# main.py
import time
import pandas as pd
from typing import List, Dict
from playwright.sync_api import sync_playwright

def search_products(keywords: str, max_results: int = 20, country: str = "br", language: str = "pt") -> pd.DataFrame:
    """
    Busca produtos no Google Shopping usando Playwright headless (Python 3.13 compatível online).
    Não requer ChromeDriver.
    """
    results: List[Dict] = []
    query = keywords.replace(" ", "+")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        url = f"https://www.google.com/search?tbm=shop&q={query}&hl={language}&gl={country}"
        page.goto(url)
        page.wait_for_timeout(3000)  # espera a página carregar

        # Seleciona os produtos
        items = page.query_selector_all("div.sh-dgr__grid-result")[:max_results]

        for item in items:
            try:
                title_elem = item.query_selector(".Xjkr3b")
                title = title_elem.inner_text() if title_elem else None
            except:
                title = None
            try:
                price_elem = item.query_selector(".a8Pemb")
                price = price_elem.inner_text() if price_elem else None
            except:
                price = None
            try:
                link_elem = item.query_selector("a")
                link = link_elem.get_attribute("href") if link_elem else None
            except:
                link = None
            try:
                img_elem = item.query_selector("img")
                image = img_elem.get_attribute("src") if img_elem else None
            except:
                image = None

            results.append({
                "title": title,
                "price": price,
                "store": None,
                "product_url": link,
                "image_url": image,
                "source": "Google Shopping",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            })

        browser.close()
    return pd.DataFrame(results)
