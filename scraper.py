from bs4 import BeautifulSoup
import json

html = open("page.html").read()
soup = BeautifulSoup(html, "html.parser")

data_div = soup.find("div", {"data-behavior": "property-details-data"})

unavailable_raw = data_div["data-unavailable-dates"]
unavailable_dates = json.loads(unavailable_raw)

print(len(unavailable_dates))
print(unavailable_dates[:5])
