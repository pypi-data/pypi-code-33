import logging

from pydantic import BaseSettings


class _Settings(BaseSettings):
    ADMIN_API_KEY: str = "JUNK"
    MONGO_SERVER: str = "Noserver"
    MONGO_PORT: str = "27017"
    MONGO_USER: str = ""
    MONGO_PWD: str = ""
    MONGO_DBNAME: str = ""

    @property
    def MONGO_URI(self):
        user_auth = ""
        if self.MONGO_USER:
            user_auth = f"{self.MONGO_USER}:{self.MONGO_PWD}@"
        uri = f"mongodb://{user_auth}{self.MONGO_SERVER}:{self.MONGO_PORT}/{self.MONGO_DBNAME}"
        logging.debug("Using uri:" + uri)
        return uri

    class Config:
        env_prefix = ''


Settings = _Settings()
