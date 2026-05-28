import os
import uuid
import shutil
import logging
import json
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks, HTTPException, Depends
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from app.database import get_db
from app.config import TEMP_DIR
from app.models.department import Department
from app.models.worker import Worker
from app.models.worksession import WorkSession
from app.schemas.worksession_payload import WorkSessionPayload
from app.services.file_service import save_uploaded_picture
from app.services.pdf_service import convert_docx_to_pdf_logic, cleanup_files
from app.services.r2_service import get_file_from_r2

logger = logging.getLogger("report-backend")

router = APIRouter()

def parse_work_session_payload(raw_payload: str) -> WorkSessionPayload:
    try:
        payload = json.loads(raw_payload)
        return WorkSessionPayload.model_validate(payload)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid work session payload JSON: {str(e)}")
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())

async def persist_worker_sessions(db: AsyncSession, export_payload: WorkSessionPayload) -> None:
    form_data = export_payload.payload.get("formData", {})
    work_date = export_payload.work_date
    location = form_data.get("projectName", "").strip() or None
    company_id = form_data.get("companyId")
    if company_id == "ADD_NEW" or not company_id:
        company_id = None
    
    # 1. Process explicit workers list if provided (from the top-level array)
    seen_keys: set[tuple[str, str, str, str, str | None]] = set()
    
    for worker in export_payload.workers:
        first_name = worker.first_name.strip()
        last_name = worker.last_name.strip()
        department_name = worker.department_name.strip()
        w_location = worker.location.strip() if worker.location else location
        
        if not first_name or not department_name:
            continue
            
        dedupe_key = (
            first_name.lower(),
            last_name.lower(),
            department_name.lower(),
            worker.work_date.isoformat(),
            (w_location or "").lower() or None,
        )
        if dedupe_key in seen_keys:
            continue
        seen_keys.add(dedupe_key)
        
        await _create_worker_and_session(db, first_name, last_name, department_name, worker.work_date, w_location, company_id)

    # 2. Extract workers from formData lists (e.g. workersForeman)
    departments_map = {
        "workersForeman": "Foreman",
        "workersElectrician": "Electrician",
        "workersIT": "IT",
        "workersMason": "Mason",
        "workersWelder": "Welder",
        "workersPlumber": "Plumber",
        "workersOthers": "Others"
    }
    
    for key, dep_name in departments_map.items():
        worker_names = form_data.get(key, [])
        for w_name in worker_names:
            w_name = w_name.strip()
            if not w_name:
                continue
            
            parts = w_name.split(" ", 1)
            first_name = parts[0]
            last_name = parts[1] if len(parts) > 1 else ""
            
            await _create_worker_and_session(db, first_name, last_name, dep_name, work_date, location, company_id)

    # 3. Process photos and attach them to the hardcoded worker
    photos = form_data.get("photos", [])
    if photos:
        HARDCODED_WORKER_ID = "5e0ebe1a-3038-43c3-9458-9608d68d296c"
        from app.models.workpicture import WorkPicture
        
        hc_session = WorkSession(
            worker_id=HARDCODED_WORKER_ID,
            company_id=company_id,
            work_date=work_date,
            location=location
        )
        db.add(hc_session)
        await db.flush()
            
        for photo in photos:
            photo_url = photo.get("data")
            if photo_url and "/r2.dev/" in photo_url or photo_url:
                result = await db.execute(select(WorkPicture).filter(
                    WorkPicture.ws_id == hc_session.ws_id,
                    WorkPicture.file_url == photo_url
                ))
                existing_wp = result.scalars().first()
                
                if not existing_wp:
                    file_key = photo_url.split("/")[-1] if "/" in photo_url else "unknown"
                    wp = WorkPicture(
                        ws_id=hc_session.ws_id,
                        worker_id=HARDCODED_WORKER_ID,
                        file_url=photo_url,
                        file_key=file_key
                    )
                    db.add(wp)


async def _create_worker_and_session(db: AsyncSession, first_name: str, last_name: str, department_name: str, work_date, location: str | None, company_id: str | None = None) -> None:
    result = await db.execute(select(Department).filter(func.lower(Department.dep_name) == department_name.lower()))
    department = result.scalars().first()
    
    if not department:
        department = Department(dep_name=department_name)
        db.add(department)
        await db.flush()
        
    result = await db.execute(select(Worker).filter(
        func.lower(Worker.w_firstname) == first_name.lower(),
        func.lower(Worker.w_lastname) == last_name.lower(),
        Worker.department_id == department.d_id
    ))
    db_worker = result.scalars().first()
    
    if not db_worker:
        db_worker = Worker(
            w_firstname=first_name,
            w_lastname=last_name,
            department_id=department.d_id
        )
        db.add(db_worker)
        await db.flush()
        
    db.add(WorkSession(
        worker_id=db_worker.w_id,
        company_id=company_id,
        work_date=work_date,
        location=location
    ))
    await db.flush()


@router.post(
    "/work-sessions",
    tags=["Work Sessions"],
)
async def create_work_session(
    payload: WorkSessionPayload,
    db: AsyncSession = Depends(get_db),
):
    """Stores the report work session payload into worker tables without saving document metadata."""
    try:
        await persist_worker_sessions(db, payload)
        await db.commit()
        return {"status": "success", "message": "Work sessions persisted."}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to persist work sessions: {str(e)}")

@router.post("/upload-picture", tags=["Documents"])
async def upload_picture(
    file: UploadFile = File(...),
    ws_id: Optional[str] = Form(None),
    worker_id: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
):
    """Receives an image file, saves it, logs it in the database, and returns its public URL."""
    return await save_uploaded_picture(db, file, ws_id=ws_id, worker_id=worker_id)


@router.get("/r2-files/{file_key}", tags=["Documents"])
def get_r2_file(file_key: str):
    """Serves an uploaded R2 file through the backend so browser exports are not blocked by R2 CORS."""
    try:
        r2_object = get_file_from_r2(file_key)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

    return StreamingResponse(
        r2_object["Body"],
        media_type=r2_object.get("ContentType") or "application/octet-stream",
    )


@router.post("/convert-docx-to-pdf", tags=["Documents"])
async def convert_docx_to_pdf(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    session_payload: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """Receives a .docx file, converts it, streams the PDF, and schedules cleanup."""
    if not file.filename.endswith(".docx"):
        raise HTTPException(status_code=400, detail="Only .docx files are allowed.")

    work_session_payload = parse_work_session_payload(session_payload) if session_payload else None

    temp_id = str(uuid.uuid4())
    temp_docx_path = os.path.join(TEMP_DIR, f"in_{temp_id}.docx")

    # Save the uploaded docx
    try:
        with open(temp_docx_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        logger.error(f"Failed to save incoming temp DOCX: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to save input document: {str(e)}")

    # Attempt conversion
    try:
        pdf_path = convert_docx_to_pdf_logic(temp_docx_path, TEMP_DIR, temp_id)
        if work_session_payload:
            await persist_worker_sessions(db, work_session_payload)
            await db.commit()
    except Exception as e:
        await db.rollback()
        # Ensure temporary input file is cleaned up on error
        if os.path.exists(temp_docx_path):
            os.remove(temp_docx_path)
        raise HTTPException(status_code=500, detail=str(e))

    # Schedule deletion of both docx and pdf files after response completes
    background_tasks.add_task(cleanup_files, [temp_docx_path, pdf_path])

    # Generate downloading filename (same name but with .pdf)
    download_filename = file.filename.rsplit(".", 1)[0] + ".pdf"

    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=download_filename
    )
