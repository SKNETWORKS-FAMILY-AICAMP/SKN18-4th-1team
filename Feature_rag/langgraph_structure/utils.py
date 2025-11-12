from langchain_openai import ChatOpenAI, OpenAIEmbeddings
import os
from psycopg2.pool import SimpleConnectionPool # 미리 DB객체 생성해놓기 
from functools import lru_cache # embedding 객체 한번만

def set_conn_str() -> str | None:
    return os.getenv("CONNECTION_STRING")

def set_openapi() -> str | None:
    """Return the OpenAI API key from the environment."""
    return os.getenv("OPENAI_API_KEY")

@lru_cache(maxsize=1)
def set_embedding_model() -> OpenAIEmbeddings:
    """Instantiate the embedding model used for vector operations."""
    return OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=set_openapi(),
    )

def model(model_name, **kwargs) -> ChatOpenAI:
    default_params = {
        "model": model_name,
        "openai_api_key": os.getenv("OPENAI_API_KEY")
    }
    default_params.update(kwargs)
    return ChatOpenAI(**default_params)

# DB Connection Pool (서버 실행 시 1번 생성 → 전체 시스템 공유)
pool = SimpleConnectionPool(
    minconn=1,
    maxconn=5,
    dsn=set_conn_str()
)

def close_pool():
    """모든 DB 연결을 안전하게 닫음"""
    try:
        pool.closeall()
    except Exception as e:
        print(f"⚠️ Connection pool close failed: {e}")