



from sqlalchemy.orm import relationship
from sqlalchemy import DateTime
from datetime import datetime
from sqlalchemy.orm import mapped_column
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from app.database import Base
import uuid
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.company_logo import CompanyLogo
    from app.models.worksession import WorkSession


class Company(Base):


    __tablename__ = "company"


    c_id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    c_name: Mapped[str] = mapped_column(String, nullable=False)
    c_created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


    sessions: Mapped[list["WorkSession"]] = relationship("WorkSession", back_populates="company")
    company_logos: Mapped["CompanyLogo"] = relationship("CompanyLogo", back_populates="company")