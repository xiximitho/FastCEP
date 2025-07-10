# FastCEP

FastCEP é uma API para consulta de endereços a partir de CEPs, utilizando uma base de dados local e integração com serviços externos para complementar informações.

## Pré-requisitos

- Python >= 3.13
- [Poetry](https://python-poetry.org/)

## Configuração do Banco de Dados

Os dados iniciais de cidades e logradouros foram obtidos a partir do repositório [devmediadev/SQL-BANCO-CEP-Cidades-Logradouros](https://github.com/devmediadev/SQL-BANCO-CEP-Cidades-Logradouros).

1. Extraia os arquivos de inserção:

   ```shell
   cd database_inserts && unzip inserts.zip
   ```
2. Popule a base inicial:

    ```shell
    sqlite3 ceps.db < database_inserts/cidade.sql
    sqlite3 ceps.db < database_inserts/logradouro.sql
    ```


## Instalação e Execução.

1. Instale as dependências do projeto:

    ```shell
    poetry install
    ```
2. Inicie a aplicação:
    ```shell
    poetry run uvicorn FastCEP.main:app --reload
    ```

## Exemplos de Uso

### Consulta de CEP existente na base local
```shell
curl http://127.0.0.1:8000/cep/01001-001
```
Resposta:
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
### Consulta de CEP não existente na base (busca em serviço externo)

```shell
curl http://127.0.0.1:8000/cep/88201-306
```
Resposta:

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

## Observações
* O banco de dados inicial é populado apenas com os dados fornecidos pelo repositório citado.

* Caso o CEP consultado não seja encontrado localmente, a API realiza a busca em serviços externos (ViaCEP) e retorna as informações disponíveis.

## Licença
Consulte o arquivo LICENSE para mais informações.