from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import os
import re

app = Flask(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# =========================
# FUNDSEXPLORER (SEM JS)
# =========================
def get_fundsexplorer_data(ticker):
    try:
        url = f"https://www.fundsexplorer.com.br/funds/{ticker.lower()}"

        response = requests.get(url, headers=HEADERS, timeout=10)

        if response.status_code != 200:
            return {"erro": "Erro ao acessar site"}

        html = response.text

        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(" ", strip=True)

        # =========================
        # VACÂNCIA
        # =========================
        vacancia_match = re.search(
            r"Vac[âa]ncia[^0-9]*([0-9]+,[0-9]+|[0-9]+)%",
            text
        )

        vacancia = vacancia_match.group(1) if vacancia_match else "N/D"

        # =========================
        # INADIMPLÊNCIA
        # =========================
        inad_match = re.search(
            r"Inadimpl[êe]ncia[^0-9]*([0-9]+,[0-9]+|[0-9]+)%",
            text
        )

        inadimplencia = inad_match.group(1) if inad_match else "N/D"

        # =========================
        # PORTFÓLIO
        # =========================
        ativos = list(set(re.findall(r"[A-Z]{4}\d{2}", html)))

        return {
            "ticker": ticker.upper(),
            "vacancia": vacancia,
            "inadimplencia": inadimplencia,
            "portfolio": ativos[:10],
            "fonte": "fundsexplorer"
        }

    except Exception as e:
        return {
            "ticker": ticker.upper(),
            "erro": str(e),
            "vacancia": "N/D",
            "inadimplencia": "N/D",
            "portfolio": []
        }


# =========================
# ROTAS
# =========================
@app.route("/")
def home():
    return jsonify({"status": "API FII sem Playwright 🚀"})


@app.route("/fii/<ticker>")
def fii(ticker):
    return jsonify(get_fundsexplorer_data(ticker))


# =========================
# RAILWAY
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
