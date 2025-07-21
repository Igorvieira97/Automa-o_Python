import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configurações
CAMINHO_CHROMEDRIVER = r'C:\Users\Igor.pessoa\vmulti_automation\chromedriver.exe'
USUARIO = 'xxxxxxxxx'  # seu usuário
SENHA = 'xxxxxxxxxx'   # sua senha
URL_LOGIN = "xxxxxxxx"
URL_USUARIOS = "xxxxxxxxxxxxxxxxxx"
URL_EDICAO_BASE = "xxxxxxxxxxxxxxx"
PROGRESSO_PATH = 'progresso.txt'

def salvar_print(driver, nome):
    caminho = os.path.join(os.getcwd(), f'{nome}.png')
    driver.save_screenshot(caminho)
    print(f"🖼 Print salvo: {caminho}")

options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)
service = Service(CAMINHO_CHROMEDRIVER)
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 60)

try:
    # Login
    print("🔐 Acessando login...")
    driver.get(URL_LOGIN)
    wait.until(EC.presence_of_element_located((By.ID, 'login'))).send_keys(USUARIO)
    wait.until(EC.presence_of_element_located((By.ID, 'password_sem_md5'))).send_keys(SENHA)
    wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Entrar')]"))).click()

    print("⏳ Aguardando pós-login...")
    wait.until(EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'Bem vindo ao Sistema Multidados')]")))
    time.sleep(5)

    # Recupera progresso
    if os.path.exists(PROGRESSO_PATH):
        with open(PROGRESSO_PATH, 'r') as f:
            codigo_sequencial = int(f.read().strip())
    else:
        codigo_sequencial = 1

    while True:
        print("📂 Acessando lista de usuários...")
        driver.get(URL_USUARIOS)
        time.sleep(5)  # espera a lista carregar

        botoes = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a.DOM_grid_btn_edit_img')))
        ids = []
        for botao in botoes:
            href = botao.get_attribute('href')
            if "idsenha=" in href:
                id_usuario = href.split("idsenha=")[-1]
                ids.append(id_usuario)

        print(f"🧾 {len(ids)} usuários encontrados.")

        # Se já passou do último, para o loop
        if codigo_sequencial > len(ids):
            print("✅ Todos os usuários foram editados.")
            break

        # Pega o ID do usuário atual
        id_usuario = ids[codigo_sequencial - 1]
        print(f"✏️ Editando usuário {codigo_sequencial} (ID {id_usuario})...")

        # Vai para edição
        driver.get(URL_EDICAO_BASE + id_usuario)

        # Espera o campo aparecer
        campo_codigo = wait.until(EC.presence_of_element_located((By.ID, 'codigo_auxiliar')))

        # Verifica se já está preenchido
        if campo_codigo.get_attribute("value").strip():
            print(f"⏭ Campo já preenchido para o usuário {id_usuario}. Pulando para o próximo...")
            codigo_sequencial += 1
            continue  # pula para o próximo usuário

        # Preenche o código
        campo_codigo.clear()
        campo_codigo.send_keys(str(codigo_sequencial))

        # Clica em confirmar
        btn_confirmar = driver.find_element(By.ID, 'btnIncluir')
        btn_confirmar.click()

        print(f"✅ Código {codigo_sequencial} salvo com sucesso.")

        # Atualiza progresso
        codigo_sequencial += 1
        with open(PROGRESSO_PATH, 'w') as f:
            f.write(str(codigo_sequencial))

        # Aguarda a página voltar para a lista (URL correta)
        wait.until(EC.url_contains("senhas_list"))
        time.sleep(4)  # para garantir que a lista carregou

except Exception as e:
    print(f"❌ Erro geral: {repr(e)}")
    salvar_print(driver, 'erro_geral')

finally:
    print("🛑 Script finalizado.")
    input("🔒 Pressione Enter para sair...")
