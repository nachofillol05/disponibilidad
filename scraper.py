import requests
from bs4 import BeautifulSoup
import json

URL = "https://www.temporadalivre.com/es/properties/143886-cobertura-com-churrasqueira-vista-ao-mar-30-metros-prainha-vaga-carro"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

r = requests.get(URL, headers=HEADERS, timeout=20)
r.raise_for_status()

soup = BeautifulSoup(r.text, "html.parser")

data_div = soup.find("div", {"data-behavior": "property-details-data"})
if not data_div:
    raise Exception("No se encontró property-details-data")

unavailable = json.loads(data_div["data-unavailable-dates"])

with open("availability.json", "w", encoding="utf-8") as f:
    json.dump(sorted(unavailable), f, indent=2)

print(f"✔ availability.json generado ({len(unavailable)} fechas ocupadas)")
