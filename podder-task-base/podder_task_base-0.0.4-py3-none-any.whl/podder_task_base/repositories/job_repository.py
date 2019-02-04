from typing import Any, List

from podder_task_base.models import JobModel
from podder_task_base.repositories.base import BaseRepository
from sqlalchemy.orm.session import Session


class JobRepository(BaseRepository):

    model_class = JobModel
    RUNNING_STATUS = 'running'
    COMPLETE_STATUS = 'complete'

    @property
    def session(self) -> Session:
        return self.context.session

    def find_all(self) -> List[Any]:
        return self.session.query(self.model_class).all()

    def find_by_unique_key(self, job_id: str) -> JobModel:
        return self.session.query(self.model_class).filter(
            self.model_class.job_id == job_id).one_or_none()

    def find_by_dag_id(self, dag_id: str) -> List[Any]:
        return self.session.query(self.model_class).filter(
            self.model_class.dag_id == dag_id)
