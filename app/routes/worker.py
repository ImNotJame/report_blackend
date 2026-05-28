from fastapi import HTTPException
from app.schemas.worker_schema import WorkerRequestAll
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.testing.plugin.plugin_base import post

from app.database import get_db
from app.models import Worker
from app.repositories.worker_repository import worker_repository
from app.schemas.worker_schema import WorkerRequest

router = APIRouter()



@router.post("/add_worker", tags=["Worker"])
async def add_worker(data: WorkerRequest, db: AsyncSession = Depends(get_db)):
    worker = Worker(**data.model_dump())
    return await worker_repository.custom_add(db, worker)



from fastapi import Query
@router.get("/get_all_by_department_id", tags=["Worker"])
async def get_all_by_department_id(data: str = Query(...), db: AsyncSession = Depends(get_db)):
    result = await worker_repository.get_all_by_department_id(db, data)
    if not result:
        return [] # Return empty list if no workers exist yet
        
    # Return a clean list of dictionaries that the frontend can use
    return [{"w_id": w.w_id, "w_firstname": w.w_firstname, "w_lastname": w.w_lastname} for w in result]
