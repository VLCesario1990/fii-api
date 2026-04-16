import asyncio
import re
import json
from playwright.async_api import async_playwright


async def get_vacancia(ticker):
    url = f"https://www.fundsexplorer.com.br/funds/{ticker.lower()}"

    print("\n==========================")
    print(f"🔎 TICKER: {ticker}")
    print(f"🌐 URL: {url}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        # 🔥 CONTEXTO "HUMANO"
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720}
        )

        page = await context.new_page()

        # 🔥 esconder webdriver
        await page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        """)

        try:
            await page.goto(url, timeout=90000)

            # simular comportamento humano
            await page.mouse.move(500, 900)
            await page.wait_for_timeout(5000)

            # esperar carregar JS
            await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(50000)

            # DEBUG HTML
            html = await page.content()
            print("\n📄 HTML (inicio):")
            print(html[:500])

            # 🔥 pegar TODOS textareas
            textareas = await page.query_selector_all("textarea")

            print(f"\n🧠 Encontrados {len(textareas)} textarea(s)")

            for i, ta in enumerate(textareas):
                content = await ta.input_value()

                print(f"\n📄 TEXTAREA {i}:")
                print(content[:300])

                if "%" in content:
                    linhas = content.strip().split("\n")
                    ultima = linhas[-1]

                    valores = re.findall(r"[0-9]+\.?[0-9]*", ultima)

                    if valores:
                        vacancia = valores[-1]
                        print(f"✅ Vacância encontrada: {vacancia}")

                        await browser.close()
                        return vacancia

            print("❌ Nenhum textarea válido encontrado")
            await browser.close()
            return "N/D"

        except Exception as e:
            print("❌ ERRO:", str(e))
            await browser.close()
            return "N/D"


async def main():
    tickers = ["xpml11", "mxrf11", "tepp11"]

    resultado = {}

    for t in tickers:
        vacancia = await get_vacancia(t)

        resultado[t] = {
            "vacancia": vacancia
        }

    print("\n📊 RESULTADO FINAL:")
    print(json.dumps(resultado, indent=2))

    # 🔥 salvar JSON
    with open("data/fii.json", "w") as f:
        json.dump(resultado, f, indent=2)


if __name__ == "__main__":
    asyncio.run(main())
