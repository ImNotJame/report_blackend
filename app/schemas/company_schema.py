


from pydantic import BaseModel, ConfigDict
from datetime import datetime

class CompanyRequest(BaseModel):
    c_name: str

class CompanyResponse(BaseModel):
    c_id: str
    c_name: str
    c_created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)