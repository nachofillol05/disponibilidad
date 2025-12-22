import requests
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime, timedelta

URL = "https://www.temporadalivre.com/es/aluguel-temporada/brasil/rio-de-janeiro/arraial-do-cabo/prainha/143886-azotea-con-barbacoa-vista-al-mar-a-30-metros-de-la-playa-plaza-de-parking"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

res = requests.get(URL, headers=HEADERS, timeout=20)
res.raise_for_status()

soup = BeautifulSoup(res.text, "html.parser")

today = datetime.today()
limit_date = today + timedelta(days=365)

disponibles = []

for day in soup.select("#calendars-container td.day"):
    classes = day.get("class", [])

    # Saltar no disponibles
    if "unavailable" in classes:
        continue

    title = day.get("title", "")

    if "Disponible" not in title:
        continue

    fecha_match = re.search(r"(\d{2}/\d{2}/\d{4})", title)
    precio_match = re.search(r"R\$ (\d+)", title)

    if not fecha_match:
        continue

    fecha_dt = datetime.strptime(fecha_match.group(1), "%d/%m/%Y")

    # Filtrar solo próximos 12 meses
    if not (today <= fecha_dt <= limit_date):
        continue

    disponibles.append({
        "date": fecha_dt.strftime("%Y-%m-%d"),
        "price": int(precio_match.group(1)) if precio_match else None
    })

# Ordenar por fecha
disponibles.sort(key=lambda x: x["date"])

with open("availability.json", "w", encoding="utf-8") as f:
    json.dump(disponibles, f, indent=2, ensure_ascii=False)

print(f"✔ availability.json actualizado ({len(disponibles)} días disponibles)")
