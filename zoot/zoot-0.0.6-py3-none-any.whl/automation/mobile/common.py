
class AppiumData():

    def __init__(self, url:str, data:dict):
        self.__url = url
        self.__data = data

    def get_url(self) -> str:
        return self.__url

    def add_data(self, key:str, value:any):
        self.__data[key] = value

    def get_data(self) -> dict:
        return self.__data