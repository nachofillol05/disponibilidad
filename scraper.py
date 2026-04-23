import requests
import json
import time
import random
from datetime import datetime
from bs4 import BeautifulSoup

BASE = "https://www.temporadalivre.com/es/properties/143886-cobertura-com-churrasqueira-vista-ao-mar-30-metros-prainha-vaga-carro"

HEADERS = {
    "User-Agent": random.choice([
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/17.0 Safari/605.1.15"
    ]),
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    "Referer": BASE
}

MESES = {
    "ene": 1, "feb": 2, "mar": 3, "abr": 4,
    "may": 5, "jun": 6, "jul": 7, "ago": 8,
    "sep": 9, "oct": 10, "nov": 11, "dic": 12
}

session = requests.Session()
session.headers.update(HEADERS)


def get_month(date):
    url = f"{BASE}/calendar?date={date}"
    r = session.get(url, timeout=20)
    r.raise_for_status()
    return r.text


def parse_unavailable(html, year):
    unavailable = []

    soup = BeautifulSoup(html, "html.parser")
    days = soup.find_all("td", class_="day")

    for day_cell in days:
        date_span = day_cell.find("span", class_="date")
        price_span = day_cell.find("span", class_="price")

        if not date_span or not price_span:
            continue

        # ejemplo: "13 jun"
        date_text = date_span.text.strip()
        parts = date_text.split()

        if len(parts) != 2:
            continue

        day, mes = parts
        mes_num = MESES.get(mes.lower())

        if not mes_num:
            continue

        # ejemplo: "--" o "R$ 275"
        price_text = price_span.text.strip()

        # 🔥 clave: "--" = ocupado
        if price_text == "--":
            fecha = datetime(year, mes_num, int(day)).strftime("%Y-%m-%d")
            unavailable.append(fecha)

    return unavailable


def generate_months(months_ahead=18):
    today = datetime.today()
    months = []

    for i in range(months_ahead):
        month = (today.month + i - 1) % 12 + 1
        year = today.year + (today.month + i - 1) // 12
        months.append(f"{year}-{month:02d}-01")

    return months


def human_delay():
    time.sleep(random.uniform(0.8, 2.0))


# 🔥 MAIN
months = generate_months(18)

all_unavailable = []

for m in months:
    print(f"→ Scrapeando {m}")

    html = get_month(m)
    year = int(m[:4])

    all_unavailable.extend(parse_unavailable(html, year))

    human_delay()


# limpiar duplicados
all_unavailable = sorted(set(all_unavailable))

with open("availability.json", "w", encoding="utf-8") as f:
    json.dump(all_unavailable, f, indent=2)

print(f"✔ availability.json generado ({len(all_unavailable)} fechas ocupadas)")
