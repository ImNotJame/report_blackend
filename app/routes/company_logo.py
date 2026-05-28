from fastapi.responses import RedirectResponse
from fastapi import HTTPException
from app.repositories.company_logo_repository import company_logo_repository
from fastapi import UploadFile, File, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter
from app.database import get_db
from app.services.file_service import save_upload_logo


router = APIRouter()


@router.post("/company_logo", tags=["company_logo"])
async def create_company_logo(
    c_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    return await save_upload_logo(db, file, c_id)


@router.get("/get_logo/{c_id}", tags=["company_logo"])
async def get_company_logo(c_id: str, db: AsyncSession = Depends(get_db)):
    logo_record = await company_logo_repository(db).get_by_company_id(c_id)
    
    if not logo_record or not logo_record.cl_file_key:
        # This explicitly handles the 404 if the DB has no record
        raise HTTPException(status_code=404, detail="Logo not found")
        
    try:
        from app.services.r2_service import get_file_from_r2
        from fastapi.responses import StreamingResponse
        
        r2_object = get_file_from_r2(logo_record.cl_file_key)
        return StreamingResponse(
            r2_object["Body"],
            media_type=r2_object.get("ContentType") or "application/octet-stream",
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Image fetch failed: {str(e)}")