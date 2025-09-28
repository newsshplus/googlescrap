# imagedownloader.py
import os
import requests

def download_images(urls, out_dir="downloads/images"):
    os.makedirs(out_dir, exist_ok=True)
    saved_files = []

    for url in urls:
        try:
            response = requests.get(url, stream=True, timeout=10)
            if response.status_code == 200:
                filename = os.path.basename(url.split("?")[0])
                path = os.path.join(out_dir, filename)
                with open(path, "wb") as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                saved_files.append(path)
        except Exception as e:
            print(f"Erro ao baixar {url}: {e}")

    return saved_files
