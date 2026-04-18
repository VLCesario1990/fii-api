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
options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# =========================
# 🔧 FUNÇÕES
# =========================
def converter_percentual(valor):
    return round(float(valor.replace(",", ".")) / 100, 4)

def limpar_numero(valor):
    valor = valor.replace(".", "").replace(",", ".")
    try:
        return float(valor)
    except:
        return 0

resultado = {}

# =========================
# 🔎 SCRAPING
# =========================
for fii in fiis:
    print(f"\n🔎 {fii.upper()}")

    try:
        url = f"https://investidor10.com.br/fiis/{fii}/"
        driver.get(url)

        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        soup = BeautifulSoup(driver.page_source, "html.parser")
        texto = soup.get_text(" ", strip=True).lower()

        # =========================
        # 📊 VACÂNCIA / INADIMPLÊNCIA
        # =========================
        vacancia_match = re.search(r"vac[aâ]ncia.*?(\d+,\d+)%", texto)
        inad_match = re.search(r"inadimpl[êe]ncia.*?(\d+,\d+)%", texto)

        vacancia = converter_percentual(vacancia_match.group(1)) if vacancia_match else 0
        inadimplencia = converter_percentual(inad_match.group(1)) if inad_match else 0

        # =========================
        # 🏢 TIPO / SEGMENTO / PRAZO
        # =========================
        try:
            tipo = driver.find_element(By.XPATH, "//div[contains(text(),'Tipo de fundo')]/following::div[1]").text
        except:
            tipo = "N/A"

        try:
            segmento = driver.find_element(By.XPATH, "//div[contains(text(),'Segmento')]/following::div[1]").text
        except:
            segmento = "N/A"

        try:
            prazo = driver.find_element(By.XPATH, "//div[contains(text(),'Prazo de duração')]/following::div[1]").text
        except:
            prazo = "N/A"

        # =========================
        # 📊 INDICADORES
        # =========================
        try:
            preco = limpar_numero(driver.find_element(By.XPATH, "//span[@class='value']").text)
        except:
            preco = 0

        try:
            pvp = limpar_numero(driver.find_element(By.XPATH, "//span[contains(text(),'P/VP')]/following::span[1]").text)
        except:
            pvp = 0

        try:
            dy = limpar_numero(driver.find_element(By.XPATH, "//span[contains(text(),'DY (12M)')]/following::span[1]").text) / 100
        except:
            dy = 0

        try:
            cotas = limpar_numero(driver.find_element(By.XPATH, "//span[contains(text(),'Nº de cotas')]/following::span[1]").text)
        except:
            cotas = 0

        try:
            cotistas = limpar_numero(driver.find_element(By.XPATH, "//span[contains(text(),'Nº de cotistas')]/following::span[1]").text)
        except:
            cotistas = 0

        resultado[fii.upper()] = {
            "vacancia": vacancia,
            "inadimplencia": inadimplencia,
            "tipo": tipo,
            "segmento": segmento,
            "prazo": prazo,
            "preco": preco,
            "pvp": pvp,
            "dy": dy,
            "cotas": cotas,
            "cotistas": cotistas
        }

        print("Resultado:", resultado[fii.upper()])

    except Exception as e:
        print(f"🔥 ERRO em {fii.upper()}: {e}")
        resultado[fii.upper()] = {
            "vacancia": 0,
            "inadimplencia": 0,
            "tipo": "N/A",
            "segmento": "N/A",
            "prazo": "N/A",
            "preco": 0,
            "pvp": 0,
            "dy": 0,
            "cotas": 0,
            "cotistas": 0
        }

driver.quit()

# =========================
# 💾 CSV FINAL
# =========================
linhas = []

for fii, dados in resultado.items():
    linhas.append([
        fii,
        dados["preco"],
        dados["pvp"],
        dados["dy"],
        dados["tipo"],
        dados["segmento"],
        dados["vacancia"],
        dados["inadimplencia"],
        dados["prazo"],
        dados["cotas"],
        dados["cotistas"],
        agora
    ])

linhas.sort(key=lambda x: x[0])

with open("dados_fiis.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f, delimiter=";")

    writer.writerow([
        "FII",
        "Preco",
        "PVP",
        "DY_12M",
        "Tipo",
        "Segmento",
        "Vacancia",
        "Inadimplencia",
        "Prazo",
        "Num_Cotas",
        "Num_Cotistas",
        "DataAtualizacao"
    ])

    writer.writerows(linhas)

print("\n✅ CSV completo gerado com sucesso!")
