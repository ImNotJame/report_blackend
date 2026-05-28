from typing import Optional

from pydantic import BaseModel

class WorkerRequest(BaseModel):

    w_firstname: str
    w_lastname: str
    department_id: Optional[str] = None


class WorkerRequestAll(BaseModel):
    department_id: str



class WorekrResponse(BaseModel):
    w_firstname: str
    w_lastname: str