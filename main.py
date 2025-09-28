# main.py
import time
import pandas as pd
from typing import List, Dict
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Token do Browserless
REMOTE_URL = "https://1RxfKOgd5lGGE5Ref3fee0629762ffc5a7977148d5ae"

def search_products(keywords: str, max_results: int = 20, country: str = "br", language: str = "pt") -> pd.DataFrame:
    results: List[Dict] = []
    query = keywords.replace(" ", "+")
    url = f"https://www.google.com/search?tbm=shop&q={query}&hl={language}&gl={country}"

    # Configurações do Chrome remoto
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Passando capabilities corretamente
    driver = webdriver.Remote(
        command_executor=REMOTE_URL,
        desired_capabilities=options.to_capabilities()
    )

    driver.get(url)
    time.sleep(3)  # espera a página carregar

    items = driver.find_elements("css selector", "div.sh-dgr__grid-result")[:max_results]

    for item in items:
        try:
            title = item.find_element("css selector", ".Xjkr3b").text
        except:
            title = None
        try:
            price = item.find_element("css selector", ".a8Pemb").text
        except:
            price = None
        try:
            link = item.find_element("tag name", "a").get_attribute("href")
        except:
            link = None
        try:
            image = item.find_element("tag name", "img").get_attribute("src")
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

    driver.quit()
    return pd.DataFrame(results)
