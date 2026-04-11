from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import os
import re

app = Flask(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# 🔥 função principal
def get_fii_data(ticker):
    ticker = ticker.upper()

    result = {
        "ticker": ticker,
        "vacancia": "N/D",
        "inadimplencia": "N/D",
        "portfolio": []
    }

    try:
        url = f"https://www.fundsexplorer.com.br/funds/{ticker.lower()}"
        r = requests.get(url, headers=HEADERS, timeout=10)

        # fallback caso bloqueie
        if r.status_code != 200:
            return result

        soup = BeautifulSoup(r.text, "html.parser")
        text = soup.get_text(" ", strip=True)

        # =========================
        # VACÂNCIA (mais robusto)
        # =========================
        vacancia_patterns = [
            r"Vac[âa]ncia[^0-9]*([0-9,.]+)%",
            r"Vacancy[^0-9]*([0-9,.]+)%"
        ]

        for pattern in vacancia_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result["vacancia"] = match.group(1)
                break

        # =========================
        # INADIMPLÊNCIA
        # =========================
        inad_patterns = [
            r"Inadimpl[êe]ncia[^0-9]*([0-9,.]+)%",
            r"Default[^0-9]*([0-9,.]+)%"
        ]

        for pattern in inad_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result["inadimplencia"] = match.group(1)
                break

        # =========================
        # PORTFÓLIO (ativos reais)
        # =========================
        ativos = re.findall(r"\b[A-Z]{4}\d{2}\b", r.text)
        ativos_unicos = list(set(ativos))

        # remove o próprio ticker
        ativos_unicos = [a for a in ativos_unicos if a != ticker]

        result["portfolio"] = ativos_unicos[:10]

        return result

    except Exception as e:
        result["erro"] = str(e)
        return result


# 🔥 rota raiz
@app.route("/")
def home():
    return jsonify({
        "status": "API FII rodando 🚀",
        "endpoint": "/fii/<ticker>"
    })


# 🔥 rota principal
@app.route("/fii/<ticker>")
def fii(ticker):
    data = get_fii_data(ticker)
    return jsonify(data)


# 🔥 RAILWAY / PRODUÇÃO
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
