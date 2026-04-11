from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import os
import re

app = Flask(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# ==============================
# FUNÇÃO PRINCIPAL (COM FALLBACK)
# ==============================
def get_fii_data(ticker):
    ticker = ticker.lower()

    fontes = [
        f"https://www.fundsexplorer.com.br/funds/{ticker}",
        f"https://investidor10.com.br/fiis/{ticker}"
    ]

    for url in fontes:
        try:
            r = requests.get(url, headers=HEADERS, timeout=10)

            if r.status_code != 200:
                continue

            soup = BeautifulSoup(r.text, "html.parser")
            text = soup.get_text(separator=" ")

            # 🚨 página inválida
            if len(text) < 200:
                continue

            # ==============================
            # VACÂNCIA
            # ==============================
            vacancia_match = re.search(r"Vac[âa]ncia[^0-9]*([0-9,.]+)%", text)
            vacancia = vacancia_match.group(1) if vacancia_match else None

            # ==============================
            # INADIMPLÊNCIA
            # ==============================
            inad_match = re.search(r"Inadimpl[êe]ncia[^0-9]*([0-9,.]+)%", text)
            inad = inad_match.group(1) if inad_match else None

            # ==============================
            # PORTFÓLIO
            # ==============================
            ativos = re.findall(r"[A-Z]{4}\d{2}", r.text)
            ativos = list(set(ativos))

            # se encontrou algo útil → retorna
            if vacancia or inad or ativos:
                return {
                    "ticker": ticker.upper(),
                    "vacancia": vacancia or "N/D",
                    "inadimplencia": inad or "N/D",
                    "portfolio": ativos[:5]
                }

        except Exception as e:
            continue

    # ==============================
    # FALLBACK TOTAL
    # ==============================
    return {
        "ticker": ticker.upper(),
        "vacancia": "N/D",
        "inadimplencia": "N/D",
        "portfolio": []
    }

# ==============================
# ROTAS
# ==============================

@app.route("/")
def home():
    return jsonify({
        "status": "API FII rodando 🚀",
        "endpoint": "/fii/<ticker>"
    })

@app.route("/fii/<ticker>")
def fii(ticker):
    return jsonify(get_fii_data(ticker))

# ==============================
# RUN LOCAL (debug)
# ==============================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
