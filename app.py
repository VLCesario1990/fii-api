import requests
from bs4 import BeautifulSoup
import re

def testar_fii(ticker):
    url = f"https://www.fundsexplorer.com.br/funds/{ticker.lower()}"
    response = requests.get(url)

    print(f"\n🔎 TESTANDO: {ticker}")
    print("Status:", response.status_code)

    soup = BeautifulSoup(response.text, "html.parser")
    text = soup.get_text(" ", strip=True)

    print("\n📄 INICIO DO HTML:")
    print(text[:500])

    vacancia = re.search(r"Vac[âa]ncia[^0-9]*([0-9,]+)%", text)
    inad = re.search(r"Inadimpl[êe]ncia[^0-9]*([0-9,]+)%", text)

    print("\n📊 RESULTADO:")
    print("Vacância:", vacancia.group(1) if vacancia else "N/D")
    print("Inadimplência:", inad.group(1) if inad else "N/D")


# 👇 TESTA AQUI
testar_fii("xpml11")
