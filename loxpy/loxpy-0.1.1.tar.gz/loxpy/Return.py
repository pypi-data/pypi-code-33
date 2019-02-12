class Return(RuntimeError):
    """用系统的异常捕获来获取返回值"""  # REVIEW: 用 map 存储每个节点的值可能是更好的方法。

    def __init__(self, value: object):
        super().__init__()
        self.value = value
