from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import os
import re
import asyncio
from playwright.async_api import async_playwright

app = Flask(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# =========================
# REQUEST SIMPLES
# =========================
def safe_request(url):
    try:
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

        vacancia_match = re.search(
            r"Vac[âa]ncia Financeira\s*([0-9]+,[0-9]+|[0-9]+)%",
            text
        )

        inad_match = re.search(
            r"Inadimpl[êe]ncia\s*([0-9]+,[0-9]+|[0-9]+)%",
            text
        )

        return {
            "vacancia_md": vacancia_match.group(1) if vacancia_match else None,
            "inadimplencia": inad_match.group(1) if inad_match else None
        }

    except:
        return {}


# =========================
# 🥈 FUNDSEXPLORER (COM JS)
# =========================
async def get_fundsexplorer_js(ticker):
    try:
        url = f"https://www.fundsexplorer.com.br/funds/{ticker.lower()}"

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            await page.goto(url, timeout=60000)

            # 🔥 espera página carregar
            await page.wait_for_timeout(5000)

            content = await page.content()
            await browser.close()

        soup = BeautifulSoup(content, "html.parser")
        text = soup.get_text(" ", strip=True)

        # 🔥 VACÂNCIA DO GRÁFICO
        vacancia_match = re.search(
            r"Vac[âa]ncia[^0-9]*([0-9]+,[0-9]+|[0-9]+)%",
            text
        )

        vacancia = vacancia_match.group(1) if vacancia_match else None

        return {
            "vacancia": vacancia
        }

    except Exception as e:
        print("Erro JS:", e)
        return {}


# =========================
# MERGE
# =========================
async def get_fii_data(ticker):

    md = get_meusdividendos(ticker)
    fe = await get_fundsexplorer_js(ticker)

    return {
        "ticker": ticker.upper(),

        # 🔥 prioridade FUNDSEXPLORER
        "vacancia": fe.get("vacancia") or md.get("vacancia_md") or "N/D",

        # 🔥 prioridade MEUSDIVIDENDOS
        "inadimplencia": md.get("inadimplencia") or "N/D"
    }


# =========================
# ROTAS
# =========================
@app.route("/")
def home():
    return jsonify({"status": "API FII JS rodando 🚀"})


@app.route("/fii/<ticker>")
def fii(ticker):
    data = asyncio.run(get_fii_data(ticker))
    return jsonify(data)


# =========================
# RAILWAY
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
