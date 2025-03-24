import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os

# Configurando o WebDriver
driver = webdriver.Chrome()

try:
    # URL do site da B3
    url = 'https://sistemaswebb3-listados.b3.com.br/indexPage/day/IBOV?language=pt-br'
    driver.get(url)

    # Aguardando o carregamento do conteúdo
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'table'))
    )

    # Função para obter a data do pregão
    def obter_data_pregao():
        try:
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            data_elemento = soup.find('span', class_='strong')  # Ajuste se necessário
            if data_elemento:
                data_texto = data_elemento.text.strip()
                return datetime.strptime(data_texto, "%d/%m/%Y").strftime('%Y-%m-%d')
        except Exception as e:
            print(f"Erro ao obter a data do pregão: {e}")
        return datetime.now().strftime('%Y-%m-%d')  # Fallback

    data_pregao = obter_data_pregao()
    print(f"Data do pregão detectada: {data_pregao}")

    # Criar diretório se não existir
    pasta_saida = f'data_pregao={data_pregao}'
    if not os.path.exists(pasta_saida):
        os.makedirs(pasta_saida)

    # Função para extrair dados de uma página
    def extrair_dados(html):
        soup = BeautifulSoup(html, 'html.parser')
        tabela = soup.find('table', {'class': ['table', 'table-responsive-sm', 'table-responsive-md']})
        dados_pagina = []
        if tabela:
            for linha in tabela.find_all('tr'):
                colunas = linha.find_all('td')
                linha_dados = [coluna.text.strip() for coluna in colunas]
                if len(linha_dados) == 5:
                    dados_pagina.append(linha_dados)
        return dados_pagina

    # Extraindo dados de todas as páginas
    dados = []

    while True:
        # Extraindo dados da página atual
        html = driver.page_source
        dados.extend(extrair_dados(html))

        try:
            # Aguarda a presença do botão de próxima página
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'li.pagination-next a'))
            )

            # Reencontrando o botão para evitar StaleElementReferenceException
            botao_proxima_pagina = driver.find_element(By.CSS_SELECTOR, 'li.pagination-next a')

            # Verificar se o botão está desabilitado
            if 'disabled' in botao_proxima_pagina.find_element(By.XPATH, '..').get_attribute('class'):
                break  # Sai do loop se o botão estiver desabilitado

            # Mover o mouse até o botão e clicar
            actions = ActionChains(driver)
            actions.move_to_element(botao_proxima_pagina).click().perform()

            # Aguarda o carregamento da próxima página antes de continuar
            WebDriverWait(driver, 10).until(
                EC.staleness_of(botao_proxima_pagina)  # Aguarda o botão antigo ficar inválido
            )
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'table'))
            )

        except (NoSuchElementException, TimeoutException) as e:
            print(f"Erro ao tentar navegar para a próxima página: {e}")
            break

    # Extraindo as linhas finais na última página
    linhas_finais = extrair_dados(driver.page_source)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    linhas_finais.extend(extrair_dados(driver.page_source))
    total_linhas = soup.select('tr:has(td[colspan="3"])')
    for linha in total_linhas:
        colunas = linha.find_all('td')
        linha_dados = [coluna.text.strip() for coluna in colunas]
        if 'Quantidade Teórica Total' in linha_dados[0]:
            linhas_finais.append([linha_dados[0], '', '', linha_dados[1], linha_dados[2]])
        elif 'Redutor' in linha_dados[0]:
            linhas_finais.append([linha_dados[0], '', '', linha_dados[1], ''])

    # Adicionar as linhas finais aos dados
    dados.extend(linhas_finais)

    # Imprimir os dados extraídos para verificar a estrutura
    for dado in dados:
        print(dado)

    if dados:
        # Converter os dados para um DataFrame do pandas
        colunas = ['Código', 'Nome', 'Tipo', 'Qtde. Teórica', 'Part. (%)']
        df = pd.DataFrame(dados, columns=colunas)

        # **Tratamento dos dados**
        df['Qtde. Teórica'] = df['Qtde. Teórica'].str.replace('.', '', regex=True)  # Remove separadores de milhar
        df['Qtde. Teórica'] = pd.to_numeric(df['Qtde. Teórica'], errors='coerce')  # Converte para float

        df['Part. (%)'] = df['Part. (%)'].str.replace(',', '.', regex=True)  # Converte vírgula decimal para ponto
        df['Part. (%)'] = pd.to_numeric(df['Part. (%)'], errors='coerce')  # Converte para float

        df['data pregão'] = pd.to_datetime(data_pregao)  # Garante que a data esteja no formato timestamp

        # Salvar o DataFrame em formato parquet com partição diária
        caminho_saida = f'{pasta_saida}/dados_{data_pregao}.parquet'
        df.to_parquet(caminho_saida, index=False)

        print("Dados extraídos e salvos localmente com sucesso!")
    else:
        print("Não foram encontrados dados com o número esperado de colunas.")

finally:
    # Fechar o driver
    driver.quit()
