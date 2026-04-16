import requests
import json
import os

def get_fii_data(ticker):
    ticker = ticker.upper()

    url = f"https://statusinvest.com.br/fundos-imobiliarios/{ticker.lower()}"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    print("\n==========================")
    print(f"🔎 {ticker}")
    print(f"🌐 {url}")

    try:
        r = requests.get(url, headers=headers, timeout=10)

        if r.status_code != 200:
            return {"erro": "Erro ao acessar"}

        html = r.text

        # =========================
        # VACÂNCIA (REGEX ROBUSTO)
        # =========================
        vacancia = "N/D"

        if "Vacância" in html:
            import re
            match = re.search(r"Vacância[^0-9]*([0-9]+,[0-9]+|[0-9]+)%", html)
            if match:
                vacancia = match.group(1)

        return {
            "ticker": ticker,
            "vacancia": vacancia
        }

    except Exception as e:
        return {"erro": str(e)}


def main():
    tickers = ["XPML11", "MXRF11", "TEPP11"]

    resultado = {}

    for t in tickers:
        resultado[t] = get_fii_data(t)

    print("\n📊 RESULTADO FINAL:")
    print(json.dumps(resultado, indent=2))

    os.makedirs("data", exist_ok=True)

    with open("data/fii.json", "w") as f:
        json.dump(resultado, f, indent=2)


if __name__ == "__main__":
    main()
