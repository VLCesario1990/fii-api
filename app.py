from flask import Flask, jsonify
import requests
import os
import re
import json
from bs4 import BeautifulSoup

app = Flask(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# =========================
# 🔥 EXTRAIR JSON NEXT.JS
# =========================
def get_next_data(html):
    try:
        soup = BeautifulSoup(html, "html.parser")

        script = soup.find("script", {"id": "__NEXT_DATA__"})

        if not script:
            return None

        return json.loads(script.string)

    except:
        return None


# =========================
# 🔥 VACÂNCIA REAL (JSON)
# =========================
def extract_vacancia_from_json(data):
    try:
        # navegação genérica (estrutura pode mudar)
        text = json.dumps(data)

        match = re.search(
            r"Vac[âa]ncia Financeira[^0-9]*([0-9]+,[0-9]+|[0-9]+)",
            text
        )

        return match.group(1) if match else "N/D"

    except:
        return "N/D"


# =========================
# 🔥 FUNÇÃO PRINCIPAL
# =========================
def get_fii_data(ticker):
    try:
        url = f"https://www.fundsexplorer.com.br/funds/{ticker.lower()}"

        response = requests.get(url, headers=HEADERS, timeout=10)

        if response.status_code != 200:
            return {"erro": "Erro ao acessar site"}

        html = response.text

        # =========================
        # 🎯 JSON REAL
        # =========================
        next_data = get_next_data(html)

        vacancia = extract_vacancia_from_json(next_data) if next_data else "N/D"

        # =========================
        # 📊 INADIMPLÊNCIA (fallback)
        # =========================
        text = re.sub(r"\s+", " ", html)

        inad_match = re.search(
            r"Inadimpl[êe]ncia[^0-9]*([0-9]+,[0-9]+|[0-9]+)%",
            text
        )

        inadimplencia = inad_match.group(1) if inad_match else "N/D"

        # =========================
        # 🏢 PORTFÓLIO
        # =========================
        ativos = list(set(re.findall(r"[A-Z]{4}\d{2}", html)))

        return {
            "ticker": ticker.upper(),
            "vacancia": vacancia,
            "inadimplencia": inadimplencia,
            "portfolio": ativos[:10],
            "fonte": "fundsexplorer_nextjs"
        }

    except Exception as e:
        return {
            "ticker": ticker.upper(),
            "vacancia": "N/D",
            "inadimplencia": "N/D",
            "portfolio": [],
            "erro": str(e)
        }


# =========================
# ROTAS
# =========================
@app.route("/")
def home():
    return jsonify({"status": "API FII (NEXT DATA) 🚀"})


@app.route("/fii/<ticker>")
def fii(ticker):
    return jsonify(get_fii_data(ticker))


# =========================
# RAILWAY
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
