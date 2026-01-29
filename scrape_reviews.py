import requests
from bs4 import BeautifulSoup
import json
import time
from urllib.parse import urljoin

BASE = "https://www.temporadalivre.com"

START_URL = "https://www.temporadalivre.com/es/properties/143886-cobertura-com-churrasqueira-vista-ao-mar-30-metros-prainha-vaga-carro"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

session = requests.Session()
session.headers.update(HEADERS)


def extract_reviews(soup):

    reviews = []

    for r in soup.select("article.review"):

        name = r.select_one(".reviwer-name")
        date = r.select_one(".date")
        text = r.select_one(".text")
        stars = r.select_one(".stars")

        reviews.append({
            "name": name.text.strip() if name else "",
            "date": date.text.strip() if date else "",
            "text": text.text.strip() if text else "",
            "stars": stars["class"][-1] if stars else ""
        })

    return reviews


def main():

    all_reviews = []

    print("➡ Página inicial")

    r = session.get(START_URL, timeout=20)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    all_reviews += extract_reviews(soup)


    while True:

        more = soup.find("a", href=lambda x: x and "reviews/load_more" in x)

        if not more:
            print("✔ No hay más reviews")
            break

        next_url = urljoin(BASE, more["href"])

        print("➡ Cargando:", next_url)

        time.sleep(2)

        r = session.get(next_url, timeout=20)

        if r.status_code != 200:
            break

        soup = BeautifulSoup(r.text, "html.parser")

        reviews = extract_reviews(soup)

        if not reviews:
            break

        all_reviews += reviews


    # eliminar duplicados
    unique = []
    seen = set()

    for r in all_reviews:
        key = (r["name"], r["date"], r["text"][:40])

        if key not in seen:
            seen.add(key)
            unique.append(r)


    with open("reviews.json", "w", encoding="utf-8") as f:
        json.dump(unique, f, indent=2, ensure_ascii=False)


    print(f"✔ Guardadas {len(unique)} reseñas")


if __name__ == "__main__":
    main()
