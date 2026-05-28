from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class WorkPictureBase(BaseModel):
    ws_id: str
    worker_id: Optional[str] = None
    file_url: str
    file_key: str


class WorkPictureCreate(WorkPictureBase):
    pass


class WorkPictureResponse(WorkPictureBase):
    wp_id: str
    create_at: datetime

    model_config = ConfigDict(from_attributes=True)
