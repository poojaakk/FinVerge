import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # API Configuration
    API_TITLE = "FinVerge"
    API_VERSION = "1.0.0"
    
    # Gemini API
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your-api-key-here")
    
    # RAG Configuration
    KNOWLEDGE_BASE_PATH = os.getenv("KNOWLEDGE_BASE_PATH", "../knowledge-base")
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    RAG_TOP_K = 2
    
    # Matching Configuration
    PRICE_TOLERANCE_PERCENT = 5.0
    
    # File Upload Configuration
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES = [".pdf"]

settings = Settings()