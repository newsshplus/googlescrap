# main.py
import time
import pandas as pd
from typing import List, Dict
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

def search_products(keywords: str, max_results: int = 20, country: str = "br", language: str = "pt") -> pd.DataFrame:
    """
    Busca produtos no Google Shopping usando undetected-chromedriver.
    Funciona em qualquer ambiente sem instalar ChromeDriver manualmente.
    """
    options = uc.ChromeOptions()
    options.headless = True
    driver = uc.Chrome(options=options)

    query = keywords.replace(" ", "+")
    url = f"https://www.google.com/search?tbm=shop&q={query}&hl={language}&gl={country}"
    driver.get(url)
    time.sleep(3)  # espera carregar

    items = driver.find_elements(By.CSS_SELECTOR, "div.sh-dgr__grid-result")[:max_results]
    results: List[Dict] = []

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
