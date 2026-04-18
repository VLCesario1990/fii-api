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
wait = WebDriverWait(driver, 20)

# =========================
# 🔧 FUNÇÕES
# =========================
def limpar_numero(valor):
    valor = valor.replace("R$", "").replace("%", "").strip()
    valor = valor.replace(".", "").replace(",", ".")
    try:
        return float(valor)
    except:
        return 0

def converter_percentual(valor):
    return round(float(valor.replace(",", ".")) / 100, 4)

# 🔥 função inteligente (ESSA É A CHAVE)
def pegar_valor(label):
    try:
        el = driver.find_element(
            By.XPATH,
            f"//*[contains(text(),'{label}')]/following::span[1]"
        )
        return el.text.strip()
    except:
        return ""

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

        # =========================
        # TEXTO (regex)
        # =========================
        soup = BeautifulSoup(driver.page_source, "html.parser")
        texto = soup.get_text(" ", strip=True).lower()

        vacancia_match = re.search(r"vac[aâ]ncia.*?(\d+,\d+)%", texto)
        inad_match = re.search(r"inadimpl[êe]ncia.*?(\d+,\d+)%", texto)

        vacancia = converter_percentual(vacancia_match.group(1)) if vacancia_match else 0
        inadimplencia = converter_percentual(inad_match.group(1)) if inad_match else 0

        # =========================
        # 📊 INDICADORES (estáveis)
        # =========================
        preco = limpar_numero(pegar_valor("R$"))
        pvp = limpar_numero(pegar_valor("P/VP"))
        dy = limpar_numero(pegar_valor("DY (12M)")) / 100

        cotas = limpar_numero(pegar_valor("Nº de cotas"))
        cotistas = limpar_numero(pegar_valor("Nº de cotistas"))

        # =========================
        # 📌 INFO DO FUNDO
        # =========================
        try:
            tipo = driver.find_element(By.XPATH, "//*[contains(text(),'Tipo de Fundo')]/following::div[1]").text
        except:
            tipo = "N/A"

        try:
            segmento = driver.find_element(By.XPATH, "//*[contains(text(),'Segmento')]/following::div[1]").text
        except:
            segmento = "N/A"

        try:
            prazo = driver.find_element(By.XPATH, "//*[contains(text(),'Prazo de duração')]/following::div[1]").text
        except:
            prazo = "N/A"

        resultado[fii.upper()] = {
            "preco": preco,
            "pvp": pvp,
            "dy": dy,
            "tipo": tipo,
            "segmento": segmento,
            "vacancia": vacancia,
            "inadimplencia": inadimplencia,
            "prazo": prazo,
            "cotas": cotas,
            "cotistas": cotistas
        }

        print("Resultado:", resultado[fii.upper()])

    except Exception as e:
        print(f"🔥 ERRO em {fii.upper()}: {e}")
        resultado[fii.upper()] = {
            "preco": 0,
            "pvp": 0,
            "dy": 0,
            "tipo": "N/A",
            "segmento": "N/A",
            "vacancia": 0,
            "inadimplencia": 0,
            "prazo": "N/A",
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

print("\n✅ CSV COMPLETO GERADO COM SUCESSO!")
