# 用来在程序中写入日志
class TaskLogger:

    def __init__(self,log_file_name) -> None:
        self._log_file_name = log_file_name

    def log(self, append_log: str):
        """
            记录日志信息
            :param append_log: 需要记录的内容
            :return:
            """
        pass

    def error(self, e: Exception):
        """
            记录异常信息
            :param e:  抛出的异常
            :return:
            """
        pass
