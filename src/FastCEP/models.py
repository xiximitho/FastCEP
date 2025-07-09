from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base


class Cidade(Base):
    __tablename__ = "cidade"
    id_cidade = Column(Integer, primary_key=True, index=True)
    descricao = Column(String(100))
    uf = Column(String(2))
    codigo_ibge = Column(Integer)
    ddd = Column(String(2))
    logradouros = relationship("Logradouro", back_populates="cidade")


class Logradouro(Base):
    __tablename__ = "logradouro"
    id_logradouro = Column(Integer, primary_key=True, index=True)
    CEP = Column(String(11), index=True)
    tipo = Column(String(50))
    descricao = Column(String(100))
    id_cidade = Column(Integer, ForeignKey("cidade.id_cidade"))
    UF = Column(String(2))
    complemento = Column(String(100))
    descricao_sem_numero = Column(String(100))
    descricao_cidade = Column(String(100))
    codigo_cidade_ibge = Column(Integer)
    descricao_bairro = Column(String(100))
    cidade = relationship("Cidade", back_populates="logradouros")
    fonte_informacao = Column(String(50), default="Base de dados local")
