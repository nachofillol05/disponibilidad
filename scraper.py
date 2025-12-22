import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

# ================= CONFIG =================

CALENDAR_URL = "https://www.temporadalivre.com/pt/properties/143886/calendar"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "X-Requested-With": "XMLHttpRequest"
}

# ================= HELPERS =================

def fetch_month(month_iso):
    r = requests.get(
        CALENDAR_URL,
        params={"months[date]": month_iso},
        headers=HEADERS,
        timeout=20
    )
    r.raise_for_status()
    return r.text


def parse_calendar(html):
    soup = BeautifulSoup(html, "html.parser")
    data = []

    for day in soup.select("td.day"):
        if "unavailable" in day.get("class", []):
            continue

        title = day.get("title", "")
        if "Disponible" not in title and "Disponível" not in title:
            continue

        fecha_match = re.search(r"(\d{2}/\d{2}/\d{4})", title)
        precio_match = re.search(r"R\$ (\d+)", title)

        if not fecha_match:
            continue

        data.append({
            "date": datetime.strptime(
                fecha_match.group(1),
                "%d/%m/%Y"
            ).strftime("%Y-%m-%d"),
            "price": int(precio_match.group(1)) if precio_match else None
        })

    return data

# ================= MAIN =================

today = date.today().replace(day=1)
months = [
    (today + relativedelta(months=i)).isoformat()
    for i in range(12)
]

disponibles = []

for month in months:
    print(f"→ cargando {month}")
    html = fetch_month(month)
    disponibles.extend(parse_calendar(html))

# Deduplicar
unique = {d["date"]: d for d in disponibles}
disponibles = list(unique.values())

disponibles.sort(key=lambda x: x["date"])

with open("availability.json", "w", encoding="utf-8") as f:
    json.dump(disponibles, f, indent=2, ensure_ascii=False)

print(f"✔ availability.json actualizado ({len(disponibles)} días disponibles)")
