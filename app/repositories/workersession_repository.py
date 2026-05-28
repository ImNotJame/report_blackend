from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.worksession import WorkSession
from app.repositories.base import BaseRepository


class WorkSessionRepository(BaseRepository[WorkSession]):
    async def get_by_uuid(self, db: AsyncSession, uuid: str) -> Optional[WorkSession]:
        result = await db.execute(select(WorkSession).filter(WorkSession.ws_id == uuid))
        return result.scalars().first()

    async def custom_add(self, db: AsyncSession, worksession: WorkSession):
        db.add(worksession)
        await db.commit()
        await db.refresh(worksession)
        return worksession

worksession_repository = WorkSessionRepository