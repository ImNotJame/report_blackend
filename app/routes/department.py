from fastapi import HTTPException
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.repositories.department_repository import department_repository
from app.schemas.department_schema import DepartmentRequest

router = APIRouter()

@router.post("/custom_add", tags=["department"])
async def custom_add_routes(data : DepartmentRequest, db: AsyncSession = Depends(get_db)):
    return await department_repository.create(db, obj_in={"dep_name": data.department_name})


@router.get("/get_id_by_name", tags=["department"])
async def get_id_by_name(name : str, db: AsyncSession = Depends(get_db)):
    result = await department_repository.get_id_by_name(db, name)
    if not result:
        raise HTTPException(status_code=404, detail="Department not found")
    return str(result)
