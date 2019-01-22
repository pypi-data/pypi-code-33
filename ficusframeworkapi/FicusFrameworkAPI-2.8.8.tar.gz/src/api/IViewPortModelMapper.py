from abc import abstractmethod

class IViewPortModelMapper:

    @abstractmethod
    def mapper(self, value):
        """
        模型转换的基类方法, 传入一个 dict的value, 返回一个转换后的 dict   或  list<dict>
        :param vale:
        :return:
        """
        pass

    @abstractmethod
    def reduce(self,values):
        """
        模型转换的基类方法, 传入一个list<dict>的values, 返回一个转换后的 dict
        :param values:
        :return:
        """
        pass