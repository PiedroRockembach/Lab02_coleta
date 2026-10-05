import requests
import pandas as pd
import json




def importar_dados():
    url = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"
    resposta = requests.get(url)
    dados = resposta.json()
    with open("municipios.json", "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=4)

importar_dados()

   