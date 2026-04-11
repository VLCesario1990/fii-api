from flask import Flask, jsonify
import requests
import os
import re
import json

app = Flask(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# =========================
# 🔥 EXTRAIR JSON DO GRÁFICO
# =========================
def extract_chart_json(html):
    try:
        # procura bloco JS que contém os dados
        match = re.search(r"var\s+chartData\s*=\s*(\{.*?\});", html, re.DOTALL)

        if not match:
            return None

        json_str = match.group(1)

        # limpa possíveis erros de JS -> JSON
        json_str = json_str.replace("'", '"')

        return json.loads(json_str)

    except:
        return None


# =========================
# 🔥 PEGAR VACÂNCIA REAL (DATA VIEW)
# =========================
def get_vacancia_from_json(chart_json):
    try:
        # geralmente fica dentro de datasets
        datasets = chart_json.get("datasets", [])

        vacancia_financeira = None

        for ds in datasets:
            label = ds.get("label", "").lower()

            if "vacância financeira" in label:
                data = ds.get("data", [])

                if data:
                    # pega último valor (mais recente)
                    vacancia_financeira = data[-1]
                    break

        return str(vacancia_financeira) if vacancia_financeira is not None else "N/D"

    except:
        return "N/D"


# =========================
# 🔥 FUNÇÃO PRINCIPAL
# =========================
def get_fundsexplorer_data(ticker):
    try:
        url = f"https://www.fundsexplorer.com.br/funds/{ticker.lower()}"

        response = requests.get(url, headers=HEADERS, timeout=10)

        if response.status_code != 200:
            return {"erro": "Erro ao acessar site"}

        html = response.text

        # =========================
        # 🎯 VACÂNCIA VIA JSON
        # =========================
        chart_json = extract_chart_json(html)
        vacancia = get_vacancia_from_json(chart_json) if chart_json else "N/D"

        # =========================
        # 📊 INADIMPLÊNCIA (fallback regex)
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
            "fonte": "fundsexplorer_json"
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
    return jsonify({"status": "API FII (JSON REAL) 🚀"})


@app.route("/fii/<ticker>")
def fii(ticker):
    return jsonify(get_fundsexplorer_data(ticker))


# =========================
# RAILWAY
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
