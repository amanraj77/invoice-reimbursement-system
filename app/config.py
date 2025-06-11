import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyCOlhqh86AoIzfWL6SRguEO1nnE96whNlk")
    LLM_MODEL = os.getenv("LLM_MODEL", "gemini-1.5-flash")
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.1"))
    
    # Simplified for production
    CHROMA_PERSIST_DIRECTORY = os.getenv("CHROMA_PERSIST_DIRECTORY", "/app/data")
    CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "invoice_documents")
    MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "25"))  # Reduced for free tier
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Production settings
    ENVIRONMENT = os.getenv("ENVIRONMENT", "production")
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
