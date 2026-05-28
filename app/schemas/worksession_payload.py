from pydantic import BaseModel
from typing import List, Optional, Any, Dict
from datetime import date

class WorkerSessionCreate(BaseModel):
    first_name: str
    last_name: str = ""
    department_name: str
    work_date: date
    location: Optional[str] = None

class WorkSessionPayload(BaseModel):
    work_date: date
    payload: Dict[str, Any] = {}
    workers: List[WorkerSessionCreate] = []
