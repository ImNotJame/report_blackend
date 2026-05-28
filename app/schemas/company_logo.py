





from pydantic import ConfigDict
from datetime import datetime
from pydantic import BaseModel


class CompanyLogoBase(BaseModel):
    c_id: str
    cl_file_url: str
    cl_file_key: str

class CompanyLogoCreate(CompanyLogoBase):
    pass


class CompanyLogoResponse(CompanyLogoBase):
    cl_id: str
    cl_uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)