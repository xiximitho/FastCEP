import requests
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from .database import engine, get_db
from .models import Base

# Criar tabelas
Base.metadata.create_all(bind=engine)

app = FastAPI(title="CEP API", version="1.0.0")


from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from .database import get_db
from .models import Cidade, Logradouro

app = FastAPI()


@app.get("/cep/{cep}")
def consultar_cep(cep: str, db: Session = Depends(get_db)):

    cep = cep.replace("-", "").replace(".", "").strip()

    logradouro = db.query(Logradouro).filter(Logradouro.CEP == cep).first()
    if logradouro:
        print("Logradouro encontrado na base de dados local")
        cidade = (
            db.query(Cidade).filter(Cidade.id_cidade == logradouro.id_cidade).first()
        )
        return {
            "cep": logradouro.CEP,
            "logradouro": logradouro.descricao,
            "tipo": logradouro.tipo,
            "bairro": logradouro.descricao_bairro,
            "cidade": logradouro.descricao_cidade
            or (cidade.descricao if cidade else None),
            "uf": logradouro.UF,
            "complemento": logradouro.complemento,
            "codigo_ibge": logradouro.codigo_cidade_ibge
            or (cidade.codigo_ibge if cidade else None),
            "ddd": cidade.ddd if cidade else None,
            "fonte_informacao": logradouro.fonte_informacao,
        }

    # Fallback: consulta no ViaCEP
    viacep_resp = requests.get(f"https://viacep.com.br/ws/{cep}/json/").json()
    if "erro" in viacep_resp:
        raise HTTPException(status_code=404, detail="CEP não encontrado")

    print("Logradouro não encontrado na base de dados local, consultando ViaCEP")

    # Verifica se a cidade já existe
    cidade = (
        db.query(Cidade)
        .filter(
            Cidade.descricao == viacep_resp.get("localidade"),
            Cidade.uf == viacep_resp.get("uf"),
        )
        .first()
    )

    if not cidade:
        cidade = Cidade(
            descricao=viacep_resp.get("localidade"),
            uf=viacep_resp.get("uf"),
            codigo_ibge=viacep_resp.get("ibge"),
            ddd=viacep_resp.get("ddd"),
        )
        db.add(cidade)
        db.commit()
        db.refresh(cidade)

    # Insere o logradouro
    novo_logradouro = Logradouro(
        CEP=viacep_resp.get("cep", "").replace("-", ""),
        tipo=None,  # ViaCEP não retorna tipo separado
        descricao=viacep_resp.get("logradouro"),
        id_cidade=cidade.id_cidade,
        UF=viacep_resp.get("uf"),
        complemento=viacep_resp.get("complemento"),
        descricao_sem_numero=viacep_resp.get("logradouro"),
        descricao_cidade=viacep_resp.get("localidade"),
        codigo_cidade_ibge=viacep_resp.get("ibge"),
        descricao_bairro=viacep_resp.get("bairro"),
        fonte_informacao="ViaCEP",
    )
    db.add(novo_logradouro)
    db.commit()

    # Retorna o mesmo padrão de resposta
    return {
        "cep": viacep_resp.get("cep"),
        "logradouro": viacep_resp.get("logradouro"),
        "tipo": None,
        "bairro": viacep_resp.get("bairro"),
        "cidade": viacep_resp.get("localidade"),
        "uf": viacep_resp.get("uf"),
        "complemento": viacep_resp.get("complemento"),
        "codigo_ibge": viacep_resp.get("ibge"),
        "ddd": viacep_resp.get("ddd"),
        "fonte_informacao": "ViaCEP",
    }


@app.get("/")
def root():
    return {"message": "CEP API funcionando!"}
