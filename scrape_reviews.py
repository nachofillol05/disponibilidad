import requests
from bs4 import BeautifulSoup
import json

URL = "https://www.temporadalivre.com/es/properties/143886-cobertura-com-churrasqueira-vista-ao-mar-30-metros-prainha-vaga-carro"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

print("→ Descargando página...")

r = requests.get(URL, headers=HEADERS, timeout=30)
r.raise_for_status()

soup = BeautifulSoup(r.text, "html.parser")

reviews_section = soup.find("section", {"data-behavior": "reviews-show-app"})

if not reviews_section:
    raise Exception("No se encontraron reviews")

reviews = []

articles = reviews_section.find_all("article", class_="review")

for art in articles:

    name = art.select_one(".reviwer-name")
    date = art.select_one(".date")
    text = art.select_one(".text")
    stars = art.select_one(".stars-container")

    review = {
        "name": name.text.strip() if name else "",
        "date": date.text.strip() if date else "",
        "text": text.get_text(" ", strip=True) if text else "",
        "stars": len(stars.text.strip()) if stars else 5
    }

    reviews.append(review)


with open("reviews.json", "w", encoding="utf-8") as f:
    json.dump(reviews, f, ensure_ascii=False, indent=2)


print(f"✔ reviews.json generado ({len(reviews)} reseñas)")
