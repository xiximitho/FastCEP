FROM python:3.13-slim

# Definir variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.2 \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

# Adicionar poetry ao PATH
ENV PATH="$POETRY_HOME/bin:$PATH"

# Definir diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema e Poetry
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    libpq-dev \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copiar arquivos de dependências primeiro (cache do Docker)
COPY pyproject.toml poetry.lock ./

# Instalar dependências do projeto
RUN poetry install --no-root --only main

# Copiar o resto do código
COPY . /app

# Expor a porta que o FastAPI usa
EXPOSE 8000

# Comando para rodar a aplicação
CMD ["uvicorn", "FastCEP.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]