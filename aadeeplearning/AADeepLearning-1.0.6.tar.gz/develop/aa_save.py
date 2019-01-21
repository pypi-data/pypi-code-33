from __future__ import print_function
import numpy as np

np.random.seed(1337)
# 生产环境
# from aa_deep_learning.aadeeplearning.aadeeplearning_old import AADeepLearning
from aa_deep_learning.AADeepLearning import AADeepLearning
from aa_deep_learning.AADeepLearning.datasets import mnist
from aa_deep_learning.AADeepLearning.datasets import np_utils

# 测试环境
# from aadeeplearning import aadeeplearning as aa



# 10分类
nb_classes = 10

# keras中的mnist数据集已经被划分成了60,000个训练集，10,000个测试集的形式，按以下格式调用即可
(x_train, y_train), (x_test, y_test) = mnist.load_data()
x_test = x_test[:100]
y_test = y_test[:100]

# print(x_test[0])

# 画出minist 数字
# import matplotlib.pyplot as plt
# fig = plt.figure()
# plt.imshow(x_test[0],cmap = 'binary')#黑白显示
# plt.show()

# 后端使用tensorflow时，即tf模式下，
# 会将100张RGB三通道的16*32彩色图表示为(100,16,32,3)，
# 第一个维度是样本维，表示样本的数目，
# 第二和第三个维度是高和宽，
# 最后一个维度是通道维，表示颜色通道数
x_train = x_train.reshape(x_train.shape[0], img_rows, img_cols, 1)
x_test = x_test.reshape(x_test.shape[0], img_rows, img_cols, 1)
input_shape = (img_rows, img_cols, 1)

# 将x_train, x_test的数据格式转为float32
x_train = x_train.astype('float32')
x_test = x_test.astype('float32')
# 归一化，将值映射到 0到1区间
x_train /= 255
x_test /= 255
# 打印出相关信息
print('x_train shape:', x_train.shape)
print('y_train shape:', y_train.shape)
print('x_test shape:', x_test.shape)
print('y_test shape:', y_test.shape)
print(x_train.shape[0], 'train samples')
print(x_test.shape[0], 'test samples')
# x_train shape: (60000, 28, 28, 1)
# 60000 train samples
# 10000 test samples

# 将类别向量(从0到nb_classes的整数向量)映射为二值类别矩阵，
# 相当于将向量用one-hot重新编码
y_train = np_utils.to_categorical(y_train, nb_classes)
y_test = np_utils.to_categorical(y_test, nb_classes)
# print(y_test.shape)
# 网络配置文件
config = {
    # 初始学习率
    "learning_rate": 0.001,
    # 学习率衰减: 通常设置为 0.99
    "learning_rate_decay": 0.9999,
    # 优化策略: sgd/momentum/rmsprop/adam
    "optimizer": "sgd",
    # 使用动量的梯度下降算法做优化,可以设置这一项，默认值为 0.9 ，一般不需要调整
    "momentum_coefficient": 0.9,
    # rmsprop优化器的衰减系数
    "rmsprop_decay": 0.95,
    # 正则化系数
    "reg_coefficient": 0,
    # 训练多少次
    "number_iteration": 2000,
    # 每次用多少个样本训练
    "batch_size": 64,
    # 每隔几个迭代周期评估一次准确率？
    "evaluate_interval": 10,


    # 保存模型快照的名称
    "save_model": "AA",
    # 每隔几个迭代周期保存一次快照？
    "save_iteration": 500,
    # 预训练参数模型所在路径

}

net = [
    {
        # 层名
        "name": "flatten_1",
        # 层类型
        "type": "flatten"
    },
    {
        # 层名
        "name": "fully_connected_1",
        # 层类型
        "type": "fully_connected",
        # 神经元个数
        "neurons_number": 32,
        # 权重初始化方式  msra/xavier/gaussian
        "weight_init": "msra"
    },
    {
        # 层名
        "name": "relu_1",
        # 层类型 可选，relu，sigmoid，tanh，
        "type": "relu",
        # relu函数的上界限制值；   注： 不做设置或者设置为0意味着是普通的relu函数
        "threshold": 0
    },
    {
        # 层名
        "name": "fully_connected_2",
        # 层类型
        "type": "fully_connected",
        # 神经元个数
        "neurons_number": 10,
        # 权重初始化方式  msra/xavier/gaussian
        "weight_init": "msra"
    },
    {
        # 层名
        "name": "softmax",
        # 层类型
        "type": "softmax"
    }
]


AA = AADeepLearning(net=net, config=config)
# 训练模型
AA.train(x_train=x_train, y_train=y_train)

# 使用测试集预测，返回概率分布和准确率， score:样本在各个分类上的概率， accuracy:准确率
score, accuracy = AA.predict(x_test=x_test, y_test=y_test)
print("test set accuracy:",accuracy)
