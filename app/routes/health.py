import sys
from fastapi import APIRouter
from app.config import GOTENBERG_URL
from app.services.pdf_service import find_libreoffice, is_gotenberg_available

router = APIRouter()

@router.get("/", tags=["Health"])
def health_check():
    libreoffice_status = "Available" if find_libreoffice() else "Not Available (will fallback to MS Word on Windows)"
    return {
        "status": "online",
        "gotenberg_url": GOTENBERG_URL,
        "gotenberg": "Available" if is_gotenberg_available() else "Unavailable",
        "libreoffice": libreoffice_status,
        "platform": sys.platform
    }
