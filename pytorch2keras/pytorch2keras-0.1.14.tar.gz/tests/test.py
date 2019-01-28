import numpy as np
import torch
from torch.autograd import Variable
from pytorch2keras.converter import pytorch_to_keras
import torchvision


class ResNet(torchvision.models.resnet.ResNet):
    def __init__(self, *args, **kwargs):
        super(ResNet, self).__init__(*args, **kwargs)

    def forward(self, x):
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.maxpool(x)

        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)

        x = self.avgpool(x)
        x = x.view(int(x.size(0)), -1)  # << This fix again
        x = self.fc(x)
        return x


def check_error(output, k_model, input_np, epsilon=1e-3):
    pytorch_output = output[0].data.numpy()
    keras_output = k_model.predict(input_np)

    error = np.max(pytorch_output - keras_output[0])
    print('Error:', error)

    assert error < epsilon
    return error

import torch.nn as nn

class resnet_gender_cls(nn.Module):
    def base_size(self): return 512
    def rep_size(self): return 1024

    def __init__(self, n_classes):
        super(resnet_gender_cls, self).__init__()
        self.resnet = torchvision.models.resnet34(pretrained=False)
        self.conv1 = self.resnet.conv1
        self.bn1 = self.resnet.bn1
        self.layer1 = self.resnet.layer1
        self.layer2 = self.resnet.layer2
        self.layer3 = self.resnet.layer3
        self.layer4 = self.resnet.layer4

        # define layers
        self.n_classes = n_classes
        self.linear = nn.Linear(7 * 7 * self.base_size(), self.rep_size())
        self.cls = nn.Linear(self.rep_size(), self.n_classes)
        self.dropout2d = nn.Dropout2d(.5)
        self.dropout = nn.Dropout(.5)
        self.relu = nn.LeakyReLU()

    def forward(self, out0):
        x = self.conv1(out0)
        x = self.bn1(x)
        x = self.resnet.relu(x)
        x = self.resnet.maxpool(x)

        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
     
        x = self.dropout2d(x)

        x = self.relu(self.linear(x.view(-1, 7*7*self.base_size())))
        x = self.dropout(x.clone())
        cls_scores = self.cls(x.clone())
        return cls_scores

if __name__ == '__main__':
    max_error = 0
    for i in range(100):
        model = resnet_gender_cls(32)
        model.eval()

        input_np = np.random.uniform(0, 1, (1, 3, 224, 224))
        input_var = Variable(torch.FloatTensor(input_np))
        output = model(input_var)

        k_model = pytorch_to_keras(model, input_var, (3, 224, 224,), verbose=True)

        error = check_error(output, k_model, input_np)
        if max_error < error:
            max_error = error

    print('Max error: {0}'.format(max_error))

