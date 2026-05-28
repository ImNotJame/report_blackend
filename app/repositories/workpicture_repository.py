from app.models.workpicture import WorkPicture
from app.repositories.base import BaseRepository


class WorkPictureRepository(BaseRepository[WorkPicture]):
    pass


work_picture_repository = WorkPictureRepository(WorkPicture)
