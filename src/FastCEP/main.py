import logging
from contextlib import asynccontextmanager

import httpx
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import ORJSONResponse
from sqlalchemy.orm import Session, joinedload

from .cache import cache_get, cache_set
from .database import get_db
from .models import Cidade, Logradouro

load_dotenv()
# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

http_client = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação"""
    global http_client
    # Startup: criar cliente HTTP
    http_client = httpx.AsyncClient(
        timeout=10.0,
        limits=httpx.Limits(max_keepalive_connections=20, max_connections=100),
    )
    logger.info("FastCEP API iniciada")
    yield
    # Shutdown: fechar cliente HTTP
    await http_client.aclose()
    logger.info("FastCEP API encerrada")


app = FastAPI(
    title="FastCEP API",
    version="2.0.0",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)


@app.get("/")
async def root():
    return {"message": "FastCEP API funcionando!", "version": "2.0.0"}


@app.get("/health")
async def health_check():
    """Endpoint para health check (útil para load balancers)"""
    return {"status": "healthy"}


@app.get("/cep/{cep}")
async def consultar_cep(cep: str, db: Session = Depends(get_db)):
    # Normalizar CEP
    cep_limpo = cep.replace("-", "").replace(".", "").strip()

    # Validação básica
    if not cep_limpo.isdigit() or len(cep_limpo) != 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CEP inválido. Deve conter 8 dígitos.",
        )

    # 1. Tentar cache primeiro (Redis)
    cached = await cache_get(f"cep:{cep_limpo}")
    if cached:
        logger.info(f"CEP {cep_limpo} encontrado no cache")
        return cached

    # 2. Buscar no banco com JOIN (1 query ao invés de 2)
    logradouro = (
        db.query(Logradouro)
        .options(joinedload(Logradouro.cidade))  # Eager loading
        .filter(Logradouro.cep == cep_limpo)
        .first()
    )

    if logradouro:
        logger.info(f"CEP {cep_limpo} encontrado no banco local")
        cidade = logradouro.cidade

        response = {
            "cep": logradouro.cep,
            "logradouro": logradouro.descricao,
            "bairro": logradouro.descricao_bairro,
            "cidade": logradouro.descricao_cidade or (cidade.descricao if cidade else None),
            "uf": logradouro.uf,
            "complemento": logradouro.complemento,
            "codigo_ibge": logradouro.codigo_cidade_ibge or (cidade.codigo_ibge if cidade else None),
            "ddd": cidade.ddd if cidade else None,
            "fonte_informacao": logradouro.fonte_informacao,
        }

        # Cachear por 24 horas
        await cache_set(f"cep:{cep_limpo}", response, ttl=86400)
        return response

    # 3. Fallback: consulta assíncrona no ViaCEP
    logger.info(f"CEP {cep_limpo} não encontrado localmente, consultando ViaCEP")

    try:
        viacep_resp = await http_client.get(f"https://viacep.com.br/ws/{cep_limpo}/json/")
        viacep_resp.raise_for_status()
        viacep_data = viacep_resp.json()
    except httpx.HTTPError as e:
        logger.error(f"Erro ao consultar ViaCEP: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço de CEP temporariamente indisponível",
        )

    if "erro" in viacep_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CEP não encontrado",
        )

    # 4. Salvar no banco (de forma otimizada)
    try:
        # Buscar ou criar cidade
        cidade = (
            db.query(Cidade)
            .filter(
                Cidade.descricao == viacep_data.get("localidade"),
                Cidade.uf == viacep_data.get("uf"),
            )
            .first()
        )

        if not cidade:
            cidade = Cidade(
                descricao=viacep_data.get("localidade"),
                uf=viacep_data.get("uf"),
                codigo_ibge=viacep_data.get("ibge"),
                ddd=viacep_data.get("ddd"),
            )
            db.add(cidade)
            db.flush()

        # Inserir logradouro
        novo_logradouro = Logradouro(
            cep=viacep_data.get("cep", "").replace("-", ""),
            descricao=viacep_data.get("logradouro"),
            id_cidade=cidade.id_cidade,
            uf=viacep_data.get("uf"),
            complemento=viacep_data.get("complemento"),
            descricao_sem_numero=viacep_data.get("logradouro"),
            descricao_cidade=viacep_data.get("localidade"),
            codigo_cidade_ibge=viacep_data.get("ibge"),
            descricao_bairro=viacep_data.get("bairro"),
            fonte_informacao="ViaCEP",
        )
        db.add(novo_logradouro)
        db.commit()

    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao salvar CEP no banco: {e}")
        # Não falhar a requisição se o salvamento falhar

    response = {
        "cep": viacep_data.get("cep"),
        "logradouro": viacep_data.get("logradouro"),
        "bairro": viacep_data.get("bairro"),
        "cidade": viacep_data.get("localidade"),
        "uf": viacep_data.get("uf"),
        "complemento": viacep_data.get("complemento"),
        "codigo_ibge": viacep_data.get("ibge"),
        "ddd": viacep_data.get("ddd"),
        "fonte_informacao": "ViaCEP",
    }

    # Cachear
    await cache_set(f"cep:{cep_limpo}", response, ttl=86400)
    return response
