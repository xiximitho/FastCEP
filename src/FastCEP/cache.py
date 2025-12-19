import json
import os
from typing import Any, Optional

import redis.asyncio as redis
from dotenv import load_dotenv
load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Pool de conexões Redis
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

async def cache_get(key: str) -> Optional[dict]:
    """Busca valor no cache"""
    try:
        value = await redis_client.get(key)
        return json.loads(value) if value else None
    except Exception as e:
        from src.FastCEP.main import logger
        logger.error("Erro no cache" + str(e))
        pass  # Não falhar se o cache estiver indisponível

async def cache_set(key: str, value: Any, ttl: int = 3600):
    """Salva valor no cache com TTL"""
    try:
        await redis_client.setex(key, ttl, json.dumps(value))
    except Exception as e:
        from src.FastCEP.main import logger
        logger.error("Erro no cache" + str(e))
        pass  # Não falhar se o cache estiver indisponível