 # main.py
import pandas as pd
import requests
from bs4 import BeautifulSoup
import urllib.parse
from typing import List, Dict
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def search_products(keywords: str, max_results: int = 20, country: str = "br", language: str = "pt") -> pd.DataFrame:
    """
    Busca produtos no Google Shopping e retorna DataFrame.
    """
    query = urllib.parse.quote(keywords)
    url = f"https://www.google.com/search?tbm=shop&q={query}&hl={language}&gl={country}"

    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")

    results: List[Dict] = []
    items = soup.select("div.sh-dgr__grid-result")[:max_results]

    for item in items:
        title = item.select_one(".Xjkr3b")  # título
        price = item.select_one(".a8Pemb")  # preço
        link = item.select_one("a[href]")   # link
        image = item.select_one("img")      # imagem
        results.append({
            "title": title.text if title else None,
            "price": price.text if price else None,
            "store": None,
            "product_url": link["href"] if link else None,
            "image_url": image["src"] if image else None,
            "source": "Google Shopping",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        })
    df = pd.DataFrame(results)
    return df
