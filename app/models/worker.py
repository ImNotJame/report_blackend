from sqlalchemy import func, ForeignKey, String, DateTime
import uuid
from datetime import datetime
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from app.database import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.department import Department
    from app.models.worksession import WorkSession
    from app.models.workpicture import WorkPicture

class Worker(Base):
    __tablename__ = "workers"
    
    w_id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    w_firstname: Mapped[str] = mapped_column(String, nullable=False)
    w_lastname: Mapped[str] = mapped_column(String, nullable=False)
    department_id: Mapped[str] = mapped_column(ForeignKey("departments.d_id"),nullable=True)
    status: Mapped[str] = mapped_column(String, default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    department: Mapped["Department"] = relationship("Department", back_populates="workers")
    sessions: Mapped[list["WorkSession"]] = relationship("WorkSession", back_populates="worker")
    pictures: Mapped[list["WorkPicture"]] = relationship("WorkPicture", back_populates="worker")