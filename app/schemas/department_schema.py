from pydantic import BaseModel

class DepartmentRequest(BaseModel):

    department_name: str


class DepartmentResponse(BaseModel):
    d_id: str
    dep_name: str