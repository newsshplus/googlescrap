# details.py
import requests
from bs4 import BeautifulSoup
from typing import Dict

def fetch_details(product_url: str) -> Dict:
    """Busca detalhes básicos do produto."""
    details = {}
    try:
        r = requests.get(product_url, timeout=5)
        soup = BeautifulSoup(r.text, "html.parser")
        title = soup.select_one("title")
        details["title"] = title.text if title else None
    except Exception as e:
        details["error"] = str(e)
    return details
