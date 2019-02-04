from typing import Any, List

from podder_task_base.models import ResourceModel
from podder_task_base.repositories.base import BaseRepository
from sqlalchemy.orm.session import Session


class ResourceRepository(BaseRepository):

    model_class = ResourceModel
    RUNNING_STATUS = 'running'
    COMPLETE_STATUS = 'complete'

    @property
    def session(self) -> Session:
        return self.context.session

    def find_all(self) -> List[Any]:
        return self.session.query(self.model_class).all()

    def find_by_job_id(self, job_id: str) -> List[Any]:
        return self.session.query(self.model_class).filter(
            self.model_class.job_id == job_id)

    def find_by_unique_key(self, job_id: str, resource_id: str) -> ResourceModel:
        return self.session.query(self.model_class).filter(
            self.model_class.job_id == job_id,
            self.model_class.resource_id == resource_id).one_or_none()
