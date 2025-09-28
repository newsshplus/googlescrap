# details.py
import requests
from bs4 import BeautifulSoup

def fetch_details(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    details = {}

    try:
        details["title"] = soup.title.string
    except:
        details["title"] = None

    try:
        details["meta_description"] = soup.find("meta", {"name":"description"})["content"]
    except:
        details["meta_description"] = None

    try:
        details["h1"] = [h.get_text() for h in soup.find_all("h1")]
    except:
        details["h1"] = None

    return details
