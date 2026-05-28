from app.repositories.base import BaseRepository
from app.models.department import Department
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

import uuid

class DepartmentRepository(BaseRepository[Department]):

    async def get_by_uuid(self, db: AsyncSession, uuid: str):
        result = await db.execute(select(self.model).filter(self.model.d_id == uuid))
        return result.scalars().first()


    async def get_id_by_name(self, db: AsyncSession, name: str):
        result = await db.execute(select(self.model.d_id).filter(func.lower(self.model.dep_name) == name.lower()))
        return result.scalars().first()


department_repository = DepartmentRepository(Department)