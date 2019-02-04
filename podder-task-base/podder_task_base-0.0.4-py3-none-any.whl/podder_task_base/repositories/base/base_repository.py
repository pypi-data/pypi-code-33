from typing import Dict, List, Union

from podder_task_base.context import Context
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm.session import Session


class BaseRepository(object):
    model_class = DeclarativeMeta

    @property
    def session(self) -> Session:
        raise Exception('Not Implements of session. Please override.')

    def __init__(self, context: Context) -> None:
        self.context = context

    def all(self) -> List[DeclarativeMeta]:
        return self.session.query(self.model_class).all()

    def create(self, fields: Dict) -> DeclarativeMeta:
        model = self.model_class(**fields)
        self.session.add(model)
        return model

    def update(self, model: DeclarativeMeta, fields: Dict) -> DeclarativeMeta:
        for key in fields:
            setattr(model, key, fields[key])
        self.session.add(model)
        return model

    def delete(self, model: DeclarativeMeta) -> None:
        self.session.delete(model)

    def find(self, primary_id: int) -> DeclarativeMeta:
        return self.session.query(
            self.model_class).filter(self.model_class.id == primary_id).one_or_none()

    def exist(self, primary_id: Union[int, str]) -> bool:
        return self.session.query(
            self.model_class).filter(self.model_class.id == primary_id).exists().scalar()

    def save(self) -> None:
        self.session.commit()
