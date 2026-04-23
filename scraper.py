import requests
import re
import json
import time
import random
from datetime import datetime

BASE = "https://www.temporadalivre.com/es/properties/143886-cobertura-com-churrasqueira-vista-ao-mar-30-metros-prainha-vaga-carro"

# headers más realistas
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


def get_month(date, retries=3):
    url = f"{BASE}/calendar?date={date}"

    for i in range(retries):
        try:
            r = session.get(url, timeout=20)
            r.raise_for_status()
            return r.text

        except requests.RequestException:
            if i == retries - 1:
                raise
            time.sleep(2 + random.random())

    return ""


def parse_unavailable(html, year):
    unavailable = []

    matches = re.findall(r"(\d{1,2})\s*(\w{3})Indisp\.", html)

    for day, mes in matches:
        mes_num = MESES.get(mes.lower())
        if not mes_num:
            continue

        fecha = datetime(year, mes_num, int(day)).strftime("%Y-%m-%d")
        unavailable.append(fecha)

    return unavailable


def generate_months(months_ahead=18):
    today = datetime.today()
    months = []

    year = today.year
    month = today.month

    for i in range(months_ahead):
        m = (month + i - 1) % 12 + 1
        y = year + (month + i - 1) // 12
        months.append(f"{y}-{m:02d}-01")

    return months


def human_delay():
    # delay variable tipo humano
    time.sleep(random.uniform(0.8, 2.2))


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
