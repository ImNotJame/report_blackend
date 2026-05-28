import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.worker import Worker
from app.repositories.base import BaseRepository

class WorkerRepository(BaseRepository[Worker]):

    async def get_by_uuid(self, db: AsyncSession, uuid: str):
        result = await db.execute(select(self.model).filter(self.model.w_id == uuid))
        return result.scalars().first()

    async def custom_add(self, db: AsyncSession, worker: Worker):
        db.add(worker)
        await db.commit()
        return worker

    async def update(self, db: AsyncSession, worker: Worker):
        result = await db.execute(select(self.model).filter(self.model.w_id == worker.w_id))
        db_worker = result.scalars().first()
        if not db_worker:
            return None

        db_worker.w_firstname = worker.w_firstname
        db_worker.w_lastname = worker.w_lastname

        await db.commit()
        await db.refresh(db_worker)
        return db_worker

    async def get_all_workers(self, db: AsyncSession):
        result = await db.execute(select(self.model))
        return list(result.scalars().all())

    async def get_all_by_department_id(self, db: AsyncSession, dep_id: str):
        result = await db.execute(select(self.model).filter(self.model.department_id == dep_id))
        return list(result.scalars().all())

worker_repository = WorkerRepository(Worker)