from sqlalchemy import String, DateTime, ForeignKey, func
import uuid
from datetime import datetime
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from app.database import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.worker import Worker
    from app.models.worksession import WorkSession

class WorkPicture(Base):
    __tablename__ = "work_pictures"
    
    wp_id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    ws_id: Mapped[str] = mapped_column(ForeignKey("work_sessions.ws_id"))
    worker_id: Mapped[str] = mapped_column(ForeignKey("workers.w_id"), nullable=False)
    file_url: Mapped[str] = mapped_column(String)
    file_key: Mapped[str] = mapped_column(String)
    create_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    session: Mapped["WorkSession"] = relationship("WorkSession", back_populates="pictures")
    worker: Mapped["Worker"] = relationship("Worker", back_populates="pictures")