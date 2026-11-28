import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import date, timedelta

URL = "https://www.temporadalivre.com/es/properties/143886-cobertura-com-churrasqueira-vista-ao-mar-30-metros-prainha-vaga-carro"
HEADERS = {"User-Agent": "Mozilla/5.0"}

r = requests.get(URL, headers=HEADERS, timeout=20)
r.raise_for_status()
soup = BeautifulSoup(r.text, "html.parser")

# 1. Base: fechas bloqueadas del atributo JSON de TemporadaLivre
data_div = soup.find("div", {"data-behavior": "property-details-data"})
if not data_div:
    raise Exception("No se encontró property-details-data")

unavailable = set(json.loads(data_div["data-unavailable-dates"]))

# 2. Leer celdas visuales con "Indisp." o clase "unavailable"
hoy = date.today()
year, month = hoy.year, hoy.month
cals = [c for c in soup.select(".calendar, .month-calendar, table") if 28 <= len(c.select(".day")) <= 42]

if cals:
    primer_txt = cals[0].select(".day")[0].get_text(" ", strip=True).lower()
    m_first = re.match(r"^(\d{1,2})\b", primer_txt)
    if m_first and int(m_first.group(1)) > 20:
        month += 1
        if month > 12:
            month = 1
            year += 1

for cal in cals:
    days = cal.select(".day")
    started = False
    for cell in days:
        txt = cell.get_text(" ", strip=True).lower()
        m = re.match(r"^(\d{1,2})\b", txt)
        if not m:
            continue
        day = int(m.group(1))

        if not started:
            if day == 1:
                started = True
            else:
                continue
        elif day == 1:
            break

        clases = " ".join(cell.get("class", [])).lower()
        if "unavailable" in clases or "indisp" in txt:
            unavailable.add(date(year, month, day).isoformat())

    if started:
        month += 1
        if month > 12:
            month = 1
            year += 1

# 3. Cerrar huecos de 1 día encerrados entre dos fechas ocupadas (ej. 2026-12-08 y 2027-01-21)
fechas_ordenadas = sorted(date.fromisoformat(d) for d in unavailable)
for i in range(len(fechas_ordenadas) - 1):
    if (fechas_ordenadas[i + 1] - fechas_ordenadas[i]).days == 2:
        dia_intermedio = fechas_ordenadas[i] + timedelta(days=1)
        unavailable.add(dia_intermedio.isoformat())

with open("availability.json", "w", encoding="utf-8") as f:
    json.dump(sorted(unavailable), f, indent=2)

print(f"✔ availability.json generado ({len(unavailable)} fechas ocupadas)")
