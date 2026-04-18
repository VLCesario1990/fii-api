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
    return float(valor.replace(",", ".")) / 100

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

    vacancia_match = re.search(r"vacancia[^%]*?(\d+,\d+)%", texto)
    inad_match = re.search(r"inadimplencia[^%]*?(\d+,\d+)%", texto)

    tipo_match = re.search(r"tipo[^a-z]*(tijolo|papel|hibrido|misto|fii de fundos)", texto)

    segmento_match = re.search(
        r"segmento[^a-z]*(logistica|shopping|lajes corporativas|escritorios|residencial|hotel|hospital|educacional)",
        texto
    )

    vacancia = converter_percentual(vacancia_match.group(1)) if vacancia_match else None
    inadimplencia = converter_percentual(inad_match.group(1)) if inad_match else None
    tipo = tipo_match.group(1).capitalize() if tipo_match else "N/A"
    segmento = segmento_match.group(1).capitalize() if segmento_match else "N/A"

    resultado[fii.upper()] = {
        "vacancia": vacancia,
        "inadimplencia": inadimplencia,
        "tipo": tipo,
        "segmento": segmento
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
        dados["tipo"],
        dados["segmento"],
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
        "Tipo",
        "Segmento",
        "DataAtualizacao"
    ])

    writer.writerows(linhas)

print("✅ CSV gerado localmente!")

# =========================
# ☁️ ENVIO PARA GOOGLE DRIVE
# =========================
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

cred_json = os.environ["GOOGLE_CREDENTIALS"]
cred_dict = json.loads(cred_json)

creds = Credentials.from_service_account_info(
    cred_dict,
    scopes=["https://www.googleapis.com/auth/drive"]
)

service = build("drive", "v3", credentials=creds)

# 👉 ID da sua pasta (já peguei da sua imagem)
PASTA_ID = "1AUGdmBwfQWwv14K_vHeFk06K2fgwcbeb"

# 🔎 verifica se já existe
query = f"name='dados_fiis.csv' and '{PASTA_ID}' in parents and trashed=false"
files = service.files().list(q=query).execute().get("files", [])

media = MediaFileUpload(file_path, mimetype="text/csv")

if files:
    service.files().update(
        fileId=files[0]["id"],
        media_body=media
    ).execute()
    print("🔄 CSV atualizado no Google Drive!")
else:
    service.files().create(
        body={
            "name": "dados_fiis.csv",
            "parents": [PASTA_ID]
        },
        media_body=media
    ).execute()
    print("📤 CSV enviado para o Google Drive!")
