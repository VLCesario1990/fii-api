import asyncio
import json
import os
from playwright.async_api import async_playwright

TICKERS = ["xpml11", "mxrf11", "tepp11", "xpml11"]


# =========================
# 🔥 SCRAPER COM DEBUG
# =========================
async def get_data(ticker):
    try:
        ticker_base = ticker.replace("11", "").lower()
        url = f"https://www.meusdividendos.com/fundo-imobiliario/{ticker_base}"

        print("\n============================")
        print(f"🔎 TICKER: {ticker}")
        print(f"🌐 URL: {url}")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            print("⏳ Acessando página...")
            await page.goto(url, timeout=60000)

            # espera JS carregar
            await page.wait_for_timeout(6000)

            html = await page.content()
            print(f"📄 HTML carregado ({len(html)} chars)")

            # =========================
            # DEBUG TEXTO
            # =========================
            if "Vacância" in html:
                print("✅ Encontrou 'Vacância'")
            else:
                print("❌ NÃO encontrou 'Vacância'")

            # =========================
            # PEGAR TODOS %
            # =========================
            elementos = await page.locator("span.converter-percentual").all_inner_texts()
            print("📊 Percentuais encontrados:", elementos)

            # =========================
            # VACÂNCIA
            # =========================
            vacancia = "N/D"
            if len(elementos) > 0:
                vacancia = elementos[0].replace("%", "").strip()

            # =========================
            # INADIMPLÊNCIA
            # =========================
            inad = "N/D"
            if len(elementos) > 1:
                inad = elementos[1].replace("%", "").strip()

            print("✅ Vacância:", vacancia)
            print("✅ Inadimplência:", inad)

            await browser.close()

        return {
            "vacancia": vacancia,
            "inadimplencia": inad,
            "portfolio": []
        }

    except Exception as e:
        print("💥 ERRO:", str(e))
        return {
            "vacancia": "N/D",
            "inadimplencia": "N/D",
            "portfolio": [],
            "erro": str(e)
        }


# =========================
# MAIN
# =========================
async def main():
    result = {}

    for t in TICKERS:
        result[t] = await get_data(t)

    # cria pasta
    os.makedirs("data", exist_ok=True)

    # salva json
    with open("data/fii.json", "w") as f:
        json.dump(result, f, indent=2)

    print("\n✅ JSON FINAL:")
    print(json.dumps(result, indent=2))


asyncio.run(main())
