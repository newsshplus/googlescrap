import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import undetected_chromedriver as uc


def perform_exit_sequence(message, driver):
    print(message)
    driver.quit()

# Create a function to download images
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

# Define the main function
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
    

# Example usage

def image_finder():
    driver = uc.Chrome(use_subprocess=False, version_main=128)
    driver.implicitly_wait(10)
    wait = WebDriverWait(driver, 20)
    
    try:
        # Step 2: Visit the Google Shopping page
        driver.get("https://www.google.co.uk/shopping/product/13184296575516912801")
        time.sleep(3)
        
        scrape_images('1318429657551691280',wait,driver)
        
    except Exception as e:
        print(f"An error occurred: {e}")
        perform_exit_sequence("An error occurred during the scraping process.", driver)

    finally:
        driver.quit()
    
if __name__ == "__main__":
    image_finder()
    