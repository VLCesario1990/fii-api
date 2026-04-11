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
# REQUEST
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
# 🥇 MEUSDIVIDENDOS
# =========================
def get_meusdividendos(ticker):
    try:
        ticker_base = ticker.replace("11", "")
        url = f"https://www.meusdividendos.com/fundo-imobiliario/{ticker_base}"

        html = safe_request(url)
        if not html:
            return {}

        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(" ", strip=True)

        # VACÂNCIA
        vacancia_match = re.search(
            r"Vac[âa]ncia Financeira\s*([0-9]+,[0-9]+|[0-9]+)%",
            text
        )

        # INADIMPLÊNCIA
        inad_match = re.search(
            r"Inadimpl[êe]ncia\s*([0-9]+,[0-9]+|[0-9]+)%",
            text
        )

        vacancia = vacancia_match.group(1) if vacancia_match else None
        inad = inad_match.group(1) if inad_match else None

        # PORTFÓLIO
        ativos = list(set(re.findall(r"[A-Z]{4}\d{2}", html)))

        return {
            "vacancia": vacancia,
            "inadimplencia": inad,
            "portfolio": ativos[:10],
            "fonte_md": True
        }

    except Exception as e:
        print("Erro MeusDividendos:", e)
        return {}


# =========================
# 🥈 FUNDSEXPLORER
# =========================
def get_fundsexplorer(ticker):
    try:
        url = f"https://www.fundsexplorer.com.br/funds/{ticker.lower()}"

        html = safe_request(url)
        if not html:
            return {}

        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text()

        # fallback (às vezes funciona)
        vacancia_match = re.search(
            r"Vac[âa]ncia.*?([0-9]+,[0-9]+|[0-9]+)%",
            text,
            re.DOTALL
        )

        inad_match = re.search(
            r"Inadimpl[êe]ncia.*?([0-9]+,[0-9]+|[0-9]+)%",
            text,
            re.DOTALL
        )

        ativos = list(set(re.findall(r"[A-Z]{4}\d{2}", html)))

        return {
            "vacancia_fe": vacancia_match.group(1) if vacancia_match else None,
            "inad_fe": inad_match.group(1) if inad_match else None,
            "portfolio_fe": ativos[:10],
            "fonte_fe": True
        }

    except Exception as e:
        print("Erro FundsExplorer:", e)
        return {}


# =========================
# 🧠 MERGE INTELIGENTE
# =========================
def merge_data(ticker, md, fe):

    return {
        "ticker": ticker.upper(),

        # 🔥 PRIORIDADE: MEUSDIVIDENDOS
        "vacancia": md.get("vacancia") or fe.get("vacancia_fe") or "N/D",
        "inadimplencia": md.get("inadimplencia") or fe.get("inad_fe") or "N/D",

        # 🔥 PORTFÓLIO: junta os dois
        "portfolio": list(set(
            (md.get("portfolio") or []) +
            (fe.get("portfolio_fe") or [])
        ))[:10],

        "fontes": {
            "meusdividendos": md.get("fonte_md", False),
            "fundsexplorer": fe.get("fonte_fe", False)
        }
    }


# =========================
# FUNÇÃO PRINCIPAL
# =========================
def get_fii_data(ticker):

    md = get_meusdividendos(ticker)
    fe = get_fundsexplorer(ticker)

    return merge_data(ticker, md, fe)


# =========================
# ROTAS
# =========================
@app.route("/")
def home():
    return jsonify({"status": "API FII PRO rodando 🚀"})


@app.route("/fii/<ticker>")
def fii(ticker):
    return jsonify(get_fii_data(ticker))


# =========================
# RAILWAY
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
