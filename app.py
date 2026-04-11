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
# FUNÇÃO PRINCIPAL
# ==============================
def get_fii_data(ticker):
    try:
        ticker = ticker.lower()
        url = f"https://www.fundsexplorer.com.br/funds/{ticker}"

        r = requests.get(url, headers=HEADERS, timeout=10)

        # 🚨 Se bloqueado
        if r.status_code != 200:
            return {
                "ticker": ticker.upper(),
                "vacancia": "N/D",
                "inadimplencia": "N/D",
                "portfolio": [],
                "erro": f"HTTP {r.status_code}"
            }

        soup = BeautifulSoup(r.text, "html.parser")
        text = soup.get_text(separator=" ")

        # 🚨 Página inválida
        if len(text) < 200:
            return {
                "ticker": ticker.upper(),
                "vacancia": "N/D",
                "inadimplencia": "N/D",
                "portfolio": [],
                "erro": "Conteúdo inválido"
            }

        # ==============================
        # VACÂNCIA
        # ==============================
        vacancia_match = re.search(r"Vac[âa]ncia[^0-9]*([0-9,.]+)%", text)
        vacancia = vacancia_match.group(1) if vacancia_match else "N/D"

        # ==============================
        # INADIMPLÊNCIA
        # ==============================
        inad_match = re.search(r"Inadimpl[êe]ncia[^0-9]*([0-9,.]+)%", text)
        inad = inad_match.group(1) if inad_match else "N/D"

        # ==============================
        # PORTFÓLIO
        # ==============================
        ativos = re.findall(r"[A-Z]{4}\d{2}", r.text)
        ativos = list(set(ativos))

        return {
            "ticker": ticker.upper(),
            "vacancia": vacancia,
            "inadimplencia": inad,
            "portfolio": ativos[:5]
        }

    except Exception as e:
        return {
            "ticker": ticker.upper(),
            "vacancia": "N/D",
            "inadimplencia": "N/D",
            "portfolio": [],
            "erro": str(e)
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
# RUN LOCAL (não usado no Railway)
# ==============================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
