from app.schemas.company_schema import CompanyRequest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.company import Company


class CompanyRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self):
        result = await self.db.execute(select(Company))
        return list(result.scalars().all())


    async def get_by_id(self, id: str):
        result = await self.db.execute(select(Company).filter(Company.c_id == id))
        return result.scalars().first()
    
    async def create(self, db: AsyncSession, company: CompanyRequest):
        # using model_dump() for pydantic v2
        newCompany = Company(**company.model_dump() if hasattr(company, 'model_dump') else company.dict())
        db.add(newCompany)
        await db.commit()
        await db.refresh(newCompany)
        return newCompany