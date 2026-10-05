from flask import Flask, jsonify, request
import json

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




    
def carrega_municipios():
    with open("municipios.json", "r", encoding="utf-8") as file:
        return json.load(file)

if __name__ == '__main__':
    app.run(debug=True)
    