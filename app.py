from flask import Flask, jsonify
import os
import asyncio
from playwright.async_api import async_playwright

app = Flask(__name__)

# =========================
# CONFIG
# =========================
HEADLESS = True


# =========================
# SCRAPER MEUSDIVIDENDOS (JS)
# =========================
async def get_fii_data(ticker):
    try:
        ticker_base = ticker.replace("11", "").lower()
        url = f"https://www.meusdividendos.com/fundo-imobiliario/{ticker_base}"

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=HEADLESS)
            page = await browser.new_page()

            await page.goto(url, timeout=60000)

            # ⏳ espera carregar
            await page.wait_for_timeout(5000)

            # =========================
            # VACÂNCIA
            # =========================
            vacancia = "N/D"
            try:
                vacancia = await page.locator(
                    "text=Vacância Financeira"
                ).locator("xpath=../span").inner_text()

                vacancia = vacancia.replace("%", "").strip()
            except:
                pass

            # =========================
            # INADIMPLÊNCIA
            # =========================
            inad = "N/D"
            try:
                inad = await page.locator(
                    "text=Inadimplência"
                ).locator("xpath=../span").inner_text()

                inad = inad.replace("%", "").strip()
            except:
                pass

            # =========================
            # PORTFÓLIO (imóveis)
            # =========================
            ativos = []
            try:
                rows = page.locator("table tbody tr")
                count = await rows.count()

                for i in range(min(count, 10)):
                    nome = await rows.nth(i).locator("td").nth(0).inner_text()
                    ativos.append(nome.strip())
            except:
                pass

            await browser.close()

        return {
            "ticker": ticker.upper(),
            "vacancia": vacancia,
            "inadimplencia": inad,
            "portfolio": ativos,
            "fonte": "meusdividendos_js"
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
    return jsonify({
        "status": "API FII rodando 🚀",
        "uso": "/fii/xpml11"
    })


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
