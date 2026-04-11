from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import os
import re
import time

app = Flask(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# =========================
# 🔒 REQUEST SEGURO
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
            return None

        soup = BeautifulSoup(html, "html.parser")

        vacancia = "N/D"
        inad = "N/D"

        # 🔥 busca spans com %
        spans = soup.find_all("span")

        for span in spans:
            texto = span.get_text(strip=True)

            if "%" in texto:
                parent = span.find_parent()
                if not parent:
                    continue

                contexto = parent.get_text(" ", strip=True).lower()

                if "vac" in contexto and vacancia == "N/D":
                    vacancia = texto.replace("%", "")

                elif "inad" in contexto and inad == "N/D":
                    inad = texto.replace("%", "")

        # 🔥 PORTFÓLIO (FIIs dentro do fundo)
        ativos = list(set(re.findall(r"[A-Z]{4}\d{2}", html)))

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

    except Exception as e:
        print(f"Erro MeusDividendos: {e}")
        return None


# =========================
# 🥈 FUNDSEXPLORER (fallback)
# =========================
def get_fundsexplorer(ticker):
    try:
        url = f"https://www.fundsexplorer.com.br/funds/{ticker.lower()}"

        html = safe_request(url)
        if not html:
            return None

        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text()

        # VACÂNCIA
        vacancia_match = re.search(
            r"Vac[âa]ncia.*?([0-9]+,[0-9]+|[0-9]+)%",
            text,
            re.DOTALL
        )
        vacancia = vacancia_match.group(1) if vacancia_match else "N/D"

        # INADIMPLÊNCIA
        inad_match = re.search(
            r"Inadimpl[êe]ncia.*?([0-9]+,[0-9]+|[0-9]+)%",
            text,
            re.DOTALL
        )
        inad = inad_match.group(1) if inad_match else "N/D"

        # PORTFÓLIO
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
# 🔥 FUNÇÃO PRINCIPAL
# =========================
def get_fii_data(ticker):

    # 🥇 tenta MeusDividendos primeiro
    data = get_meusdividendos(ticker)

    if data:
        print(f"✔ {ticker} veio do MEUSDIVIDENDOS")
        return data  # 🔥 PARA AQUI

    # 🥈 fallback
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


# =========================
# 🌐 ROTAS
# =========================
@app.route("/")
def home():
    return jsonify({"status": "API FII rodando 🚀"})


@app.route("/fii/<ticker>")
def fii(ticker):
    return jsonify(get_fii_data(ticker))


# =========================
# 🚀 RAILWAY
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
