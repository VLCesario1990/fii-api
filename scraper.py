import asyncio
import json
import re
from playwright.async_api import async_playwright

TICKERS = ["xpml11", "mxrf11", "tepp11"]

async def get_data(ticker):
    ticker_base = ticker.replace("11", "")
    url = f"https://www.meusdividendos.com/fundo-imobiliario/{ticker_base}"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        await page.goto(url, timeout=60000)
        await page.wait_for_timeout(5000)

        content = await page.content()
        await browser.close()

    text = re.sub(r"\s+", " ", content)

    vacancia = "N/D"
    inad = "N/D"

    v = re.search(r"Vac[âa]ncia Financeira[^0-9]*([0-9]+,[0-9]+|[0-9]+)%", text)
    if v:
        vacancia = v.group(1)

    i = re.search(r"Inadimpl[êe]ncia[^0-9]*([0-9]+,[0-9]+|[0-9]+)%", text)
    if i:
        inad = i.group(1)

    portfolio = list(set(re.findall(r"[A-Z]{4}\d{2}", content)))

    return {
        "vacancia": vacancia,
        "inadimplencia": inad,
        "portfolio": portfolio[:10]
    }

async def main():
    result = {}

    for t in TICKERS:
        print("Coletando:", t)
        result[t] = await get_data(t)

    with open("data/fii.json", "w") as f:
        json.dump(result, f, indent=2)

asyncio.run(main())
