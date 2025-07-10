Para popular a base de dados.
### DB Inicial

para criar o db inicial, rode
```shell
cd database_inserts && unzip inserts.zip
```
E após, para executar os arquivos SQL.

```shell
sqlite3 ceps.db < database_inserts/cidade.sql && sqlite3 ceps.db < database_inserts/logradouro.sql
```


poetry install
poetry run uvicorn FastCEP.main:app --reload


```shell
#Consultando um cep antigo e já existente.
curl http://127.0.0.1:8000/cep/01001-001
```
```json
{
    "cep": "01001001",
    "logradouro": "Praça da Sé",
    "bairro": "Sé",
    "cidade": "São Paulo",
    "uf": "SP",
    "complemento": "- lado par",
    "codigo_ibge": 3550308,
    "ddd": "11",
    "fonte_informacao": "Local"
}
```

```shell
#Consultando um cep novo e não existente na base.
curl http://127.0.0.1:8000/cep/88201-306
```
```json
{
    "cep": "88201306",
    "logradouro": "Avenida Araucária",
    "bairro": "Areias",
    "cidade": "Tijucas",
    "uf": "SC",
    "complemento": "até 99999 - lado ímpar",
    "codigo_ibge": 4218004,
    "ddd": "48",
    "fonte_informacao": "ViaCEP"
}
```