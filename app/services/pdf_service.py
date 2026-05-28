import os
import sys
import shutil
import subprocess
import logging
import httpx
from app.config import GOTENBERG_URL

logger = logging.getLogger("report-backend")

def is_gotenberg_available() -> bool:
    try:
        response = httpx.get(f"{GOTENBERG_URL}/health", timeout=5.0)
        return response.is_success
    except httpx.RequestError:
        return False

def find_libreoffice():
    """Locate the LibreOffice / soffice executable on the system."""
    # 1. Check typical Windows install paths
    if sys.platform == "win32":
        windows_paths = [
            r"C:\Program Files\LibreOffice\program\soffice.exe",
            r"C:\Program Files (x86)\LibreOffice\program\soffice.exe"
        ]
        for p in windows_paths:
            if os.path.exists(p):
                logger.info(f"LibreOffice found at: {p}")
                return p
                
    # 2. Check system PATH (for Linux/Mac and custom Windows installs)
    for cmd in ["soffice", "libreoffice"]:
        path = shutil.which(cmd)
        if path:
            logger.info(f"LibreOffice found in PATH: {path}")
            return path
            
    return None

def convert_docx_to_pdf_logic(docx_path: str, out_dir: str, temp_id: str) -> str:
    """Convert docx to pdf using Gotenberg API with local fallbacks."""
    expected_pdf = os.path.join(out_dir, f"in_{temp_id}.pdf")
    
    # 1. Try Gotenberg first (Extremely fast, sub-second)
    try:
        logger.info(f"Attempting conversion via Gotenberg API: {docx_path}")
        
        with open(docx_path, "rb") as f:
            files = {
                "files": (
                    os.path.basename(docx_path), 
                    f, 
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
            }
            # Gotenberg v8 uses the /forms/libreoffice/convert endpoint
            response = httpx.post(
                f"{GOTENBERG_URL}/forms/libreoffice/convert",
                files=files,
                timeout=15.0  # Safe timeout limit
            )
            
        if response.status_code == 200:
            with open(expected_pdf, "wb") as f_out:
                f_out.write(response.content)
            logger.info(f"Gotenberg conversion successful: {expected_pdf}")
            return expected_pdf
        else:
            logger.warning(f"Gotenberg service returned error {response.status_code}: {response.text}")
            
    except (httpx.RequestError, Exception) as e:
        logger.warning(f"Gotenberg API call failed or timed out: {str(e)}. Falling back to local engines...")

    # 2. Local Fallback (LibreOffice CLI Subprocess)
    libreoffice_path = find_libreoffice()
    if libreoffice_path:
        logger.info(f"Fallback: Converting using local LibreOffice: {docx_path} -> {out_dir}")
        try:
            result = subprocess.run(
                [libreoffice_path, "--headless", "--convert-to", "pdf", docx_path, "--outdir", out_dir],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            logger.info(f"Local LibreOffice fallback conversion output: {result.stdout}")
            if os.path.exists(expected_pdf):
                return expected_pdf
            else:
                raise Exception("Local LibreOffice finished but expected PDF was not created.")
        except subprocess.CalledProcessError as e:
            logger.error(f"Local LibreOffice fallback failed: {e.stderr}")
            raise Exception(f"Local LibreOffice subprocess error: {e.stderr}")

    # 3. Local Fallback (MS Word COM on Windows)
    elif sys.platform == "win32":
        logger.info("Fallback: Local LibreOffice not found. Attempting MS Word COM fallback...")
        try:
            from docx2pdf import convert
            abs_docx = os.path.abspath(docx_path)
            abs_pdf = os.path.abspath(expected_pdf)
            convert(abs_docx, abs_pdf)
            if os.path.exists(abs_pdf):
                return abs_pdf
            else:
                raise Exception("docx2pdf finished but expected PDF was not created.")
        except Exception as e:
            logger.error(f"docx2pdf fallback failed: {str(e)}")
            raise Exception(f"No conversion engine available: {str(e)}")
            
    else:
        raise Exception(
            "No conversion engine is active. Gotenberg is offline, "
            "and local LibreOffice is not installed on this server."
        )

def cleanup_files(paths: list[str]):
    """Background task to delete temporary files after streaming response is done."""
    for p in paths:
        try:
            if os.path.exists(p):
                os.remove(p)
                logger.info(f"Cleaned up temporary file: {p}")
        except Exception as e:
            logger.error(f"Failed to cleanup file {p}: {str(e)}")
