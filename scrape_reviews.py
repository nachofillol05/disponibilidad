import requests
from bs4 import BeautifulSoup
import json

BASE_URL = "https://www.temporadalivre.com/es/properties/143886-cobertura-com-churrasqueira-vista-ao-mar-30-metros-prainha-vaga-carro/reviews/load_more"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

all_reviews = []

page = 0

while True:
    print(f"→ Cargando page={page}")

    url = f"{BASE_URL}?page={page}"

    r = requests.get(url, headers=HEADERS, timeout=20)
    r.raise_for_status()

    data = r.json()

    html = data.get("html", "").strip()
    count = data.get("count", 0)

    # Cortar si no hay más
    if count == 0 or not html:
        print("✔ No hay más reviews")
        break

    soup = BeautifulSoup(html, "html.parser")

    for review in soup.select("article.review"):

        name = review.select_one(".reviwer-name")
        date = review.select_one(".date")
        text = review.select_one(".text")
        stars = review.select_one(".stars-container")

        all_reviews.append({
            "name": name.get_text(strip=True) if name else "",
            "date": date.get_text(strip=True) if date else "",
            "text": text.get_text(" ", strip=True) if text else "",
            "stars": stars.get_text(strip=True) if stars else ""
        })

    page += 1


# Guardar JSON
with open("reviews.json", "w", encoding="utf-8") as f:
    json.dump(all_reviews, f, indent=2, ensure_ascii=False)

print(f"✔ reviews.json generado ({len(all_reviews)} reseñas)")
