from six.moves.queue import Queue


class Scheduler(object):
    """
    1. 缓存请求对象(Request)，并为下载器提供请求对象，实现请求的调度
    2. 对请求对象进行去重判断
    """
    def __init__(self):
        self.queue = Queue()

    def add_request(self, request):
        """添加请求对象"""
        self.queue.put(request)

    def get_request(self):
        """获取一个请求对象并返回"""
        request = self.queue.get()
        return request

    def _filter_request(self):
        """请求去重"""
        # 暂时不实现
        pass