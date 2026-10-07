from flask import Flask, jsonify, request
import json
import os
import requests
import unicodedata


app = Flask(__name__)

URL_IBGE = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"

UFS = {"AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA",
       "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"}

CAMPOS_OBRIGATORIOS = ["id", "nome", "microrregiao", "regiao-imediata"]

@app.route('/')
def home():
    return jsonify({"mensagem": "API Funcionando!"}), 200

@app.route("/importacoes", methods=["POST"])
def criar_importacao():
    if not importar_dados():
        return jsonify({"erro": "Falha na comunicação com a API do IBGE. Tente novamente mais tarde."}), 502
    return jsonify({"mensagem": "Dados importados da API do IBGE",
                    "total": len(carrega_municipios())}), 201

@app.route('/municipios', methods=['GET'])
def listar_municipios():
    municipios = carrega_municipios()
    return jsonify(municipios), 200

@app.route("/municipios/<int:id>", methods=["GET"])
def buscar_municipio(id):
    for municipio in carrega_municipios():
        if municipio["id"] == id:
            return jsonify(municipio), 200
    return jsonify({"erro": "Municipio não encontrado"}), 404

@app.route("/municipios", methods=["POST"])
def adicionar_municipio():
    municipios = carrega_municipios()
    dados = request.get_json(silent=True)
    if not isinstance(dados, dict):
        return jsonify({"erro": "O corpo da requisição deve ser um JSON"}), 400
    faltando = [campo for campo in CAMPOS_OBRIGATORIOS if campo not in dados]
    if faltando:
        return jsonify({"erro": f"Campos obrigatórios ausentes: {', '.join(faltando)}"}), 400
    if not isinstance(dados["id"], int):
        return jsonify({"erro": "O campo 'id' deve ser um número inteiro"}), 400

    novo_municipio = {
        "id": dados["id"],
        "nome": dados["nome"],
        "microrregiao": dados["microrregiao"],
        "regiao-imediata": dados["regiao-imediata"]
    }
    for municipio in municipios:
        if municipio["id"] == novo_municipio["id"]:
            return jsonify({"erro": "Municipio já existe"}), 409
    municipios.append(novo_municipio)

    with open("municipios.json", "w", encoding="utf-8") as file:
        json.dump(municipios, file, ensure_ascii=False, indent=4)

    return jsonify(novo_municipio), 201

@app.route("/municipios/<int:id>", methods=["PUT"])
def atualizar_municipio(id):
    municipios = carrega_municipios()
    dados = request.get_json(silent=True)
    if not isinstance(dados, dict):
        return jsonify({"erro": "O corpo da requisição deve ser um JSON"}), 400
    faltando = [campo for campo in CAMPOS_OBRIGATORIOS if campo != "id" and campo not in dados]
    if faltando:
        return jsonify({"erro": f"Campos obrigatórios ausentes: {', '.join(faltando)}"}), 400
    municipio_encontrado = None

    for municipio in municipios:
        if municipio["id"] == id:
            municipio_encontrado = municipio
            break

    if municipio_encontrado:
        municipio_encontrado["nome"] = dados["nome"]
        municipio_encontrado["microrregiao"] = dados["microrregiao"]
        municipio_encontrado["regiao-imediata"] = dados["regiao-imediata"]

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


@app.route("/estados/<uf>/municipios", methods=["GET"])
def listar_municipios_por_uf(uf):
    uf = uf.upper()
    if uf not in UFS:
        return jsonify({"erro": f"UF inválida: {uf}"}), 400
    municipios_filtrados = []
    for municipio in carrega_municipios():
        if uf_do_municipio(municipio).get("sigla") == uf:
            municipios_filtrados.append(municipio)
    return jsonify(municipios_filtrados), 200

@app.route("/municipios/busca", methods=["GET"])
def buscar_municipios_por_nome():
    nome = request.args.get("nome")
    if nome is None:
        return jsonify({"erro": "Parâmetro 'nome' é obrigatório. Ex.: /municipios/busca?nome=porto"}), 400
    nome = nome.strip()
    if len(nome) < 2:
        return jsonify({"erro": "O parâmetro 'nome' deve ter pelo menos 2 letras"}), 400

    termo = sem_acento(nome)
    municipios_filtrados = []
    for municipio in carrega_municipios():
        if termo in sem_acento(municipio["nome"]):
            municipios_filtrados.append(municipio)
    return jsonify(municipios_filtrados), 200


@app.errorhandler(404)
def nao_encontrado(erro):
    return jsonify({"erro": "Recurso não encontrado"}), 404

@app.errorhandler(405)
def metodo_nao_permitido(erro):
    return jsonify({"erro": "Método não permitido para este recurso"}), 405


def uf_do_municipio(municipio):
    # A microrregiao vem null em alguns municípios (ex.: Boa Esperança do Norte/MT),
    # por isso a UF é lida pela regiao-imediata, que vem preenchida em todos.
    try:
        return municipio["regiao-imediata"]["regiao-intermediaria"]["UF"]
    except (KeyError, TypeError):
        return {}

def sem_acento(texto):
    texto = unicodedata.normalize("NFKD", str(texto))
    return "".join(c for c in texto if not unicodedata.combining(c)).lower()

def importar_dados():
    try:
        resposta = requests.get(URL_IBGE, timeout=30)
        resposta.raise_for_status()
        dados = resposta.json()
    except (requests.RequestException, ValueError) as erro:
        print(f"Falha ao coletar dados da API do IBGE: {erro}")
        return False
    if not isinstance(dados, list) or not dados:
        print("A API do IBGE retornou um formato inesperado.")
        return False
    with open("municipios.json", "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=4)
    return True

   
    
def carrega_municipios():
    with open("municipios.json", "r", encoding="utf-8") as file:
        return json.load(file)

if __name__ == '__main__':
    if not os.path.exists("municipios.json") and not importar_dados():
        raise SystemExit("Não foi possível obter os dados do IBGE. Tente novamente mais tarde.")
    app.run(debug=True)
    