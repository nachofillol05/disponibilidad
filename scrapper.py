import requests
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime

URL = "https://www.temporadalivre.com/es/aluguel-temporada/brasil/rio-de-janeiro/arraial-do-cabo/prainha/143886-azotea-con-barbacoa-vista-al-mar-a-30-metros-de-la-playa-plaza-de-parking"

HEADERS = {"User-Agent": "Mozilla/5.0"}

res = requests.get(URL, headers=HEADERS, timeout=20)
soup = BeautifulSoup(res.text, "html.parser")

disponibles = []

for day in soup.select("#calendars-container td.day"):
    if "unavailable" in day.get("class", []):
        continue

    title = day.get("title", "")
    if "Disponible" not in title:
        continue

    fecha_match = re.search(r"(\d{2}/\d{2}/\d{4})", title)
    precio_match = re.search(r"R\$ (\d+)", title)

    if not fecha_match:
        continue

    fecha = datetime.strptime(
        fecha_match.group(1),
        "%d/%m/%Y"
    ).strftime("%Y-%m-%d")

    disponibles.append({
        "date": fecha,
        "price": int(precio_match.group(1)) if precio_match else None
    })

with open("availability.json", "w", encoding="utf-8") as f:
    json.dump(disponibles, f, indent=2, ensure_ascii=False)

print("✔ availability.json actualizado")
