from dotenv import load_dotenv
from sqlalchemy import Column, Integer, String, create_engine, pool
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

load_dotenv()
# PostgreSQL connection string
# Formato: postgresql://usuario:senha@host:porta/nome_do_banco
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5440/cep"
)

engine = create_engine(
    DATABASE_URL,
    poolclass=pool.QueuePool,
    pool_size=20,              # Conexões permanentes
    max_overflow=40,           # Conexões extras sob demanda
    pool_pre_ping=True,        # Verifica conexões antes de usar
    pool_recycle=1800,         # Recicla conexões a cada 30m
    echo=False,                # Desabilitar logs SQL em produção
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()