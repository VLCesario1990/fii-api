from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

HEADERS = {"User-Agent": "Mozilla/5.0"}

def get_fii_data(ticker):
    try:
        url = f"https://www.fundsexplorer.com.br/funds/{ticker.lower()}"
        r = requests.get(url, headers=HEADERS, timeout=10)

        soup = BeautifulSoup(r.text, "html.parser")
        html = soup.get_text()

        vacancia = None
        if "Vacância" in html:
            try:
                vacancia = html.split("Vacância")[1].split("%")[0].strip()
            except:
                pass

        inad = None
        if "Inadimplência" in html:
            try:
                inad = html.split("Inadimplência")[1].split("%")[0].strip()
            except:
                pass

        ativos = r.text
        ativos = list(set([x for x in ativos.split() if len(x) == 6 and x[-2:].isdigit()]))

        return {
            "ticker": ticker,
            "vacancia": vacancia,
            "inadimplencia": inad,
            "portfolio": ativos[:5]
        }

    except Exception as e:
        return {"erro": str(e)}

@app.route("/fii/<ticker>")
def fii(ticker):
    return jsonify(get_fii_data(ticker))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
