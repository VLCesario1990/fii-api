from flask import Flask, jsonify
import json
import os

app = Flask(__name__)

DATA_FILE = "data/fii.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE) as f:
        return json.load(f)

@app.route("/")
def home():
    return jsonify({"status": "API FII leve 🚀"})

@app.route("/fii/<ticker>")
def fii(ticker):
    data = load_data()
    ticker = ticker.lower()

    if ticker in data:
        return jsonify({
            "ticker": ticker.upper(),
            **data[ticker]
        })

    return jsonify({"erro": "Ticker não encontrado"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
