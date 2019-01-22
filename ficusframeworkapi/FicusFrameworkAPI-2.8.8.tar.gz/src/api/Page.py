
class Page:

    def __init__(self,pageNum=0,pageSize=0,total=0,list=None):
        """

        :param pageNum:  页数
        :param pageSize: 每一页大小
        :param total: 总结果大小
        :param list: 结果集数据
        """
        self.pageNum = pageNum
        self.pageSize = pageSize
        self.list = list
        if  total==0 and list is not None:
            self._set_total(len(list))
        else:
            self._set_total(total)

    def result(self):
        return self.list

    def pages(self):
        return self.pages

    def _set_total(self,total):
        self.total = total

        if  self.pageSize > 0:
            self.pages = total // self.pageSize + (0 if (total % self.pageSize == 0 ) else 1)
        else:
            self.pages = 0



