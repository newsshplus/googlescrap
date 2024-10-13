# HOW TO EXECUTE:
As we know how difficult it is to scrap data from google shopping due to its dynamic website changes,captcha and cookies 

I found a way to scrap data from google shopping using Selenium undetected browser adding checks for captcha and cookies 

1. The main.py file is for listing the products realted to the keyword you may add the keyword in the *keywords.txt* file as many as u want comma separated 
2. Keeping in mind i added check for location as well u can fix it according to your need 
3. The *imagedownloader.py* file is for downloading the product related images by clicking on them first gathering the image links and downloads them in their respective dimensions
4.The *details.py* file is for downloading data for scpecific product u can provide productURL and it will download the data in csv format or any that u require 

# Libraries:
1. To install the libraries 

    *pip install -r requirements.txt*
