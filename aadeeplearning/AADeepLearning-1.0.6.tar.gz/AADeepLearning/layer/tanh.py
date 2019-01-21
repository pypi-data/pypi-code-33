import numpy as np

class Tanh:
    """
    Tanh 激活函数层
    """
    @staticmethod
    def init(layer, flow_data_shape, config):
        """
        初始化， 这里无操作
        :param layer: 层，包含该层的权重、偏置项、梯度、前向输入输出缓存、实例化对象等信息
        :param flow_data_shape: 流动数据的形状
        :param config:配置
        :return: 更新后的层， 流动数据的形状
        """
        return layer, flow_data_shape
    @staticmethod
    def forword(flow_data, layer, is_train):
        """
        前向传播
        :param flow_data: 流动数据
        :param layer: 层，包含该层的权重、偏置项、梯度、前向输入输出缓存、实例化对象等信息
        :param is_train: 是否是训练模式
        :return: 流动数据， 更新后的层
        """
        flow_data = np.tanh(flow_data)
        return flow_data, layer
    @staticmethod
    def backword(flow_data, cache_output):
        """
        反向传播
        :param flow_data: 流动数据
        :param layer: 层，包含该层的权重、偏置项、梯度、前向输入输出缓存、实例化对象等信息
        :param config:配置
        :return: 流动数据， 更新后的层
        """
        # dtanh/dz  = 1-a^2
        return flow_data * (1 - np.power(cache_output, 2))
