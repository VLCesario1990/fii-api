from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import os
import re

app = Flask(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def get_fii_data(ticker):
    try:
        url = f"https://www.fundsexplorer.com.br/funds/{ticker.lower()}"
        r = requests.get(url, headers=HEADERS, timeout=10)

        if r.status_code != 200:
            return {"erro": f"HTTP {r.status_code}"}

        soup = BeautifulSoup(r.text, "html.parser")
        text = soup.get_text()

        # VACÂNCIA
        vacancia_match = re.search(r"Vac[âa]ncia[^0-9]*([0-9,.]+)%", text)
        vacancia = vacancia_match.group(1) if vacancia_match else "N/D"

        # INADIMPLÊNCIA
        inad_match = re.search(r"Inadimpl[êe]ncia[^0-9]*([0-9,.]+)%", text)
        inad = inad_match.group(1) if inad_match else "N/D"

        # PORTFÓLIO (tickers encontrados)
        ativos = re.findall(r"[A-Z]{4}\d{2}", r.text)
        ativos = list(set(ativos))

        return {
            "ticker": ticker.upper(),
            "vacancia": vacancia,
            "inadimplencia": inad,
            "portfolio": ativos[:5]
        }

    except Exception as e:
        return {"erro": str(e)}

@app.route("/")
def home():
    return "API FII rodando 🚀"

@app.route("/fii/<ticker>")
def fii(ticker):
    return jsonify(get_fii_data(ticker))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
