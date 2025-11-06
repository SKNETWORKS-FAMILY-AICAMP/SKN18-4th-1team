from langchain_openai import ChatOpenAI, OpenAIEmbeddings
import os

def set_conn_str() -> str | None:
    return os.getenv("CONNECTION_STRING")

def set_openapi() -> str | None:
    """Return the OpenAI API key from the environment."""
    return os.getenv("OPENAI_API_KEY")

def set_embedding_model() -> OpenAIEmbeddings:
    """Instantiate the embedding model used for vector operations."""
    return OpenAIEmbeddings(
        model="text-embedding-3-large",
        openai_api_key=set_openapi(),
    )

def model(model_name, **kwargs) -> ChatOpenAI:
    default_params = {
        "model": model_name,
        "openai_api_key": os.getenv("OPENAI_API_KEY")
    }
    default_params.update(kwargs)
    return ChatOpenAI(**default_params)