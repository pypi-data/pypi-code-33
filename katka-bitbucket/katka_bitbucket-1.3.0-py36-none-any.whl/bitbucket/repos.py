import logging

from dataclasses import dataclass

from .service import BitbucketService

log = logging.getLogger(__name__)


@dataclass
class BitbucketRepos(BitbucketService):
    project_id: str = None

    def __post_init__(self):
        """
        Raises:
            ValueError: In case project_key is null or empty
        """
        if not self.project_id:
            raise ValueError('project_id can\'t be null or empty')

        super().__post_init__()

    def get_repos(self, params: dict = None) -> dict:
        self.path = f'projects/{self.project_id}/repos'
        return super().get(params=params)
