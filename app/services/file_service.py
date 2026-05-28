from app.repositories.company_logo_repository import company_logo_repository
from app.schemas.company_logo import CompanyLogoCreate
import os
import uuid
import logging
from typing import Optional

from fastapi import UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.workpicture_repository import work_picture_repository
from app.schemas.workpicture import WorkPictureCreate
from app.services.r2_service import upload_file_to_r2

logger = logging.getLogger("report-backend")

async def save_uploaded_picture(
    db: AsyncSession,
    file: UploadFile,
    ws_id: Optional[str] = None,
    worker_id: Optional[str] = None,
) -> dict:
    """Receives an image file, uploads it to Cloudflare R2, creates a database record, and returns upload info."""
    # Ensure it's an image
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed.")
    
    # Extract extension
    ext = os.path.splitext(file.filename)[1]
    if not ext:
        ext = ".jpg"
        
    # Generate unique name
    unique_name = f"{uuid.uuid4()}{ext}"
    
    try:
        # Read the file content and stream to Cloudflare R2
        file.file.seek(0)
        file_content = file.file.read()
        url = upload_file_to_r2(file_content, unique_name, file.content_type)
    except Exception as e:
        logger.error(f"Failed to save uploaded picture to R2: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to upload image: {str(e)}")
        
    db_work_picture = None
    if ws_id:
        work_picture_in = WorkPictureCreate(
            ws_id=ws_id,
            worker_id=worker_id,
            file_url=url,
            file_key=unique_name,
        )
        db_work_picture = await work_picture_repository.create(db, obj_in=work_picture_in)
    
    logger.info(f"Successfully uploaded image to R2: {unique_name}")
    
    response = {
        "status": "success",
        "filename": unique_name,
        "url": url,
        "file_key": unique_name,
    }

    if db_work_picture:
        response["work_picture_id"] = db_work_picture.wp_id
        response["ws_id"] = db_work_picture.ws_id
        response["worker_id"] = db_work_picture.worker_id

    return response



async def save_upload_logo(db: AsyncSession, file: UploadFile, c_id: Optional[str] = None):


    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed.")


    ext = os.path.splitext(file.filename)[1]
    if not ext:
        ext = ".jpg"
        
    unique_name = f"{uuid.uuid4()}{ext}"
    
    try:
        # Read the file content and stream to Cloudflare R2
        file.file.seek(0)
        file_content = file.file.read()
        url = upload_file_to_r2(file_content, unique_name, file.content_type)
    except Exception as e:
        logger.error(f"Failed to save uploaded picture to R2: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to upload image: {str(e)}")
        


    logo_in = CompanyLogoCreate(
        c_id=c_id,
        cl_file_url=url,
        cl_file_key=unique_name,
    )

    db_logo = await company_logo_repository(db).create(logo_in)

    logger.info(f"Successfully uploaded logo to R2 and logged to DB: {unique_name} (ID: {db_logo.cl_id})")

    response = {
        "status": "success",
        "cl_id": db_logo.cl_id,
        "cl_file_url": db_logo.cl_file_url,
        "cl_file_key": db_logo.cl_file_key,
    }

    return response
