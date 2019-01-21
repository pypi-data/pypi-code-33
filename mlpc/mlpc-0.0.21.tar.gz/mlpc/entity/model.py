from mlpc.entity.base_entities import BaseEntityWithRegularStorage


class Model(BaseEntityWithRegularStorage):
    def __init__(self, storage):
        super().__init__(storage, "model")
