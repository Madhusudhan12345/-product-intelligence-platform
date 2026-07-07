import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    TOP_K: int = 6
    DB_PATH: str = os.getenv("DB_PATH", "app/data/platform.db")
    FAISS_INDEX_PATH: str = os.getenv("FAISS_INDEX_PATH", "app/data/faiss.index")
    FAISS_META_PATH: str = os.getenv("FAISS_META_PATH", "app/data/faiss_meta.json")

settings = Settings()