   # imagedownloader.py
import os
from typing import List
import requests

def download_images(urls: List[str], out_dir: str = "downloads/images") -> List[str]:
    """
    Baixa imagens de URLs e retorna lista de paths.
    """
    os.makedirs(out_dir, exist_ok=True)
    saved_paths = []

    for url in urls:
        try:
            r = requests.get(url, stream=True)
            if r.status_code == 200:
                filename = os.path.join(out_dir, url.split("/")[-1])
                with open(filename, "wb") as f:
                    for chunk in r.iter_content(1024):
                        f.write(chunk)
                saved_paths.append(filename)
        except Exception as e:
            print(f"Erro ao baixar {url}: {e}")
    return saved_paths


if __name__ == "__main__":
    import sys
    urls = sys.argv[1:]
    paths = download_images(urls)
    print(paths)
