from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

driver.get("https://investidor10.com.br/fiis/xpml11/")

# 🔥 espera até aparecer algo na tela
wait = WebDriverWait(driver, 30)

body = wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

texto = driver.page_source

driver.quit()

# DEBUG
print("TAMANHO HTML:", len(texto))

# 🔍 procurar inadimplência
for linha in texto.split("\n"):
    if "inadimpl" in linha.lower():
        print("ACHOU:", linha)
