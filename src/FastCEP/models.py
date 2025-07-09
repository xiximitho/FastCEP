from sqlalchemy import Column, String

from .database import Base


class CEP(Base):
    __tablename__ = "ceps"

    cep = Column(String, primary_key=True, index=True)
    logradouro = Column(String)
    bairro = Column(String)
    cidade = Column(String)
    uf = Column(String)
