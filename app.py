def get_fii_data(ticker):
    ticker = ticker.lower()

    url = f"https://www.fundsexplorer.com.br/funds/{ticker}"

    try:
        r = requests.get(url, headers=HEADERS, timeout=10)

        if r.status_code != 200:
            return fallback(ticker, f"HTTP {r.status_code}")

        html = r.text

        # 🔥 TENTA PEGAR JSON INTERNO (melhor chance)
        vacancia = "N/D"
        inad = "N/D"

        # procura padrões escondidos
        vac_match = re.search(r"vacancy.*?([0-9,.]+)", html, re.IGNORECASE)
        inad_match = re.search(r"default.*?([0-9,.]+)", html, re.IGNORECASE)

        if vac_match:
            vacancia = vac_match.group(1)

        if inad_match:
            inad = inad_match.group(1)

        # 🔥 fallback texto normal
        if vacancia == "N/D":
            vac_text = re.search(r"Vac[âa]ncia[^0-9]*([0-9,.]+)%", html)
            if vac_text:
                vacancia = vac_text.group(1)

        if inad == "N/D":
            inad_text = re.search(r"Inadimpl[êe]ncia[^0-9]*([0-9,.]+)%", html)
            if inad_text:
                inad = inad_text.group(1)

        # PORTFÓLIO
        ativos = re.findall(r"[A-Z]{4}\d{2}", html)
        ativos = list(set(ativos))

        return {
            "ticker": ticker.upper(),
            "vacancia": vacancia,
            "inadimplencia": inad,
            "portfolio": ativos[:5]
        }

    except Exception as e:
        return fallback(ticker, str(e))


def fallback(ticker, erro):
    return {
        "ticker": ticker.upper(),
        "vacancia": "N/D",
        "inadimplencia": "N/D",
        "portfolio": [],
        "erro": erro
    }
