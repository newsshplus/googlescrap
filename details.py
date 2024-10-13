import csv
import urllib.parse
import time
import requests
import os 
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import undetected_chromedriver as uc



def read_urls_from_csv(file_path):
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        return [(row['Scrap_Source_Identifier'], row['URL']) for row in reader]

def extract_buying_options(soup):
    buying_options = soup.find_all("div", class_="TZeISb")
    options = []

    for option in buying_options:
        price_element = option.find("span", class_="g9WBQb")
        price = price_element.get_text(strip=True) if price_element else "N/A"

        seller_element = option.find("a", class_="b5ycib shntl")
        if seller_element:
            seller = seller_element.get_text(strip=True).split('-')[0].strip()  
        else:
            seller = "N/A"

        visit_site_element = seller_element['href'] if seller_element else None
        visit_site = "N/A"
        if visit_site_element:
            clean_url = urllib.parse.urlparse(visit_site_element)
            visit_site = urllib.parse.parse_qs(clean_url.query).get('q', ['N/A'])[0]

        formatted_option = f"Price: {price}\nSeller: {seller}\nVisit: {visit_site}"
        options.append(formatted_option)

    return "\n\n".join(options) if options else "N/A"

def extract_key_features(soup):
    features_list = soup.find("ul", class_="xpDPYb")
    features = []

    if features_list:
        feature_items = features_list.find_all("li", class_="KgL16d")
        for item in feature_items:
            feature_text = item.get_text(strip=True)
            features.append(feature_text)

    return "\n".join(features) if features else "N/A"

def download_image(img_url, folder_path, img_name):
    # Download and save the image
    try:
        response = requests.get(img_url)
        if response.status_code == 200:
            # Save image
            with open(os.path.join(folder_path, img_name), 'wb') as file:
                file.write(response.content)
            print(f"Downloaded {img_name}")
        else:
            print(f"Failed to download {img_name}")
    except Exception as e:
        print(f"Error downloading {img_name}: {e}")

def scrape_images(scrape_source_identifier,wait,driver):

    try:
        # Step 3: Click on the "View all photos" button
        view_all_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[@class='PYKPKd' and @role='button']//span[text()='View all photos']"))
        )
        ActionChains(driver).move_to_element(view_all_button).click().perform()
        print("Clicked on 'View all photos'")

        # Step 4: Locate all images within the div
        images_div = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'TiQ3Vc qVUc9e main-image')]//img")))
        
        # Create a directory for storing images based on the scrape source identifier
        folder_path = f'images/{scrape_source_identifier}'
        os.makedirs(folder_path, exist_ok=True)

        # Step 5: Download each image
        for idx, img in enumerate(images_div):
            img_url = img.get_attribute('src')
            img_name = f'image_{idx + 1}.jpg'
            download_image(img_url, folder_path, img_name)
    
    except Exception as e:
        print(f"An error occurred: {e}")

def extract_product_info(driver, url, scrape_source_identifier, wait):
    driver.get(url)
    time.sleep(2)

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    title_element = soup.find("span", class_="BvQan sh-t__title-pdp sh-t__title translate-content")
    title = title_element.get_text(strip=True) if title_element else "N/A"

    reviews_element = soup.find("span", class_="qIEPib")
    reviews = reviews_element.get_text(strip=True) if reviews_element else "N/A"

    rating_element = soup.find("div", class_="uYNZm")
    rating = rating_element.get_text(strip=True) if rating_element else "N/A"

    product_details_element = soup.find("div", class_="BfIk5d")
    product_details = product_details_element.get_text(strip=True) if product_details_element else "N/A"

    spec_table = soup.find("table", class_="lW5xPd")
    specifications = ""
    if spec_table:
        rows = spec_table.find_all("tr")
        for row in rows:
            columns = row.find_all("td")
            if len(columns) == 2:
                key = columns[0].get_text(strip=True)
                value = columns[1].get_text(strip=True)
                specifications += f"{key}: {value}\n"

    buying_options = extract_buying_options(soup)
    key_features = extract_key_features(soup)

    # Call scrape_images() with correct arguments
    scrape_images(scrape_source_identifier, wait, driver)

    return {
        "Title": title,
        "Reviews": reviews,
        "Rating": rating,
        "Product_details": product_details,
        "Product_specifications": specifications.strip(),
        "Buying_options": buying_options,
        "Key_features": key_features
    }

def save_to_csv(data, file_name='product_info.csv'):
    headers = ['Scrap_Source_Identifier', 'Title', 'Reviews', 'Rating', 'Product_details', 'Product_specifications', 'Buying_options', 'Key_features']

    with open(file_name, mode='w', newline='', encoding='utf-8-sig') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

def perform_exit_sequence(message, driver):
    print(message)
    driver.quit()

def decline_cookies(driver):
    try:
        # Wait for the cookies modal to appear and decline cookies
        wait = WebDriverWait(driver, 10)
        decline_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Decline all')]")))
        decline_button.click()
    except TimeoutException:
        print("No cookies pop-up found.")



def open_product_urls_from_csv(csv_file, driver, wait):
    url_data = read_urls_from_csv(csv_file)

    all_product_data = []

    for scrap_source_id, url in url_data:
        print(f"Scraping URL: {url}")
        product_data = extract_product_info(driver, url)
        if product_data:
            product_data['Scrap_Source_Identifier'] = scrap_source_id
            all_product_data.append(product_data)

    return all_product_data

def perform_google_shopping_flow():
    driver = uc.Chrome(use_subprocess=False, version_main=128)
    driver.implicitly_wait(10)
    wait = WebDriverWait(driver, 20)

    try:
        # Visit the Google Shopping page
        driver.get("https://www.google.com/shopping")
        # while check_for_captcha(driver):
        #     print("Please solve the captcha manually.")
        #     time.sleep(3)

        try:
            accept_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Accept all']]")))
            accept_button.click()
        except TimeoutException:
            print("Cookies acceptance not found.")

        # Read product URLs from the CSV and process them
        csv_file = 'googleshopping_listing.csv'  # Replace with your actual CSV file path
        product_data = open_product_urls_from_csv(csv_file, driver, wait)

        # Save scraped data to CSV
        output_csv = 'googleshopping_product_info.csv'
        save_to_csv(product_data, output_csv)

    except Exception as e:
        print(f"An error occurred: {e}")
        perform_exit_sequence("An error occurred during the scraping process.", driver)

    finally:
        driver.quit()

if __name__ == "__main__":
    perform_google_shopping_flow()
