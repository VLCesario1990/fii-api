import asyncio
import json
import re
import os
from playwright.async_api import async_playwright

TICKERS = ["xpml11", "mxrf11", "tepp11"]

async def get_data(ticker):
    try:
        ticker_base = ticker.replace("11", "")
        url = f"https://www.meusdividendos.com/fundo-imobiliario/{ticker_base}"

        print("\n============================")
        print("🔎 TICKER:", ticker)
        print("🌐 URL:", url)

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            await page.goto(url, timeout=60000)
            await page.wait_for_timeout(6000)

            content = await page.content()
            await browser.close()

        # 🔥 DEBUG HTML
        print("\n📄 HTML (inicio):")
        print(content[:500])

        # 🔥 TEXTO LIMPO
        text = re.sub(r"\s+", " ", content)

        print("\n🧠 TEXTO LIMPO (inicio):")
        print(text[:500])

        # 🔍 TESTES DE EXISTÊNCIA
        print("\n🔍 CHECKS:")
        print("Tem 'Vacância'? ->", "Vacância" in text)
        print("Tem 'Inadimplência'? ->", "Inadimplência" in text)

        # =========================
        # VACÂNCIA
        # =========================
        vacancia = "N/D"
        v = re.search(
            r"Vac[âa]ncia[^0-9]*([0-9]+,[0-9]+|[0-9]+)%",
            text
        )

        if v:
            vacancia = v.group(1)
            print("✅ Vacância encontrada:", vacancia)
        else:
            print("❌ Vacância NÃO encontrada")

        # =========================
        # INADIMPLÊNCIA
        # =========================
        inad = "N/D"
        i = re.search(
            r"Inadimpl[êe]ncia[^0-9]*([0-9]+,[0-9]+|[0-9]+)%",
            text
        )

        if i:
            inad = i.group(1)
            print("✅ Inadimplência encontrada:", inad)
        else:
            print("❌ Inadimplência NÃO encontrada")

        # =========================
        # PORTFÓLIO
        # =========================
        portfolio = list(set(re.findall(r"[A-Z]{4}\d{2}", content)))

        print("\n📊 Portfolio encontrado:", portfolio[:10])

        return {
            "vacancia": vacancia,
            "inadimplencia": inad,
            "portfolio": portfolio[:10]
        }

    except Exception as e:
        print("❌ ERRO:", str(e))
        return {
            "vacancia": "N/D",
            "inadimplencia": "N/D",
            "portfolio": [],
            "erro": str(e)
        }


async def main():
    result = {}

    for t in TICKERS:
        result[t] = await get_data(t)

    os.makedirs("data", exist_ok=True)

    with open("data/fii.json", "w") as f:
        json.dump(result, f, indent=2)

    print("\n✅ JSON FINAL:")
    print(json.dumps(result, indent=2))


asyncio.run(main())
