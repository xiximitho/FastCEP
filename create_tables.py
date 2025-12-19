from src.FastCEP.database import engine, Base
from src.FastCEP.models import Cidade, Logradouro
# Isso cria todas as tabelas definidas nos models
Base.metadata.create_all(bind=engine)

print("✅ Tabelas criadas com sucesso!")