FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pipenv

COPY Pipfile Pipfile.lock ./

# Para produção, use --deploy para garantir consistência
RUN pipenv install --system --deploy --ignore-pipfile

COPY . .

EXPOSE 8000


# Comando para rodar a aplicação
CMD ["uvicorn", "FastCEP.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]