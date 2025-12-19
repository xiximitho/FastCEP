from sqlalchemy import Column, ForeignKey, Integer, String, Index
from sqlalchemy.orm import relationship

from .database import Base


class Cidade(Base):
    __tablename__ = "cidade"

    id_cidade = Column("id_cidade", Integer, primary_key=True, index=True)
    descricao = Column("descricao", String(100))
    uf = Column("uf", String(2))
    codigo_ibge = Column("codigo_ibge", Integer)
    ddd = Column("ddd", String(2))

    logradouros = relationship("Logradouro", back_populates="cidade")

    __table_args__ = (
        # mesmo nome do índice que você usaria no SQL
        Index("idx_cidade_uf", "id_cidade", "uf"),
        Index("idx_cidade_estado", "uf"),
    )


class Logradouro(Base):
    __tablename__ = "logradouro"

    id_logradouro = Column("id_logradouro", Integer, primary_key=True, index=True)
    # coluna física "CEP", atributo Python "cep"
    cep = Column("cep", String(11), index=True)
    tipo = Column("tipo", String(50))
    descricao = Column("descricao", String(100))
    id_cidade = Column("id_cidade", Integer, ForeignKey("cidade.id_cidade"))
    uf = Column("uf", String(2))
    complemento = Column("complemento", String(100))
    descricao_sem_numero = Column("descricao_sem_numero", String(100))
    descricao_cidade = Column("descricao_cidade", String(100))
    codigo_cidade_ibge = Column("codigo_cidade_ibge", Integer)
    descricao_bairro = Column("descricao_bairro", String(100))
    fonte_informacao = Column(
        "fonte_informacao",
        String(50),
        default="Base de dados local",
    )

    cidade = relationship("Cidade", back_populates="logradouros")

    __table_args__ = (
        Index("idx_logradouro_cep", "cep"),  # usa a *key* da coluna (atributo Python)
        Index("idx_logradouro_cidade", "id_cidade", "uf"),
    )