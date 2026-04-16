import requests
from bs4 import BeautifulSoup
import re

url = "https://www.meusdividendos.com/fundo-imobiliario/tepp"

response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

rows = soup.find_all("tr")

print("🔎 RESULTADO:\n")

for row in rows:
    cols = row.find_all("td")

    if len(cols) >= 6:
        nome = cols[0].text.strip()
        vac = cols[3].text.strip()
        inad = cols[4].text.strip()

        print(nome, "| Vac:", vac, "| Inad:", inad)
