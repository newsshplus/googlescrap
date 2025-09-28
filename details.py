# details.py
import requests
from bs4 import BeautifulSoup
from typing import Dict

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def fetch_details(product_url: str) -> Dict:
    """
    Retorna detalhes do produto.
    """
    details = {}
    try:
        resp = requests.get(product_url, headers=HEADERS)
        soup = BeautifulSoup(resp.text, "html.parser")
        title = soup.select_one("title")
        details["title"] = title.text if title else None
        # Exemplo simples: você pode adicionar mais scraping aqui
    except Exception as e:
        details["error"] = str(e)
    return details
