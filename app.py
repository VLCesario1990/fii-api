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

# =========================
# REQUEST SEGURO
# =========================
def safe_request(url):
    try:
        time.sleep(1)
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            return r.text
        return None
    except:
        return None


# =========================
# 🥇 MEUSDIVIDENDOS (CORRIGIDO)
# =========================
def get_meusdividendos(ticker):
    try:
        ticker_base = ticker.replace("11", "")
        url = f"https://www.meusdividendos.com/fundo-imobiliario/{ticker_base}"

        html = safe_request(url)
        if not html:
            return None

        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(" ", strip=True)

        # 🔥 EXTRAÇÃO CORRETA
        vacancia_match = re.search(
            r"Vac[âa]ncia Financeira\s*([0-9]+,[0-9]+|[0-9]+)%",
            text
        )

        inad_match = re.search(
            r"Inadimpl[êe]ncia\s*([0-9]+,[0-9]+|[0-9]+)%",
            text
        )

        vacancia = vacancia_match.group(1) if vacancia_match else "N/D"
        inad = inad_match.group(1) if inad_match else "N/D"

        # 🔥 PORTFÓLIO
        ativos = list(set(re.findall(r"[A-Z]{4}\d{2}", html)))

        if vacancia != "N/D" or inad != "N/D" or len(ativos) > 0:
            return {
                "ticker": ticker.upper(),
                "Vacância Financeira": vacancia,
                "Inadimplência": inad,
                "portfolio": ativos[:10],
                "fonte": "meusdividendos"
            }

        return None

    except Exception as e:
        print(f"Erro MeusDividendos: {e}")
        return None


# =========================
# 🥈 FUNDSEXPLORER
# =========================
def get_fundsexplorer(ticker):
    try:
        url = f"https://www.fundsexplorer.com.br/funds/{ticker.lower()}"

        html = safe_request(url)
        if not html:
            return None

        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text()

        vacancia_match = re.search(
            r"Vac[âa]ncia.*?([0-9]+,[0-9]+|[0-9]+)%",
            text,
            re.DOTALL
        )
        vacancia = vacancia_match.group(1) if vacancia_match else "N/D"

        inad_match = re.search(
            r"Inadimpl[êe]ncia.*?([0-9]+,[0-9]+|[0-9]+)%",
            text,
            re.DOTALL
        )
        inad = inad_match.group(1) if inad_match else "N/D"

        ativos = list(set(re.findall(r"[A-Z]{4}\d{2}", html)))

        return {
            "ticker": ticker.upper(),
            "vacancia": vacancia,
            "inadimplencia": inad,
            "portfolio": ativos[:10],
            "fonte": "fundsexplorer"
        }

    except Exception as e:
        print(f"Erro FundsExplorer: {e}")
        return None


# =========================
# FUNÇÃO PRINCIPAL
# =========================
def get_fii_data(ticker):

    # 🥇 PRIORIDADE
    data = get_meusdividendos(ticker)
    if data:
        print(f"✔ {ticker} → MEUSDIVIDENDOS")
        return data

    # 🥈 FALLBACK
    data = get_fundsexplorer(ticker)
    if data:
        print(f"✔ {ticker} → FUNDSEXPLORER")
        return data

    return {
        "ticker": ticker.upper(),
        "vacancia": "N/D",
        "inadimplencia": "N/D",
        "portfolio": [],
        "erro": "Nenhuma fonte respondeu"
    }


# =========================
# ROTAS
# =========================
@app.route("/")
def home():
    return jsonify({"status": "API FII rodando 🚀"})


@app.route("/fii/<ticker>")
def fii(ticker):
    return jsonify(get_fii_data(ticker))


# =========================
# RAILWAY
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
    
