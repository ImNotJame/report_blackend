from app.database import get_db
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter
from app.schemas.company_schema import CompanyRequest, CompanyResponse
from app.repositories.company_repository import CompanyRepository
from typing import List

router = APIRouter()

@router.post("/add_company",tags=["company"], response_model=CompanyResponse)
async def create_company(company: CompanyRequest, db: AsyncSession = Depends(get_db)):
    return await CompanyRepository(db).create(db,company)

@router.get("/companies",tags=["company"], response_model=List[CompanyResponse])
async def get_companies(db: AsyncSession = Depends(get_db)):
    return await CompanyRepository(db).get_all()