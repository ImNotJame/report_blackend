from sqlalchemy.orm import relationship
import uuid
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import String, DateTime
from datetime import datetime
from app.database import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.worker import Worker

class Department(Base):
    __tablename__ = "departments"

    d_id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    dep_name: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    workers: Mapped[list["Worker"]] = relationship("Worker", back_populates="department")