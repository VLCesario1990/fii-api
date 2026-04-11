from flask import Flask, jsonify
import os
import re
import asyncio
from playwright.async_api import async_playwright

app = Flask(__name__)

# =========================
# FUNDSEXPLORER (JS + DATA VIEW)
# =========================
async def get_fundsexplorer_data(ticker):
    try:
        url = f"https://www.fundsexplorer.com.br/funds/{ticker.lower()}"

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            await page.goto(url, timeout=60000)

            # ⏳ espera carregar
            await page.wait_for_timeout(5000)

            # 🔥 TENTA ABRIR DATA VIEW (se existir botão)
            try:
                await page.click("text=Data View", timeout=3000)
                await page.wait_for_timeout(2000)
            except:
                pass

            content = await page.content()
            await browser.close()

        text = re.sub(r"\s+", " ", content)

        # =========================
        # VACÂNCIA FINANCEIRA (último valor da tabela)
        # =========================
        matches = re.findall(
            r"Vac[âa]ncia Financeira[^0-9]*([0-9]+\.?[0-9]*)",
            text
        )

        if matches:
            vacancia = matches[-1]  # último mês
        else:
            vacancia = "N/D"

        # =========================
        # INADIMPLÊNCIA
        # =========================
        inad_match = re.search(
            r"Inadimpl[êe]ncia[^0-9]*([0-9]+,[0-9]+|[0-9]+)%",
            text
        )

        inadimplencia = inad_match.group(1) if inad_match else "N/D"

        # =========================
        # PORTFÓLIO
        # =========================
        ativos = list(set(re.findall(r"[A-Z]{4}\d{2}", content)))

        return {
            "ticker": ticker.upper(),
            "vacancia": vacancia,
            "inadimplencia": inadimplencia,
            "portfolio": ativos[:10],
            "fonte": "fundsexplorer_data_view"
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
    return jsonify({"status": "API FII (Data View real) 🚀"})


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
