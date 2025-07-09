Para popular a base de dados.
### DB Inicial
para criar o db inicial, rode
````shell
sqlite3 ceps.db < database_inserts/cidade.sql && sqlite3 ceps.db < database_inserts/logradouro.sql
```


poetry install
poetry run uvicorn FastCEP.main:app --reload
