# TechChallenge_Fase2

Esse repositório contém os códigos usados no nosso projeto para a 2º fase da pós graduação em Machine Learning Engineering na FIAP. 

## 💻 Sobre o projeto

Para este projeto construímos um pipeline de dados com processamento em lote com dados do pregão da Bovespa, utilizando serviços da AWS, que possui as seguintes etapas:

• Criamos um código em Python utilizando o Selenium para realizar um webscrapping dos dados no site da B3.

• Os dados, em formato parquet, são salvos em um Bucket do Amazon S3 com partição diária 

• Com o Lambda, configuramos um código em Python para ser executado cada vez que um novo arquivo é adicionado no bucket. Esse código aciona um crawler que cataloga os dados no AWS Glue Data Catalog e aciona também um trabalho no AWS Glue.

• O trabalho de ETL no Glue realiza algumas agregações e transformações nos dados. Os dados redefinidos são salvos em um outro bucket no S3, e também catalogados no Data Catalog.

• Os dados redefinidos estão disponíveis no Athena para realização de análises de dados e também alimentam um dashboard construído no PowerBI 📊
Nesse repositório se encontram os dois códigos que foram utilizados:

Dentro deste repositório se encontram dois códigos utilizados neste desafio:

• O código "scraping_b3.py" utiliza a biblioteca Selenium para realizar um webscraping dos dados e salvar em formato parquet, dentro de uma pasta particionada.

• O código "acionar_glue.py" dentro do pipeline é carregado em uma função lambda e toda vez que um novo arquivo é adicionado no bucket de dados brutos no Amazon S3, o código é acionado. Ele realiza o acionamento de um crawler que cataloga os dados no AWS Glue Data Catalog e aciona um trabalho do AWS Glue que realiza um processo de ETL.

## 📖 Fonte dos dados

Os dados foram obtidos através de webscraping diretamente do site 'https://sistemaswebb3-listados.b3.com.br/indexPage/day/IBOV?language=pt-br" e salvos em formato parquet.

## 🔧 Arquitetura

![image](https://github.com/user-attachments/assets/400fef20-39db-4073-b7b1-0fd9f9933a0a)

## 📁 Documentação

Mais informações sobre como construimos nosso pipeline dentro da AWS podem ser vistas na documentação que entregamos junto ao nosso pipeline: https://drive.google.com/file/d/1hY8m-AVWq_Al8orH7bavELr0GakeImEx/view?usp=drive_link
