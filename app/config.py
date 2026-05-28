import os
from dotenv import load_dotenv

# Base directory is the project root (parent of app/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load .env file
dotenv_path = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path=dotenv_path)

GOTENBERG_URL = os.getenv("GOTENBERG_URL", "http://localhost:3010")
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "http://localhost:8000").rstrip("/")

# Database settings
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./database.db")

# Cloudflare R2 settings
R2_ENDPOINT = os.getenv("R2_ENDPOINT")
R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
R2_BUCKET_NAME = os.getenv("R2_BUCKET_NAME")
R2_PUBLIC_URL = os.getenv("R2_PUBLIC_URL", "").rstrip("/")

# Folder directory settings
UPLOAD_DIR = os.path.join(BASE_DIR, "static", "uploads")
TEMP_DIR = os.path.join(BASE_DIR, "temp_convert")

# Ensure required directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)
