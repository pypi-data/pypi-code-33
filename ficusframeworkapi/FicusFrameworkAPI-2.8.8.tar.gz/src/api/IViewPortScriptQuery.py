from abc import abstractmethod

from api.Page import Page


class IViewPortScriptQuery:
    """
    viewport 自定义查询脚本接口
    """

    @abstractmethod
    def query(self,fd_code:str,parameters:dict) -> Page:
        """
        查询的业务逻辑
        :param fd_code: viewport源fd
        :param parameters: 上下文参数
        :return: 查询结果, 要求是Page对象
        """
        pass