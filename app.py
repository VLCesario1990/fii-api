from flask import Flask, jsonify
import os
import re
import asyncio
from playwright.async_api import async_playwright

app = Flask(__name__)

# =========================
# FUNDSEXPLORER (JS REAL)
# =========================
async def get_fundsexplorer_data(ticker):
    try:
        url = f"https://www.fundsexplorer.com.br/funds/{ticker.lower()}"

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            await page.goto(url, timeout=60000)

            # ⏳ espera carregar gráfico
            await page.wait_for_timeout(6000)

            content = await page.content()
            await browser.close()

        # 🔥 TEXTO COMPLETO
        text = re.sub(r"\s+", " ", content)

        # =========================
        # VACÂNCIA
        # =========================
        vacancia_match = re.search(
            r"Vac[âa]ncia[^0-9]*([0-9]+,[0-9]+|[0-9]+)%",
            text
        )

        vacancia = vacancia_match.group(1) if vacancia_match else "N/D"

        # =========================
        # INADIMPLÊNCIA
        # =========================
        inad_match = re.search(
            r"Inadimpl[êe]ncia[^0-9]*([0-9]+,[0-9]+|[0-9]+)%",
            text
        )

        inadimplencia = inad_match.group(1) if inad_match else "N/D"

        # =========================
        # PORTFÓLIO (tickers dentro da página)
        # =========================
        ativos = list(set(re.findall(r"[A-Z]{4}\d{2}", content)))

        return {
            "ticker": ticker.upper(),
            "vacancia": vacancia,
            "inadimplencia": inadimplencia,
            "portfolio": ativos[:10],
            "fonte": "fundsexplorer"
        }

    except Exception as e:
        print("Erro:", e)
        return {
            "ticker": ticker.upper(),
            "vacancia": "N/D",
            "inadimplencia": "N/D",
            "portfolio": [],
            "erro": str(e)
        }


# =========================
# ROUTES
# =========================
@app.route("/")
def home():
    return jsonify({"status": "API FII (FundsExplorer JS) 🚀"})


@app.route("/fii/<ticker>")
def fii(ticker):
    data = asyncio.run(get_fundsexplorer_data(ticker))
    return jsonify(data)


# =========================
# RAILWAY
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
