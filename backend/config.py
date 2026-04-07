import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# Storage paths
DATA_DIR = os.getenv("DATA_DIR", "./data")
MODELS_DIR = os.getenv("MODELS_DIR", "./models")
FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "./data/faiss.index")
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./data/chroma")
SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", "./data/talking.db")
REPORTS_DIR = os.getenv("REPORTS_DIR", "./data/reports")

# App config
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "100"))
MAX_ROWS_ML = int(os.getenv("MAX_ROWS_ML", "500000"))
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(os.path.dirname(FAISS_INDEX_PATH), exist_ok=True)
os.makedirs(CHROMA_DB_PATH, exist_ok=True)
