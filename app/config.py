import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration settings"""
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyCOlhqh86AoIzfWL6SRguEO1nnE96whNlk")
    LLM_MODEL = os.getenv("LLM_MODEL", "gemini-1.5-flash")
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.1"))
    CHROMA_PERSIST_DIRECTORY = os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_db")
    CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "invoice_documents")
    MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
