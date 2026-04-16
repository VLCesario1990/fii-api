import requests
import json
import os
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def get_data(ticker):
    url = f"https://statusinvest.com.br/fundos-imobiliarios/{ticker.lower()}"

    print("\n==========================")
    print(f"🔎 {ticker}")
    print(f"🌐 {url}")

    try:
        r = requests.get(url, headers=HEADERS, timeout=10)

        print("Status:", r.status_code)

        if r.status_code != 200:
            return {"vacancia": "N/D"}

        html = r.text

        vacancia = "N/D"

        # 🔥 REGEX MAIS FORTE
        match = re.search(
            r"Vacância[^0-9]*([0-9]+,[0-9]+|[0-9]+)%",
            html
        )

        if match:
            vacancia = match.group(1)

        print("Vacância:", vacancia)

        return {
            "vacancia": vacancia
        }

    except Exception as e:
        print("Erro:", e)
        return {"vacancia": "N/D"}


def main():
    tickers = ["XPML11", "MXRF11", "TEPP11"]

    resultado = {}

    for t in tickers:
        resultado[t] = get_data(t)

    print("\n📊 RESULTADO FINAL:")
    print(json.dumps(resultado, indent=2))

    # 🔥 RESOLVE SEU ERRO DEFINITIVAMENTE
    os.makedirs("data", exist_ok=True)

    with open("data/fii.json", "w") as f:
        json.dump(resultado, f, indent=2)

    print("✅ JSON salvo com sucesso")


if __name__ == "__main__":
    main()
