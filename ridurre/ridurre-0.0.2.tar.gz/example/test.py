from keras import optimizers, losses

import ridurre
from example.cifar_10_resnet import resnet

# Creating ResNet50 model
model = resnet.resnet_v1(input_shape=(32, 32, 3), depth=20, num_classes=10)


def compile_model(my_model):
    my_model.compile(optimizer=optimizers.Adam(lr=0.001), loss=losses.categorical_crossentropy, metrics=["accuracy"])


compile_model(model)

pruning = ridurre.KMeansFilterPruning(0.9,
                                      compile_model,
                                      None,
                                      nb_finetune_epochs=5,
                                      maximum_pruning_percent=0.85,
                                      maximum_prune_iterations=10)
pruning.define_prune_bins([0, 20, 60, 10, 10], [ 1., 1., 0.5])
model, last_epoch_number = pruning.run_pruning(model)
