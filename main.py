# main.py
import time
import pandas as pd
from typing import List, Dict
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# URL remoto do Browserless com sua key
REMOTE_URL = "https://chrome.browserless.io?token=1RxfKOgd5lGGE5Ref3fee0629762ffc5a7977148d5ae98dae"

def search_products(keywords: str, max_results: int = 50, country: str = "br", language: str = "pt") -> pd.DataFrame:
    """
    Busca produtos no Google Shopping usando Selenium via Browserless remoto.
    Retorna um DataFrame com título, preço, loja, avaliação, link, imagem, fonte e timestamp.
    """
    results: List[Dict] = []
    query = keywords.replace(" ", "+")
    url = f"https://www.google.com/search?tbm=shop&q={query}&hl={language}&gl={country}"

    # Configurações do Chrome headless
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    # Cria driver remoto via Browserless
    driver = webdriver.Remote(
        command_executor=REMOTE_URL,
        options=options
    )

    driver.get(url)
    time.sleep(3)  # espera a página carregar

    # Paginação simples: rolar até carregar resultados suficientes
    scroll_pause = 2
    total_items = 0
    while total_items < max_results:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause)
        total_items = len(driver.find_elements(By.CSS_SELECTOR, "div.sh-dgr__grid-result"))
        if total_items >= max_results:
            break

    items = driver.find_elements(By.CSS_SELECTOR, "div.sh-dgr__grid-result")[:max_results]

    for item in items:
        try:
            title = item.find_element(By.CSS_SELECTOR, ".Xjkr3b").text
        except:
            title = None
        try:
            price = item.find_element(By.CSS_SELECTOR, ".a8Pemb").text
        except:
            price = None
        try:
            link = item.find_element(By.TAG_NAME, "a").get_attribute("href")
        except:
            link = None
        try:
            image = item.find_element(By.TAG_NAME, "img").get_attribute("src")
        except:
            image = None
        try:
            store = item.find_element(By.CSS_SELECTOR, ".aULzUe").text
        except:
            store = None
        try:
            rating = item.find_element(By.CSS_SELECTOR, ".Rsc7Yb").text
        except:
            rating = None

        results.append({
            "title": title,
            "price": price,
            "store": store,
            "rating": rating,
            "product_url": link,
            "image_url": image,
            "source": "Google Shopping",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        })

    driver.quit()
    return pd.DataFrame(results)
