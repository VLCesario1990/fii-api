import re
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 🔹 lista de FIIs
fiis = ["xpml11", "hglg11", "vghf11"]

options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# 🔧 função para converter número BR → float
def converter(valor):
    return float(valor.replace(",", "."))

resultado = {}

for fii in fiis:
    print(f"\n🔎 Processando {fii.upper()}...")

    url = f"https://investidor10.com.br/fiis/{fii}/"
    driver.get(url)

    wait = WebDriverWait(driver, 15)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    texto = driver.page_source.lower()

    # 🔍 regex
    vacancia_match = re.search(r"vac[aâ]ncia.*?(\d+,\d+)%", texto)
    inad_match = re.search(r"inadimpl[êe]ncia.*?(\d+,\d+)%", texto)

    vacancia = converter(vacancia_match.group(1)) if vacancia_match else None
    inadimplencia = converter(inad_match.group(1)) if inad_match else None

    resultado[fii.upper()] = {
        "vacancia": vacancia,
        "inadimplencia": inadimplencia
    }

    print("Resultado:", resultado[fii.upper()])

driver.quit()

# 💾 salvar JSON final
with open("dados_fiis.json", "w", encoding="utf-8") as f:
    json.dump(resultado, f, indent=4, ensure_ascii=False)

print("\n✅ JSON gerado com sucesso!")
