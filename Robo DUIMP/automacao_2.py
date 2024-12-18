from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from datetime import datetime
import pandas as pd
import time

#define usuário do Windows
userWindows = "amartu01"
# Configurações do Chrome e da conexão local
chrome_options = Options()
chrome_options.add_argument(f"user-data-dir=C:\\Users\\{userWindows}\\AppData\\Local\\Google\\Chrome\\User Data")
chrome_options.add_experimental_option("debuggerAddress", "localhost:9222")

# Inicializa o driver do Chrome
driver = webdriver.Chrome(options=chrome_options)

url_teste = "https://val.portalunico.siscomex.gov.br/catp/#/produto/incluir"
url_producao = "https://portalunico.siscomex.gov.br/catp/#/produto/incluir"

# Importando o catálogo de produtos (Agora usando o Excel)
# Ler a planilha Excel corretamente
tabela = pd.read_excel(f"C:\\Users\\{userWindows}\\OneDrive - Donaldson Company, Inc\\Desktop\\Subidão DUIMP\\Plan DUIMP Project\\Planilha Catálogo\\CATALOGO ROBO.xlsx",  sheet_name="Sheet1")

PgDadosBasicos = 1
atributos = 0
contAtributos = 0
def verificar_pagina_completa(driver, timeout=30):
    # Usa WebDriverWait com uma função lambda para verificar o estado 'complete'
    try:
        WebDriverWait(driver, timeout).until(
            lambda driver: driver.execute_script('return document.readyState') == 'complete'
        )
        return True
    except Exception as e:
        print(f"Erro: A página não foi carregada dentro do tempo limite ({timeout}s).")
        return False
    
def mover_linhas_para_feitos(tabela, erro):

    if erro == 1 or erro == 3:
        try:
            #pendentes
            planilha_copia = pd.read_excel(f"C:\\Users\\{userWindows}\\OneDrive - Donaldson Company, Inc\\Desktop\\Subidão DUIMP\\Plan DUIMP Project\\Planilha Catálogo\\pendentes.xlsx")
        except FileNotFoundError:
            planilha_copia = pd.DataFrame()
    else:
        try:
            #feitos
            planilha_copia = pd.read_excel(f"C:\\Users\\{userWindows}\\OneDrive - Donaldson Company, Inc\\Desktop\\Subidão DUIMP\\Plan DUIMP Project\\Planilha Catálogo\\feitos.xlsx")
        except FileNotFoundError:
            planilha_copia = pd.DataFrame()

    tabela_a_mover = tabela.iloc[:atributos+2].copy()  
    tabela_a_mover.loc[:, 'data'] = datetime.today().strftime('%Y-%m-%d')  # Usando .loc para garantir a modificação

    if erro == 3:
        #preencher a coluna observacoes como "tempo de espera maximo atingido"
        tabela_a_mover.loc[:, 'observação'] =  "tempo de espera máxima agintido, tente mais tarde"

    if not planilha_copia.empty:
        planilha_copia = planilha_copia.replace("", float("nan"))
        primeira_linha_vazia = planilha_copia.isna().all(axis=1).idxmax()  # Encontra o índice da primeira linha vazia
        if pd.isna(primeira_linha_vazia):
            primeira_linha_vazia = len(planilha_copia)
    else:
        primeira_linha_vazia = 0

    planilha_copia = pd.concat([planilha_copia.iloc[:primeira_linha_vazia], tabela_a_mover, planilha_copia.iloc[primeira_linha_vazia:]], ignore_index=True)
    planilha_copia.to_excel(f"C:\\Users\\{userWindows}\\OneDrive - Donaldson Company, Inc\\Desktop\\Subidão DUIMP\\Plan DUIMP Project\\Planilha Catálogo\\feitos.xlsx", index=False)

    tabela = tabela.iloc[0:0]  # Deixa apenas a primeira linha
    tabela.to_excel(f"C:\\Users\\{userWindows}\\OneDrive - Donaldson Company, Inc\\Desktop\\Subidão DUIMP\\Plan DUIMP Project\\Planilha Catálogo\\CATALOGO ROBO.xlsx", index=False)

def pagina_correta():
    
    driver.get(url_producao)

    driver.refresh()  # Isto simula o F5
    time.sleep(3)

pagina_correta()
for linha in tabela.index:

    if verificar_pagina_completa(driver, timeout=30):
        if contAtributos == atributos:
            PgDadosBasicos = 1
            contAtributos = 0
            mover_linhas_para_feitos(tabela, 0)

            atributos = int(tabela.loc[linha, "qnt"])

        if PgDadosBasicos == 1:
            # Verificando se 'ncm' existe na tabela
            if 'ncm' not in tabela.columns:
                print("Coluna 'ncm' não encontrada.")
                break  # Ou levante um erro dependendo da sua lógica

            ncm = WebDriverWait(driver, 1000).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".p-inputtext.p-component.p-element.p-inputmask"))
            )
            if ncm.is_enabled() and ncm.is_displayed():
                ncm.clear() 
                ncm.send_keys(str(tabela.loc[linha, "ncm"]))  
            else:
                print("NCM não está visível ou não está habilitado.")
                mover_linhas_para_feitos(tabela, 1)
                print("Itens movidos para erro")
                break

            # Seleciona importação/exportação
            modalidade = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.ID, "modalidade"))
            )
            modalidade.click()

            option_modalidade = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[text()='Importação']"))
            )
            option_modalidade.click()  # Clica na opção "Importação"

            # Seleção do codigoInterno
            time.sleep(2)
            codigo_interno = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "codigoInterno"))
            )
            codigo_interno.send_keys(str(tabela.loc[linha, "codigointerno"]))  # Usando o campo correto da tabela

            # Aguarda até o botão "Incluir" estar visível e clicável
            btn_incluir = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, "//span[text()='Incluir']/ancestor::button"))
            )
            btn_incluir.click()

            # Seleção dos países
            campo_pais = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.ID, "paisOrigem"))
            )
            campo_pais.click()

            # Digita a sigla
            sigla_pais = campo_pais.find_element(By.CSS_SELECTOR, "input")
            sigla_pais.send_keys(str(tabela.loc[linha, "paisorigem"]))  # Usando o campo correto da tabela
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "ng-option"))
            )

            # Selecionar a opção que corresponde à sigla
            opcoes_pais = driver.find_elements(By.CLASS_NAME, "ng-option")
            for opcao in opcoes_pais:
                # Verifica se a opção começa com a sigla c/ a função startswith
                if opcao.text.startswith(str(tabela.loc[linha, "paisorigem"])):  # Usando o campo correto da tabela
                    opcao.click()
                    break

            fabricanteConhecido = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//label[@for='pucx-radio-fabDesconhecidoSim']"))
            )
            fabricanteConhecido.click()

            # Seleciona o endereço (clicar na lupa)
            lupa_pais = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".p-ripple.p-element.btn.btn-form.p-button.p-component.p-button-icon-only")))
            lupa_pais.click()

            modal = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "p-dialog-content"))
            )

            # Digitar o código (estilo OPE_5) e em seguida consulta
            codigo_input = modal.find_element(By.ID, "codigo")
            codigo_input.send_keys(str(tabela.loc[linha, "codigo"]))  # Usando o campo correto da tabela

            # Clica em consultar
            consultar_button = modal.find_element(By.XPATH, "//button[contains(span, 'consultar')]")
            consultar_button.click()

            # Clica no rádio com a opção escolhida anteriormente
            radio_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='radio'][name='gridCampoTaSelect']"))
            )
            radio_button.click()

            btn_confirmar = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "btnConfirmar")))

            btn_confirmar.click()

            btn_vincular = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[text()='Vincular']/ancestor::button"))
            )
            btn_vincular.click()

            # Muda para a página Descrição do Produto
            Pag_Descricao_Produto = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "p-tabpanel-1-label")))
            Pag_Descricao_Produto.click()

            # Digita a marca
            fornecedor = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "p-tabpanel-1-label")))
            fornecedor.click()

            # Muda para desc do produto
            elemento = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "p-tabpanel-1-label")))
            elemento.click()
            

            WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "denominacao"))).send_keys(str(tabela.loc[linha, "denominacao"]))
            WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "descricao"))).send_keys(str(tabela.loc[linha, "descricao"]))

            
            PgDadosBasicos = 0

        tabela.columns = tabela.columns.str.strip().str.lower() 

        contAtributos +=1
        # Preenche os atributos de acordo com o tipo de dado
        if "atributo" in tabela.columns and "tipodado" in tabela.columns and "resposta" in tabela.columns:
            nome_atributo = str(tabela.loc[linha, "atributo"])
            tipo_input = str(tabela.loc[linha, "tipodado"]).upper()
            resposta = str(tabela.loc[linha, "resposta"])

            if tipo_input == "BOOLEANO":
        # Normaliza a resposta
                resposta_bool = str(tabela.loc[linha, "resposta"]).strip().lower()
                if resposta_bool == "não" or  resposta_bool == "Não":
                    resposta_bool = "Nao"  # Converte "não" para "nao"

                # Define o valor esperado no HTML
                valor_radio = "true" if resposta_bool == "sim" else "false"
                id_elemento = f"pucx-radio-atributos_{nome_atributo}{resposta_bool.capitalize()}"

                try:
                    # Localiza o contêiner que contém os radio buttons
                    container = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, f"//div[contains(@class, 'pucx-box') and contains(@class, 'radioButton')]"))
                    )
                    # Verifica os radio buttons dentro do contêiner
                    elemento_radio = container.find_element(By.XPATH, f"//input[@type='radio' and @id='{id_elemento}' and @value='{valor_radio}']")
                    
                    # Clica no elemento
                    label_elemento = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, f"//label[@for='{id_elemento}']"))
                    )
                    label_elemento.click()
                    print(f"Elemento booleano '{id_elemento}' selecionado com sucesso.")
                except Exception as e:
                    print(f"Erro ao interagir com o elemento booleano '{id_elemento}': {e}")
                    #implementa para copiar todas as linha p/pendente
                    mover_linhas_para_feitos(tabela, 1)
                time.sleep(2)

            elif tipo_input == "TEXTO":
                # Primeiro tenta encontrar o campo _input
                id_elemento_input = f"{nome_atributo}_input"
                id_elemento_textarea = f"{nome_atributo}_textarea"
                
                # Tentar converter o valor de 'resposta' para int, depois para float, se necessário
                try:
                    # Tentando converter para inteiro
                    resposta = int(resposta)  # Se puder converter para inteiro, faz a conversão
                    driver.execute_script("arguments[0].value = arguments[1];", id_elemento_input, resposta)
                except ValueError:
                    try:
                        # Se falhar, tenta converter para float
                        resposta = float(resposta)  # Se puder converter para float, faz a conversão
                        driver.execute_script("arguments[0].value = arguments[1];", id_elemento_input, resposta)
                    except ValueError:
                        # Se falhar em ambas, mantém como string
                        resposta = str(resposta)

                try:
                    # Tenta encontrar e preencher o campo de entrada (_input)
                    elemento_texto = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.ID, id_elemento_input))
                    )
                    elemento_texto.clear()  # Limpa o campo antes de preencher
                    elemento_texto.send_keys(resposta)  # Envia a resposta (convertida para string)
                except Exception as e:
                    print(f"Elemento '{id_elemento_input}' não encontrado. Tentando com '{id_elemento_textarea}'.")
                    try:
                        # Caso não encontre _input, tenta _textarea
                        elemento_textarea = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.ID, id_elemento_textarea))
                        )
                        elemento_textarea.clear()  # Limpa o campo antes de preencher
                        elemento_textarea.send_keys(resposta)  # Envia a resposta (convertida para string)
                    except Exception as e:
                        print(f"Erro ao interagir com o elemento de texto '{id_elemento_textarea}': {e}")
                        # Caso ocorra um erro, chama a função para mover as linhas para a planilha 'feitos'
                        mover_linhas_para_feitos(tabela, 1)


        if(contAtributos==atributos):         
            try:
                # Localiza e clica no botão "Salvar e Ativar"
                salvar_ativar = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "salvar_ativar"))
                )
                salvar_ativar.click()  # Clica no botão
                print("Botão 'Salvar e Ativar' clicado com sucesso.")
                #quero fazer isso ´so se o botao salvar_ativar tiver dado certo...
            
            except Exception as e:
                print(f"Erro ao clicar no botão 'Salvar e Ativar': {e}")    
    else:
        mover_linhas_para_feitos(tabela, 3)

    # Fechar o navegador
    #driver.quit()
