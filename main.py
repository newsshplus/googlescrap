from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time
import requests
import os

# Endpoint Browserless + Token
REMOTE_URL = "https://chrome.browserless.io/webdriver?token=1RxfKOgd5lGGE5Ref3fee0629762ffc5a7977148d5ae98dae"

def search_products(keywords, max_results=10, country="us", language="en"):
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Remote(
        command_executor=REMOTE_URL,
        options=options
    )

    try:
        query = "+".join(keywords.split())
        url = f"https://www.google.com/search?tbm=shop&q={query}&hl={language}&gl={country}"
        driver.get(url)
        time.sleep(3)

        items = driver.find_elements("css selector", "div.sh-dgr__grid-result")
        results = []

        for item in items[:max_results]:
            title_elem = item.find_elements("css selector", "h4")
            price_elem = item.find_elements("css selector", ".a8Pemb")
            link_elem = item.find_elements("css selector", "a")
            img_elem = item.find_elements("css selector", "img")

            title = title_elem[0].text if title_elem else ""
            price = price_elem[0].text if price_elem else ""
            link = link_elem[0].get_attribute("href") if link_elem else ""
            image = img_elem[0].get_attribute("src") if img_elem else None

            results.append({
                "Título": title,
                "Preço": price,
                "Link": link,
                "Imagem": image
            })

        df = pd.DataFrame(results)
        return df

    finally:
        driver.quit()

def download_images(df, folder="images"):
    if not os.path.exists(folder):
        os.makedirs(folder)
    for idx, row in df.iterrows():
        url = row.get("Imagem")
        if url:
            try:
                r = requests.get(url)
                filename = os.path.join(folder, f"{idx}.jpg")
                with open(filename, "wb") as f:
                    f.write(r.content)
            except:
                pass
