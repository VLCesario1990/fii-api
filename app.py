from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import os
import re

app = Flask(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def get_meusdividendos(ticker):
    try:
        ticker_base = ticker.replace("11", "").lower()

        url = f"https://www.meusdividendos.com/fundo-imobiliario/{ticker_base}"
        response = requests.get(url, headers=HEADERS, timeout=10)

        if response.status_code != 200:
            return {"erro": f"HTTP {response.status_code}"}

        soup = BeautifulSoup(response.text, "html.parser")

        # =========================
        # 🏢 PORTFÓLIO (TABELA)
        # =========================
        portfolio = []
        vacancias = []
        inads = []

        rows = soup.find_all("tr")

        for row in rows:
            cols = row.find_all("td")

            if len(cols) >= 6:
                nome = cols[0].get_text(strip=True)
                vac = cols[3].get_text(strip=True)
                inad = cols[4].get_text(strip=True)

                # tenta extrair ticker do nome
                ticker_match = re.search(r"[A-Z]{4}\d{2}", nome)

                if ticker_match:
                    portfolio.append(ticker_match.group(0))

                # guarda vacâncias válidas
                if "%" in vac:
                    vacancias.append(vac.replace("%", "").strip())

                if "%" in inad:
                    inads.append(inad.replace("%", "").strip())

        # =========================
        # 📊 AGREGAÇÃO
        # =========================
        vacancia = vacancias[0] if vacancias else "N/D"
        inadimplencia = inads[0] if inads else "N/D"

        return {
            "ticker": ticker.upper(),
            "vacancia": vacancia,
            "inadimplencia": inadimplencia,
            "portfolio": list(set(portfolio))[:10],
            "fonte": "meusdividendos"
        }

    except Exception as e:
        return {
            "erro": str(e)
        }

# =========================
# ROTAS
# =========================
@app.route("/")
def home():
    return jsonify({
        "status": "API MeusDividendos rodando 🚀",
        "teste": "/fii/tepp11"
    })

@app.route("/fii/<ticker>")
def fii(ticker):
    return jsonify(get_meusdividendos(ticker))

# =========================
# RAILWAY
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
    
