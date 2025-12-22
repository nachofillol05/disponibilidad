import requests
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime

URL = "https://www.temporadalivre.com/es/properties/143886-cobertura-com-churrasqueira-vista-ao-mar-30-metros-prainha-vaga-carro"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

r = requests.get(URL, headers=HEADERS, timeout=20)
r.raise_for_status()

soup = BeautifulSoup(r.text, "html.parser")

disponibles = []

for day in soup.select("#calendars-container td.day"):
    classes = day.get("class", [])

    # saltar no disponibles
    if "unavailable" in classes or "disabled" in classes:
        continue

    title = day.get("title", "")
    if "Disponible" not in title:
        continue

    fecha_match = re.search(r"(\d{2}/\d{2}/\d{4})", title)
    precio_match = re.search(r"R\$ (\d+)", title)

    if not fecha_match or not precio_match:
        continue

    fecha = datetime.strptime(
        fecha_match.group(1), "%d/%m/%Y"
    ).strftime("%Y-%m-%d")

    disponibles.append({
        "date": fecha,
        "price": int(precio_match.group(1))
    })

# ordenar
disponibles.sort(key=lambda x: x["date"])

with open("availability.json", "w", encoding="utf-8") as f:
    json.dump(disponibles, f, indent=2, ensure_ascii=False)

print(f"✔ availability.json actualizado ({len(disponibles)} días disponibles)")
