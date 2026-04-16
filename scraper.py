import asyncio
import json
import os
from playwright.async_api import async_playwright

# 🔥 TICKERS QUE SERÃO COLETADOS
TICKERS = ["xpml11", "mxrf11", "tepp11"]


# =========================
# 🔥 SCRAPER PRINCIPAL
# =========================
async def get_data(ticker):
    try:
        ticker_base = ticker.replace("11", "")
        url = f"https://www.meusdividendos.com/fundo-imobiliario/{ticker_base}"

        print("\n========================")
        print("🔎 TICKER:", ticker)
        print("🌐 URL:", url)

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            await page.goto(url, timeout=60000)
            await page.wait_for_timeout(6000)

            # =========================
            # 🎯 VACÂNCIA (XPATH)
            # =========================
            vacancia = "N/D"
            try:
                vacancia_el = page.locator(
                    "xpath=/html/body/div[2]/div/section[2]/div/div[2]/div[3]/div[2]/div/div[1]/div/div[3]/div/div[1]/div/div/span"
                )
                vacancia_text = await vacancia_el.inner_text()
                vacancia = vacancia_text.replace("%", "").strip()

                print("✅ Vacância:", vacancia)
            except:
                print("❌ Vacância não encontrada")

            # =========================
            # 🎯 INADIMPLÊNCIA (XPATH)
            # =========================
            inad = "N/D"
            try:
                inad_el = page.locator(
                    "xpath=/html/body/div[2]/div/section[2]/div/div[2]/div[3]/div[2]/div/div[1]/div/div[3]/div/div[2]/div/div/span"
                )
                inad_text = await inad_el.inner_text()
                inad = inad_text.replace("%", "").strip()

                print("✅ Inadimplência:", inad)
            except:
                print("❌ Inadimplência não encontrada")

            await browser.close()

        return {
            "vacancia": vacancia,
            "inadimplencia": inad,
            "portfolio": []
        }

    except Exception as e:
        print("❌ ERRO:", str(e))
        return {
            "vacancia": "N/D",
            "inadimplencia": "N/D",
            "portfolio": [],
            "erro": str(e)
        }


# =========================
# 🔥 MAIN
# =========================
async def main():
    result = {}

    for t in TICKERS:
        result[t] = await get_data(t)

    # 🔥 cria pasta se não existir
    os.makedirs("data", exist_ok=True)

    # 🔥 salva JSON
    with open("data/fii.json", "w") as f:
        json.dump(result, f, indent=2)

    print("\n✅ JSON FINAL:")
    print(json.dumps(result, indent=2))


# =========================
# RUN
# =========================
asyncio.run(main())
