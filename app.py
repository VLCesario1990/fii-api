from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import os
import re
import time

app = Flask(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def safe_request(url):
    try:
        time.sleep(1)
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            return r.text
        return None
    except:
        return None


# 🥇 MEUSDIVIDENDOS (PRIORIDADE)
def get_meusdividendos(ticker):
    try:
        ticker_base = ticker.replace("11", "")
        url = f"https://www.meusdividendos.com/fundo-imobiliario/{ticker_base}"

        html = safe_request(url)
        if not html:
            return None

        ativos = list(set(re.findall(r"[A-Z]{4}\d{2}", html)))

        vacancia_match = re.search(r"Vac[âa]ncia[^0-9]*([0-9,.]+)%", html)
        vacancia = vacancia_match.group(1) if vacancia_match else "N/D"

        inad_match = re.search(r"Inadimpl[êe]ncia[^0-9]*([0-9,.]+)%", html)
        inad = inad_match.group(1) if inad_match else "N/D"

        # 🚨 REGRA IMPORTANTE
        encontrou_algo = (
            len(ativos) > 0 or
            vacancia != "N/D" or
            inad != "N/D"
        )

        if encontrou_algo:
            return {
                "ticker": ticker.upper(),
                "vacancia": vacancia,
                "inadimplencia": inad,
                "portfolio": ativos[:10],
                "fonte": "meusdividendos"
            }

        return None

    except:
        return None


# 🥈 FUNDSEXPLORER (FALLBACK)
def get_fundsexplorer(ticker):
    try:
        url = f"https://www.fundsexplorer.com.br/funds/{ticker.lower()}"

        html = safe_request(url)
        if not html:
            return None

        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text()

        vacancia_match = re.search(r"Vac[âa]ncia[^0-9]*([0-9,.]+)%", text)
        vacancia = vacancia_match.group(1) if vacancia_match else "N/D"

        inad_match = re.search(r"Inadimpl[êe]ncia[^0-9]*([0-9,.]+)%", text)
        inad = inad_match.group(1) if inad_match else "N/D"

        ativos = list(set(re.findall(r"[A-Z]{4}\d{2}", html)))

        return {
            "ticker": ticker.upper(),
            "vacancia": vacancia,
            "inadimplencia": inad,
            "portfolio": ativos[:10],
            "fonte": "fundsexplorer"
        }

    except:
        return None


# 🔥 FUNÇÃO PRINCIPAL (COM STOP INTELIGENTE)
def get_fii_data(ticker):

    # 🥇 tenta primeiro
    data = get_meusdividendos(ticker)

    if data:
        print(f"✔ {ticker} veio do MEUSDIVIDENDOS")
        return data  # 🔥 PARA AQUI

    # 🥈 só entra aqui se NÃO encontrou nada
    data = get_fundsexplorer(ticker)

    if data:
        print(f"✔ {ticker} veio do FUNDSEXPLORER")
        return data

    # ❌ nada encontrado
    return {
        "ticker": ticker.upper(),
        "vacancia": "N/D",
        "inadimplencia": "N/D",
        "portfolio": [],
        "erro": "Nenhuma fonte respondeu"
    }


# 🌐 ROTAS
@app.route("/")
def home():
    return jsonify({"status": "API FII rodando 🚀"})


@app.route("/fii/<ticker>")
def fii(ticker):
    return jsonify(get_fii_data(ticker))


# 🚀 RAILWAY
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
