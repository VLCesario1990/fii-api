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
# 🔥 PEGAR DATA VIEW REAL
# =========================
def get_vacancia_data_view(soup):
    try:
        # procura tabela que contém "Vacância Financeira"
        tables = soup.find_all("table")

        for table in tables:
            if "Vacância Financeira" in table.text:

                rows = table.find_all("tr")

                # pega última linha (mais recente)
                last_row = rows[-1].find_all("td")

                if len(last_row) >= 4:
                    # coluna 4 = Vacância Financeira
                    valor = last_row[3].text.strip()

                    return valor.replace("%", "").strip()

        return "N/D"

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

        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text(" ", strip=True)

        # =========================
        # 🎯 VACÂNCIA (DATA VIEW)
        # =========================
        vacancia = get_vacancia_data_view(soup)

        # =========================
        # 📊 INADIMPLÊNCIA
        # =========================
        inad_match = re.search(
            r"Inadimpl[êe]ncia[^0-9]*([0-9]+,[0-9]+|[0-9]+)%",
            text
        )

        inadimplencia = inad_match.group(1) if inad_match else "N/D"

        # =========================
        # 🏢 PORTFÓLIO
        # =========================
        ativos = list(set(re.findall(r"[A-Z]{4}\d{2}", response.text)))

        return {
            "ticker": ticker.upper(),
            "vacancia": vacancia,
            "inadimplencia": inadimplencia,
            "portfolio": ativos[:10],
            "fonte": "fundsexplorer_dataview"
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
    return jsonify({"status": "API FII (DATA VIEW REAL) 🚀"})


@app.route("/fii/<ticker>")
def fii(ticker):
    return jsonify(get_fii_data(ticker))


# =========================
# RAILWAY
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
