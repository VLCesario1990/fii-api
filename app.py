import requests
from bs4 import BeautifulSoup
import json
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def get_meusdividendos(ticker):
    try:
        ticker_base = ticker.replace("11", "").lower()
        url = f"https://www.meusdividendos.com/fundo-imobiliario/{ticker_base}"

        response = requests.get(url, headers=HEADERS, timeout=10)

        print("🔎 URL:", url)
        print("Status:", response.status_code)
        print("📄 HTML (inicio):")
        print(response.text[:300])

        if response.status_code != 200:
            return {"erro": "Erro ao acessar site"}

        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text(" ", strip=True)

        # VACÂNCIA
        vacancia = "N/D"
        match = re.search(r"Vac[âa]ncia Financeira\s*([0-9]+,[0-9]+|[0-9]+)%", text)
        if match:
            vacancia = match.group(1)

        # INADIMPLÊNCIA
        inad = "N/D"
        match = re.search(r"Inadimpl[êe]ncia\s*([0-9]+,[0-9]+|[0-9]+)%", text)
        if match:
            inad = match.group(1)

        # PORTFÓLIO
        portfolio = list(set(re.findall(r"[A-Z]{4}\d{2}", response.text)))

        return {
            "ticker": ticker.upper(),
            "vacancia": vacancia,
            "inadimplencia": inad,
            "portfolio": portfolio[:10]
        }

    except Exception as e:
        return {"erro": str(e)}


# TESTE
if __name__ == "__main__":
    ticker = "xpml11"

    print("🚀 TESTANDO:", ticker)

    resultado = get_meusdividendos(ticker)

    print("📊 RESULTADO:")
    print(json.dumps(resultado, indent=2, ensure_ascii=False))
