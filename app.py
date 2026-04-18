import re
import csv
import os
import json

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from datetime import datetime
from zoneinfo import ZoneInfo

# =========================
# 🕒 DATA BR
# =========================
agora = datetime.now(ZoneInfo("America/Sao_Paulo")).strftime("%d-%m-%Y %H:%M")

# =========================
# 📄 LISTA DE FIIs
# =========================
with open("fii.txt", "r", encoding="utf-8") as f:
    fiis = [linha.strip().lower() for linha in f if linha.strip()]

# =========================
# 🔧 SELENIUM
# =========================
options = webdriver.ChromeOptions()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# =========================
# 🔧 FUNÇÕES
# =========================
def converter_percentual(valor):
    return round(float(valor.replace(",", ".")) / 100, 4)

def normalizar(texto):
    return texto.replace("í", "i").replace("é", "e").replace("ã", "a")

resultado = {}

# =========================
# 🔎 SCRAPING
# =========================
for fii in fiis:
    print(f"\n🔎 {fii.upper()}")

    url = f"https://investidor10.com.br/fiis/{fii}/"
    driver.get(url)

    wait = WebDriverWait(driver, 20)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    texto = normalizar(driver.page_source.lower())

    vacancia_match = re.search(r"vac[aâ]ncia[^0-9]*?(\d+,\d+)%", texto)
    inad_match = re.search(r"inadimpl[êe]ncia[^0-9]*?(\d+,\d+)%", texto)

    vacancia = converter_percentual(vacancia_match.group(1)) if vacancia_match else 0
    inadimplencia = converter_percentual(inad_match.group(1)) if inad_match else 0

    resultado[fii.upper()] = {
        "vacancia": vacancia,
        "inadimplencia": inadimplencia
    }

    print("Resultado:", resultado[fii.upper()])

driver.quit()

# =========================
# 💾 CSV LOCAL
# =========================
linhas = []

for fii, dados in resultado.items():
    linhas.append([
        fii,
        dados["vacancia"],
        dados["inadimplencia"],
        agora
    ])

linhas.sort(key=lambda x: x[0])

file_path = "dados_fiis.csv"

with open(file_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f, delimiter=";")

    writer.writerow([
        "FII",
        "Vacancia",
        "Inadimplencia",
        "DataAtualizacao"
    ])

    writer.writerows(linhas)

print("✅ CSV gerado localmente!")
