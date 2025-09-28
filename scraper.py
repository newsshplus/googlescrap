from playwright.sync_api import sync_playwright
import pandas as pd

def search_products(keywords, max_results=10, country="us", language="en"):
    """
    Busca produtos no Google Shopping usando Playwright
    """
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        query = keywords.replace(" ", "+")
        url = f"https://www.google.com/search?tbm=shop&q={query}&hl={language}&gl={country}"
        page.goto(url)

        # Seleciona os produtos
        product_cards = page.query_selector_all("div.sh-dgr__grid-result")
        for card in product_cards[:max_results]:
            title_el = card.query_selector("h4")
            price_el = card.query_selector(".a8Pemb")
            link_el = card.query_selector("a.shntl")
            img_el = card.query_selector("img")

            title = title_el.inner_text() if title_el else ""
            price = price_el.inner_text() if price_el else ""
            link = link_el.get_attribute("href") if link_el else ""
            image = img_el.get_attribute("src") if img_el else ""

            results.append({
                "Título": title,
                "Preço": price,
                "Link": link,
                "Imagem": image
            })

        browser.close()

    return pd.DataFrame(results)
