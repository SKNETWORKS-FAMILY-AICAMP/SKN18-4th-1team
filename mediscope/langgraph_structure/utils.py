from langchain_openai import ChatOpenAI, OpenAIEmbeddings
import os
from dotenv import load_dotenv
load_dotenv()
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


# ========================================
# 🔧 DB Connection Pool (Singleton)
# ========================================
class DBPoolManager(metaclass=type):
    """
    Singleton: DB 연결 풀 관리
    - Pool 생성/정리 통합 관리
    - 모든 모듈에서 공유
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.pool = SimpleConnectionPool(
                minconn=1,
                maxconn=5,
                dsn=set_conn_str()
            )
        return cls._instance
    
    def get_connection(self):
        """Pool에서 연결 획득"""
        return self.pool.getconn()
    
    def return_connection(self, conn):
        """연결을 Pool에 반환"""
        try:
            self.pool.putconn(conn)
        except Exception as e:
            print(f"⚠️ Failed to return connection: {e}")
    
    def close_all(self):
        """모든 연결 정리"""
        try:
            self.pool.closeall()
        except Exception as e:
            print(f"⚠️ Connection pool close failed: {e}")


# ========================================
# 🗄️ 전역 Pool 객체
# ========================================
_pool_manager = DBPoolManager()
pool = _pool_manager.pool  # 기존 코드 호환성

def close_pool():
    """모든 DB 연결을 안전하게 닫음"""
    _pool_manager.close_all()
