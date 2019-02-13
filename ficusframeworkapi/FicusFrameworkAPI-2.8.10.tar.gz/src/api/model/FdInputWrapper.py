

class FdInputWrapper:
    """
    fd输入的一个包装
    """
    __fd_code = None
    __join_fd_codes = set()

    def fd_code(self):
        return self.__fd_code

    def __init__(self, fd_code):
        self.__fd_code = fd_code
        self.__join_fd_codes.add(fd_code)

    def join(self, other_fd_input):
        """
        合并两个fd的查询
        :param other_fd_input:
        :return:
        """
        return self

    def query(self, query, parameters={}):
        """
        对fd进行查询
        :param query: 查询语句
        :param parameters: 上下文参数
        :return: Munch对象数据
        """
        return None

    def info(self):
        """
        获取fd的信息
        :return:
        """
        return None
