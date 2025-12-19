#!/usr/bin/env bash
set -euo pipefail

CONTAINER_NAME="postgres-fastcep"
DB_NAME="cep"
DB_USER="postgres"

echo "==> Criando tabelas e indices"
python create_tables.py

echo "==> Inserindo dados de cidade..."
docker exec -i "$CONTAINER_NAME" \
  psql -U "$DB_USER" -d "$DB_NAME" < database_inserts/cidade.sql

echo "==> Inserindo dados de logradouro..."
docker exec -i "$CONTAINER_NAME" \
  psql -U "$DB_USER" -d "$DB_NAME" < database_inserts/logradouro.sql

echo "==> Ajustando sequências (cidade.id_cidade e logradouro.id_logradouro)..."
docker exec -i "$CONTAINER_NAME" \
  psql -U "$DB_USER" -d "$DB_NAME" << 'EOF'
-- Ajusta sequência de cidade.id_cidade
SELECT setval(
  pg_get_serial_sequence('cidade', 'id_cidade'),
  COALESCE((SELECT MAX(id_cidade) FROM cidade), 1),
  true
);

-- Ajusta sequência de logradouro.id_logradouro
SELECT setval(
  pg_get_serial_sequence('logradouro', 'id_logradouro'),
  COALESCE((SELECT MAX(id_logradouro) FROM logradouro), 1),
  true
);
EOF

echo "==> Finalizado com sucesso."