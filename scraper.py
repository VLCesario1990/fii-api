import requests
from bs4 import BeautifulSoup
import json
import os
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}


def get_data(ticker):
    ticker_clean = ticker.replace("11", "").lower()
    url = f"https://www.meusdividendos.com/fundo-imobiliario/{ticker_clean}"

    print("\n==========================")
    print(f"🔎 TICKER: {ticker}")
    print(f"🌐 URL: {url}")

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)

        print(f"📡 Status: {response.status_code}")

        if response.status_code != 200:
            return {
                "vacancia": "N/D",
                "inadimplencia": "N/D",
                "portfolio": []
            }

        soup = BeautifulSoup(response.text, "html.parser")

        # =========================
        # VACÂNCIA
        # =========================
        vacancia = "N/D"
        spans = soup.select("span.converter-percentual")

        print(f"🧠 spans encontrados: {len(spans)}")

        for s in spans:
            texto = s.get_text(strip=True)
            print(f"➡️ span: {texto}")

            if "%" in texto:
                vacancia = texto.replace("%", "").strip()
                break

        # =========================
        # PORTFÓLIO
        # =========================
        portfolio = []

        linhas = soup.select("table tr")

        for l in linhas:
            tds = l.find_all("td")
            if len(tds) >= 2:
                nome = tds[0].get_text(strip=True)
                if nome:
                    portfolio.append(nome)

        print(f"🏢 Portfolio encontrados: {len(portfolio)}")

        return {
            "vacancia": vacancia,
            "inadimplencia": "N/D",
            "portfolio": portfolio[:10]
        }

    except Exception as e:
        print("❌ ERRO:", str(e))
        return {
            "vacancia": "N/D",
            "inadimplencia": "N/D",
            "portfolio": []
        }


def main():
    tickers = ["xpml11", "mxrf11", "tepp11"]

    resultado = {}

    for t in tickers:
        resultado[t] = get_data(t)

    print("\n📊 RESULTADO FINAL:")
    print(json.dumps(resultado, indent=2))

    # 🔥 GARANTE PASTA
    os.makedirs("data", exist_ok=True)

    # 🔥 SALVA JSON
    with open("data/fii.json", "w") as f:
        json.dump(resultado, f, indent=2)

    print("✅ JSON salvo com sucesso")


if __name__ == "__main__":
    main()
