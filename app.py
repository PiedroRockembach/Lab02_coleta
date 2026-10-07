from flask import Flask, jsonify, request
import json
import os
import requests
import pandas as pd


app = Flask(__name__)

@app.route('/')
def home():
    return "API Funcionando!"

@app.route('/municipios', methods=['GET'])
def listar_municipios():
    municipios = carrega_municipios()
    return jsonify(municipios), 200

@app.route("/municipios", methods=["POST"])
def adicionar_municipio():
    municipios = carrega_municipios()
    dados = request.json

    novo_municipio = {
        "id": dados["id"],
        "nome": dados["nome"],
        "microrregiao": dados["microrregiao"],
        "regiao-imediata": dados["regiao-imediata"]
    }
    for municipio in municipios:
        if municipio["id"] == novo_municipio["id"]:
            return jsonify({"erro": "Municipio já existe"}), 400
    municipios.append(novo_municipio)

    with open("municipios.json", "w", encoding="utf-8") as file:
        json.dump(municipios, file, ensure_ascii=False, indent=4)

    return jsonify(novo_municipio), 201

@app.route("/municipios/<int:id>", methods=["PUT"])
def atualizar_municipio(id):
    municipios = carrega_municipios()
    dados = request.json
    municipio_encontrado = None

    for municipio in municipios:
        if municipio["id"] == id:
            municipio_encontrado = municipio
            break

    if municipio_encontrado:
        municipio_encontrado["nome"] = dados.get("nome", municipio_encontrado["nome"])
        municipio_encontrado["microrregiao"] = dados.get("microrregiao", municipio_encontrado["microrregiao"])
        municipio_encontrado["regiao-imediata"] = dados.get("regiao-imediata", municipio_encontrado["regiao-imediata"])

        with open("municipios.json", "w", encoding="utf-8") as file:
            json.dump(municipios, file, ensure_ascii=False, indent=4)

        return jsonify(municipio_encontrado), 200
    
    return jsonify({"erro": "Municipio não encontrado"}), 404

@app.route("/municipios/<int:id>", methods=["DELETE"])
def deletar_municipio(id):
    municipios = carrega_municipios()
    municipio_encontrado = None

    for municipio in municipios:
        if municipio["id"] == id:
            municipio_encontrado = municipio
            break

    if municipio_encontrado:
        municipios.remove(municipio_encontrado)
        with open("municipios.json", "w", encoding="utf-8") as file:
            json.dump(municipios, file, ensure_ascii=False, indent=4)
        return jsonify({"mensagem": "Municipio deletado com sucesso"}), 200
    
    return jsonify({"erro": "Municipio não encontrado"}), 404


@app.route("/municipios/<str:uf>", methods=["GET"])
def listar_municipios_por_uf(uf):
    municipios = carrega_municipios()
    municipios_filtrados = []
    for municipio in municipios:
        if municipio["microrregiao"]["mesorregiao"]["UF"]["sigla"].lower() == uf.lower():
            municipios_filtrados.append(municipio)

    if municipios_filtrados:
        return jsonify(municipios_filtrados), 200
    
    return jsonify({"erro": "Nenhum municipio encontrado para a UF especificada"}), 404 

@app.route("/municipios/<str:estado>", methods=["GET"])
def listar_municipios_por_estado(estado):
    municipios = carrega_municipios()
    municipios_filtrados = []
    for municipio in municipios:
        if municipio["microrregiao"]["mesorregiao"]["UF"]["nome"].lower() == estado.lower():
            municipios_filtrados.append(municipio)

    if municipios_filtrados:
        return jsonify(municipios_filtrados), 200
    
    return jsonify({"erro": "Nenhum municipio encontrado para o estado especificado"}), 404


def importar_dados():
    url = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"
    resposta = requests.get(url)
    dados = resposta.json()
    with open("municipios.json", "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=4)

   
    
def carrega_municipios():
    with open("municipios.json", "r", encoding="utf-8") as file:
        return json.load(file)

if __name__ == '__main__':
    if not os.path.exists("municipios.json"):
        importar_dados()
    app.run(debug=True)
    