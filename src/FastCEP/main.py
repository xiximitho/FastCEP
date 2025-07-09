from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from .database import engine, get_db
from .models import CEP, Base

# Criar tabelas
Base.metadata.create_all(bind=engine)

app = FastAPI(title="CEP API", version="1.0.0")


@app.get("/cep/{cep}")
def consultar_cep(cep: str, db: Session = Depends(get_db)):

    cep_data = db.query(CEP).filter(CEP.cep == cep).first()
    if not cep_data:
        raise HTTPException(status_code=404, detail="CEP não encontrado")
    return cep_data


@app.get("/")
def root():
    return {"message": "CEP API funcionando!"}
