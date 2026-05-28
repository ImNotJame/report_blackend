
from typing import TYPE_CHECKING
from sqlalchemy.orm import relationship
from sqlalchemy import DateTime
from datetime import datetime
from sqlalchemy import ForeignKey
import uuid
from sqlalchemy import String
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Mapped
from app.database import Base

if TYPE_CHECKING:
    from app.models.company import Company


class CompanyLogo(Base):
    __tablename__ = "company_logo"

    cl_id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    c_id: Mapped[str] = mapped_column(String, ForeignKey("company.c_id"))
    cl_file_url: Mapped[str] = mapped_column(String, nullable=False)
    cl_file_key: Mapped[str] = mapped_column(String, nullable=False)
    cl_uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    company: Mapped["Company"] = relationship("Company", back_populates="company_logos")
    

    