from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import os
import re

app = Flask(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# =========================================
# 🔥 1. MEUSDIVIDENDOS (PRIORIDADE)
# =========================================
def get_meusdividendos(ticker):
    try:
        url = f"https://www.meusdividendos.com/fundo-imobiliario/{ticker.lower()}"
        r = requests.get(url, headers=HEADERS, timeout=10)

        if r.status_code != 200:
            return None

        soup = BeautifulSoup(r.text, "html.parser")
        text = soup.get_text(" ", strip=True)

        # VACÂNCIA
        vacancia = "N/D"
        vac_match = re.search(r"Vac[âa]ncia[^0-9]*([0-9,.]+)%", text)
        if vac_match:
            vacancia = vac_match.group(1)

        # INADIMPLÊNCIA
        inad = "N/D"
        inad_match = re.search(r"Inadimpl[êe]ncia[^0-9]*([0-9,.]+)%", text)
        if inad_match:
            inad = inad_match.group(1)

        # PORTFÓLIO (FIIs dentro)
        ativos = re.findall(r"\b[A-Z]{4}\d{2}\b", r.text)
        ativos = list(set(ativos))
        ativos = [a for a in ativos if a != ticker.upper()]

        return {
            "vacancia": vacancia,
            "inadimplencia": inad,
            "portfolio": ativos[:10],
            "fonte": "meusdividendos"
        }

    except:
        return None


# =========================================
# 🔥 2. FUNDSEXPLORER (FALLBACK)
# =========================================
def get_fundsexplorer(ticker):
    try:
        url = f"https://www.fundsexplorer.com.br/funds/{ticker.lower()}"
        r = requests.get(url, headers=HEADERS, timeout=10)

        if r.status_code != 200:
            return None

        soup = BeautifulSoup(r.text, "html.parser")
        text = soup.get_text(" ", strip=True)

        vacancia = "N/D"
        inad = "N/D"

        vac_match = re.search(r"Vac[âa]ncia[^0-9]*([0-9,.]+)%", text)
        if vac_match:
            vacancia = vac_match.group(1)

        inad_match = re.search(r"Inadimpl[êe]ncia[^0-9]*([0-9,.]+)%", text)
        if inad_match:
            inad = inad_match.group(1)

        ativos = re.findall(r"\b[A-Z]{4}\d{2}\b", r.text)
        ativos = list(set(ativos))
        ativos = [a for a in ativos if a != ticker.upper()]

        return {
            "vacancia": vacancia,
            "inadimplencia": inad,
            "portfolio": ativos[:10],
            "fonte": "fundsexplorer"
        }

    except:
        return None


# =========================================
# 🔥 3. FUNÇÃO PRINCIPAL (INTELIGENTE)
# =========================================
def get_fii_data(ticker):
    ticker = ticker.upper()

    resultado = {
        "ticker": ticker,
        "vacancia": "N/D",
        "inadimplencia": "N/D",
        "portfolio": [],
        "fonte": "nenhuma"
    }

    # 🔥 1º tentativa → MEUSDIVIDENDOS
    data = get_meusdividendos(ticker)
    if data:
        resultado.update(data)

    # 🔥 fallback → FUNDSEXPLORER
    if resultado["vacancia"] == "N/D" and resultado["inadimplencia"] == "N/D":
        data = get_fundsexplorer(ticker)
        if data:
            resultado.update(data)

    return resultado


# =========================================
# 🔥 ROTAS
# =========================================
@app.route("/")
def home():
    return jsonify({
        "status": "API FII PRO rodando 🚀",
        "uso": "/fii/mxrf11"
    })


@app.route("/fii/<ticker>")
def fii(ticker):
    return jsonify(get_fii_data(ticker))


# =========================================
# 🔥 RAILWAY
# =========================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
