from torch import nn

def resnet_fc(num_features,num_classes):

	return nn.Sequential(
        nn.Linear(num_features,512),
		nn.ReLU(),
        nn.Dropout(0.3),
        nn.Linear(512,128),
        nn.ReLU(),
        nn.Dropout(0.3),
        nn.Linear(128,num_classes)
    )
