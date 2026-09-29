import requests
import pandas as pd


url = "https://servicodados.ibge.gov.br/api/v1/localidades/estados/35/municipios"

resposta = requests.get(url)

print(resposta.status_code)
dados = resposta.json()

print(type(dados))
print(len(dados))