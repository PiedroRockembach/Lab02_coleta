# Lab02 — API de Municípios (IBGE) com Flask

Aplicação Flask que consome a [API de Localidades do IBGE](https://servicodados.ibge.gov.br/api/v1/localidades/municipios), armazena os 5571 municípios brasileiros localmente em `municipios.json` e oferece CRUD e dois filtros sobre esses dados.

## Como rodar

Requer Python 3.9 ou superior.

```bash
cd Lab02_coleta

python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt

python app.py
```

A API sobe em `http://127.0.0.1:5000`.

O `municipios.json` já acompanha o projeto. Se ele for apagado, o app baixa os dados do IBGE automaticamente ao iniciar (requer internet).

**macOS:** se a porta 5000 estiver ocupada pelo Receptor AirPlay, rode em outra porta:

```bash
flask --app app run --port 5001
```

## Rotas

| Método | URL | Descrição | Sucesso | Erros |
|---|---|---|---|---|
| GET | `/` | Verifica se a API está no ar | 200 | — |
| POST | `/importacoes` | Coleta novamente os dados da API do IBGE | 201 | 502 (falha na API do IBGE) |
| GET | `/municipios` | Lista todos os municípios | 200 | — |
| GET | `/municipios/<id>` | Busca um município pelo id | 200 | 404 |
| POST | `/municipios` | Cria um município | 201 | 400 (JSON inválido ou campo faltando), 409 (id já existe) |
| PUT | `/municipios/<id>` | Substitui os dados de um município | 200 | 400, 404 |
| DELETE | `/municipios/<id>` | Remove um município | 200 | 404 |
| GET | `/estados/<uf>/municipios` | **Filtro 1:** municípios de uma UF (ex.: `SP`) | 200 | 400 (UF inválida) |
| GET | `/municipios/busca?nome=<termo>` | **Filtro 2:** busca por parte do nome, sem diferenciar acentos e maiúsculas | 200 | 400 (parâmetro ausente ou com menos de 2 letras) |

Todas as respostas, inclusive as de erro, são em JSON.

O POST exige os campos `id` (inteiro), `nome`, `microrregiao` e `regiao-imediata`. O PUT exige os mesmos campos, exceto o `id`, que vem da URL.

## Exemplos

Rotas GET podem ser abertas no navegador:

- http://127.0.0.1:5000/municipios/4314902
- http://127.0.0.1:5000/estados/RS/municipios
- http://127.0.0.1:5000/municipios/busca?nome=sao%20leo

Para POST, PUT e DELETE, use `curl` (ou Postman / Thunder Client):

```bash
# Criar
curl -i -X POST http://127.0.0.1:5000/municipios -H "Content-Type: application/json" \
  -d '{"id": 4399999, "nome": "Teste", "microrregiao": null, "regiao-imediata": null}'

# Atualizar
curl -i -X PUT http://127.0.0.1:5000/municipios/4399999 -H "Content-Type: application/json" \
  -d '{"nome": "Teste Atualizado", "microrregiao": null, "regiao-imediata": null}'

# Remover
curl -i -X DELETE http://127.0.0.1:5000/municipios/4399999

# Coletar novamente os dados do IBGE
curl -i -X POST http://127.0.0.1:5000/importacoes
```
