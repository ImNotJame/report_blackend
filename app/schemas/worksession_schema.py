from datetime import datetime

from pydantic import BaseModel


class WorksessionRequest(BaseModel):

    worker_id: str
    work_date: datetime
    location: str

