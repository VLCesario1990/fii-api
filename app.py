import re
import os
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 🔹 Google Sheets
import gspread
from google.oauth2.service_account import Credentials

# =========================
# 🔹 lista de FIIs
# =========================
fiis = ["xpml11", "hglg11", "vghf11"]

# =========================
# 🔧 Selenium
# =========================
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def converter(valor):
    return float(valor.replace(",", "."))

resultado = {}

# =========================
# 🔎 SCRAPING
# =========================
for fii in fiis:
    print(f"\n🔎 {fii.upper()}")

    url = f"https://investidor10.com.br/fiis/{fii}/"
    driver.get(url)

    wait = WebDriverWait(driver, 15)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    texto = driver.page_source.lower()

    vacancia_match = re.search(r"vac[aâ]ncia.*?(\d+,\d+)%", texto)
    inad_match = re.search(r"inadimpl[êe]ncia.*?(\d+,\d+)%", texto)

    vacancia = converter(vacancia_match.group(1)) if vacancia_match else None
    inadimplencia = converter(inad_match.group(1)) if inad_match else None

    resultado[fii.upper()] = [vacancia, inadimplencia]

driver.quit()

# =========================
# 🔐 GOOGLE SHEETS (via GitHub Secret)
# =========================

# 👉 pega credenciais do secret (IMPORTANTE)
cred_json = os.environ["GOOGLE_CREDENTIALS"]
cred_dict = json.loads(cred_json)

scope = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_info(cred_dict, scopes=scope)
client = gspread.authorize(creds)

# =========================
# 📄 ABRIR OU CRIAR PLANILHA
# =========================
nome_planilha = "info_fii_python"

try:
    sheet = client.open(nome_planilha).sheet1
except:
    sheet = client.create(nome_planilha).sheet1

# =========================
# 🧹 LIMPAR E ATUALIZAR
# =========================
sheet.clear()

# cabeçalho
sheet.append_row(["FII", "Vacancia", "Inadimplencia"])

# dados
for fii, dados in resultado.items():
    sheet.append_row([fii, dados[0], dados[1]])

print("✅ Planilha 'info_fii_python' atualizada!")
