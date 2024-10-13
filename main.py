import os
import csv
import time
from collections import defaultdict
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urlunparse
import undetected_chromedriver as uc
from selenium.common.exceptions import NoSuchElementException, TimeoutException



# Read keywords from the keywords.txt file
def read_keywords_from_file(filename):
    try:
        with open(filename, 'r') as file:
            # Read all lines, split by comma, and flatten them into a single list
            keywords = [keyword.strip() for line in file for keyword in line.split(",") if keyword.strip()]
        return keywords
    except Exception as e:
        print(f"Error reading keywords from file: {e}")
        return []

# Save extracted data to CSV with a duplicate count and keyword column
def save_data_to_csv_with_duplicates(data, filename):
    keys = ["Scrap_Source_Identifier", "Keyword", "Page_number", "URL", "Title", "Rating", "Reviews", "Price", "Store URL", "Delivery_Info", "Compare_Prices", "Duplicate_Count"]
    
    # Check if the file exists to decide the mode (write or append)
    file_exists = os.path.isfile(filename)
    
    try:
        # Open file in append mode if it exists, otherwise create a new file
        with open(filename, mode='a' if file_exists else 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=keys)
            
            # Write header only if the file is being created for the first time
            if not file_exists:
                writer.writeheader()
            
            # Append new data to the CSV file
            writer.writerows(data)
        
        print(f"Data successfully appended to {filename}")
    
    except Exception as e:
        print(f"Error saving data to CSV: {e}")

# Function to count duplicates based on Scrap_Source_Identifier
def count_duplicates(data):
    # Dictionary to store the duplicate count for each product
    duplicate_counter = defaultdict(int)
    
    # Count occurrences of each product based on Scrap_Source_Identifier
    for product in data:
        identifier = product['Scrap_Source_Identifier']
        duplicate_counter[identifier] += 1

    # Add a 'Duplicate_Count' column to each product
    for product in data:
        product['Duplicate_Count'] = duplicate_counter[product['Scrap_Source_Identifier']]
    
    return data

# Function to extract product data from the HTML content
def extract_product_data(soup, page_number, keyword):
    # Find the container for each product
    product_container = soup.find_all("div", class_="sh-dgr__gr-auto sh-dgr__grid-result")
    product_data_list = []

    for product in product_container:
        try:
            # Extract Scrap_Source_Identifier
            url_element = product.find("a", class_="xCpuod")
            url = url_element["href"] if url_element else "N/A"
            parsed_url = urlparse(url)
            path_elements = parsed_url.path.split("/")
            scrap_source_identifier = str(path_elements[3]) if len(path_elements) >= 3 else "N/A"

            # Clean and form the complete URL
            url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, "", "", ""))
            url = "https://www.google.co.uk" + url

            # Extract Title
            title_element = product.find("h3", class_="tAxDx")
            title = title_element.get_text(strip=True) if title_element else "N/A"

            # Extract Price
            price_element = product.find("span", class_="a8Pemb OFFNJ")
            price = price_element.get_text(strip=True) if price_element else "N/A"

            # Extract Store URL
            store_url_element = product.find("div", class_="mnIHsc").find("a")
            store_url = store_url_element["href"] if store_url_element else "N/A"
            store_url = store_url.replace("/url?url=", "")

            # Extract Delivery Info
            delivery_info_element = product.find("div", class_="vEjMR")
            delivery_info = delivery_info_element.get_text(strip=True) if delivery_info_element else "N/A"

            # Extract Compare Prices URL
            compare_prices_element = product.find("a", class_="iXEZD")  # Moved inside the product loop
            compare_prices = compare_prices_element.get_text(strip=True) if compare_prices_element else "N/A"

            # Extract Rating & Reviews (moved within the product loop)
            rating = "N/A"
            reviews = "N/A"
            rating_reviews_element = product.find("div", class_="NzUzee")  # Look for the class inside each product

            if rating_reviews_element:
                # Find the span containing the rating value
                rating_element = rating_reviews_element.find("span", class_="Rsc7Yb")
                if rating_element:
                    rating = rating_element.get_text(strip=True)

                # Find the reviews part
                reviews_element = rating_reviews_element.find("span", class_="QIrs8")
                if reviews_element:
                    text_content = reviews_element.get_text(strip=True)
                    if "out of 5 stars." in text_content:
                        try:
                            rating_part, reviews_part = text_content.split(" out of 5 stars.")
                            rating = rating_part.strip()
                            if "product reviews." in reviews_part:
                                reviews = reviews_part.split(" product reviews.")[0].strip()
                        except ValueError:
                            print(f"Error parsing rating and reviews: {text_content}")
                    else:
                        print(f"Unexpected rating/review format: {text_content}")

            # Append the extracted data to the list
            product_data_list.append({
                "Keyword": keyword,
                "Scrap_Source_Identifier": scrap_source_identifier,
                "URL": url,
                "Title": title,
                "Page_number": page_number,
                "Rating": rating,
                "Reviews": reviews,
                "Price": price,
                "Store URL": store_url,
                "Delivery_Info": delivery_info,
                "Compare_Prices": compare_prices
            })
        except Exception as e:
            print(f"Error extracting product data: {e}")

    return product_data_list


# Function to check location from the page source (Google Shopping location specific)
def check_location(soup) -> bool:
    try:
        location_span = soup.find("span", class_="ubXuae")
        if location_span:
            location = location_span.text.strip()
            if location == "United Kingdom" or "England, UK":
                return True
            else:
                print(f"Location mismatch: {location}")
                return False
        else:
            print("Location information not found.")
            return False
    except Exception as e:
        print(f"Error checking location: {e}")
        return False

# Function to handle exit sequence with message and driver quit
def perform_exit_sequence(msg: str, driver: uc.Chrome, exit_code: int = -1):
    print(msg)
    try:
        if driver:
            driver.quit()
    except Exception as e:
        print(f"Error during driver quit: {e}")
    exit(exit_code)

def save_page_source(keyword, page_number, page_source):
    folder_name = "pagesources"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)  # Create directory if it doesn't exist
    
    # Format the filename as pagesource_{keyword}_{page_number}.html
    filename = os.path.join(folder_name, f"pagesource_{keyword}_{page_number}.html")
    
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(page_source)
        print(f"Page source for {keyword} (Page {page_number}) saved as {filename}")
    except Exception as e:
        print(f"Error saving page source for {keyword} (Page {page_number}): {e}")

def perform_google_shopping_flow(keyword):
    driver = uc.Chrome(use_subprocess=False, version_main=128)
    driver.implicitly_wait(10)
    wait = WebDriverWait(driver, 20)

    try:
        # Visit the target URL
        driver.get("https://shopping.google.co.uk/")
        time.sleep(5)

        # Accept cookies if the button is available
        try:
            accept_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Accept all']]")))
            accept_button.click()
        except TimeoutException:
            print("Cookies acceptance not found.")

        # Enter the search keyword
        print(f"Scraping for keyword: {keyword}")
        search_box = wait.until(EC.presence_of_element_located((By.ID, "REsRA")))
        search_box.send_keys(keyword)
        print(f"Entered '{keyword}' and initiated search.")
        search_box.send_keys(Keys.ENTER)
        

        total_pages = 0

        # Loop to scrape data from each page until the "Next" button is unavailable
        while True:
            time.sleep(5)
            total_pages += 1  # Increment the page count
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            # Check if location matches the desired region (United Kingdom)
            if not check_location(soup):
                perform_exit_sequence("Location mismatch.", driver)
            
            save_page_source(keyword, total_pages, driver.page_source)

            # Extract product data, pass keyword for each product
            product_data = extract_product_data(soup, total_pages, keyword)
            
            # For each product in the product_data list, process and save it immediately
            for product in product_data:
                product_list = [product]  

                
                product_list = count_duplicates(product_list)

                # Check if the product has 'N/A' Scrap_Source_Identifier and save accordingly
                if product['Scrap_Source_Identifier'] == "N/A":
                    save_data_to_csv_with_duplicates(product_list, "googleshopping_na_listing.csv")
                    # print(f"Entry with 'N/A' Scrap_Source_Identifier saved.")
                else:
                    save_data_to_csv_with_duplicates(product_list, "googleshopping_listing.csv")
                    # print(f"Product data saved for keyword '{keyword}'.")

            # Check for the "Next" button and navigate to the next page
            try:
                next_button = driver.find_element(By.ID, "pnnext")
                next_button.click()
                print(f"Moving to page {total_pages + 1}")
            except NoSuchElementException:
                print("No more pages to scrape.")
                break

        print(f"Scraping completed for keyword '{keyword}'. Total pages scraped: {total_pages}")

    except Exception as e:
        print(f"An error occurred: {e}")
        perform_exit_sequence(f"Error during the scraping process for keyword '{keyword}'.", driver)

    finally:
        driver.quit()

if __name__ == "__main__":
    # Read keywords from file
    keywords = read_keywords_from_file("google_shopping/keywords.txt")

    # Perform scraping for each keyword
    for keyword in keywords:
        
        perform_google_shopping_flow(keyword)
