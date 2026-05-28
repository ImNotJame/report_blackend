from sqlalchemy import Date, ForeignKey, func, String, DateTime
import uuid
from datetime import datetime
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from app.database import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.worker import Worker
    from app.models.workpicture import WorkPicture
    from app.models.company import Company

class WorkSession(Base):
    __tablename__ = "work_sessions"
    
    ws_id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    worker_id: Mapped[str] = mapped_column(ForeignKey("workers.w_id"))
    company_id: Mapped[str] = mapped_column(ForeignKey("company.c_id"), nullable=True)
    work_date: Mapped[datetime] = mapped_column(Date, nullable=False)
    location: Mapped[str] = mapped_column(String)
    create_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    worker: Mapped["Worker"] = relationship("Worker", back_populates="sessions")
    pictures: Mapped[list["WorkPicture"]] = relationship("WorkPicture", back_populates="session")
    company: Mapped["Company"] = relationship("Company", back_populates="sessions")