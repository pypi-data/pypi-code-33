from deepclas4bio.PredictorFactory import PredictorFactory
from deepclas4bio import Evaluator, ReadDatasetFolders

readdataset= ReadDatasetFolders.ReadDatasetFolders()

evaluator= Evaluator.Evaluator(readdataset, '/home/adines/Escritorio/DatasetPrueba', '/home/adines/Escritorio/labels.txt')

# Añadimos las medidas
evaluator.addMeasure('accuracy')
evaluator.addMeasure('rank5')
evaluator.addMeasure('f1')

m=PredictorFactory()

# Keras
model=m.getPredictor('Keras','VGG16')

model2=m.getPredictor('Keras','VGG19')

# DL4J
model3=m.getPredictor('DL4J','ResNet50')

model4=m.getPredictor('DL4J','GoogleNet')

# Añadimos los modelos
evaluator.addPredictor(model)
evaluator.addPredictor(model2)
evaluator.addPredictor(model3)
evaluator.addPredictor(model4)


evaluator.evaluate()