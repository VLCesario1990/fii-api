from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time

options = webdriver.ChromeOptions()
options.add_argument("--headless")  # roda sem abrir navegador

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

driver.get("https://investidor10.com.br/fiis/xpml11/")

time.sleep(5)  # espera carregar JS

# pega tudo da página
texto = driver.page_source

driver.quit()

print(texto[:2000])
