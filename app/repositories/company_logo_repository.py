









from app.schemas.company_logo import CompanyLogoCreate
from app.models import CompanyLogo
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


class company_logo_repository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self):
        result = await self.db.execute(select(CompanyLogo))
        return list(result.scalars().all())

    async def get_by_id(self, id: str):
        result = await self.db.execute(select(CompanyLogo).filter(CompanyLogo.cl_id == id))
        return result.scalars().first()

    async def create(self, company_logo: CompanyLogoCreate):
        newCompanyLogo = CompanyLogo(**company_logo.model_dump())
        self.db.add(newCompanyLogo)
        await self.db.commit()
        await self.db.refresh(newCompanyLogo)
        return newCompanyLogo

    async def get_by_company_id(self, c_id: str):
        result = await self.db.execute(select(CompanyLogo).filter(CompanyLogo.c_id == c_id))
        return result.scalars().first()