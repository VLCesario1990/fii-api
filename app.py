import re
import csv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup
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

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 20)

# =========================
# 🔧 FUNÇÃO
# =========================
def converter_percentual(valor):
    return round(float(valor.replace(",", ".")) / 100, 4)

resultado = {}

# =========================
# 🔎 SCRAPING
# =========================
for fii in fiis:
    print(f"\n🔎 {fii.upper()}")

    try:
        url = f"https://investidor10.com.br/fiis/{fii}/"
        driver.get(url)

        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # 🔥 pega texto limpo (ESSENCIAL)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        texto = soup.get_text(" ", strip=True).lower()

        # 🔍 regex simples e confiável
        vacancia_match = re.search(r"vac[aâ]ncia.*?(\d+,\d+)%", texto)
        inad_match = re.search(r"inadimpl[êe]ncia.*?(\d+,\d+)%", texto)

        vacancia = converter_percentual(vacancia_match.group(1)) if vacancia_match else 0
        inadimplencia = converter_percentual(inad_match.group(1)) if inad_match else 0

        resultado[fii.upper()] = {
            "vacancia": vacancia,
            "inadimplencia": inadimplencia
        }

        print("Resultado:", resultado[fii.upper()])

    except Exception as e:
        print(f"🔥 ERRO em {fii.upper()}: {e}")
        resultado[fii.upper()] = {
            "vacancia": 0,
            "inadimplencia": 0
        }

driver.quit()

# =========================
# 💾 CSV FINAL
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

with open("dados_fiis.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f, delimiter=";")

    writer.writerow([
        "FII",
        "Vacancia",
        "Inadimplencia",
        "DataAtualizacao"
    ])

    writer.writerows(linhas)

print("\n✅ CSV simples gerado com sucesso!")
