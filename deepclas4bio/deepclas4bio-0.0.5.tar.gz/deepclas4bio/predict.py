from deepclas4bio import DatasetManager
from deepclas4bio.PredictorFactory import PredictorFactory

def predict(image,framework,model):
    predictor_factory=PredictorFactory()
    modelo=predictor_factory.getPredictor(framework,model)
    return modelo.predict(image)

def predictBatch(images,framework,model,batch=64):
    predictor_factory=PredictorFactory()
    modelo=predictor_factory.getPredictor(framework,model)
    dataManager= DatasetManager.DatasetManager(images, batch=batch)
    predictions=[]
    while(dataManager.hasNextBach()):
        batchImages=dataManager.nextBatch()
        prediction=modelo.predictBatch(batchImages)
        predictions+=prediction
    results=[]
    for p in predictions:
        results.append(modelo.model.postProcessor(p))
    return results

# parser=argparse.ArgumentParser()
# parser.add_argument("-i", "--image", required=True, help="Image to classify")
# parser.add_argument("-f", "--framework", required=True, help="Framework used to classify the image")
# parser.add_argument("-m", "--model", required=True, help="Model used to classify the image")
#
# args=vars(parser.parse_args())
# result=predict(args["image"],args["framework"], args["model"])
#
# data={}
# data['type']='classification'
# data['image']=args["image"]
# data['framework']=args["framework"]
# data['model']=args["model"]
# data['class']=result
# with open('data.json','w') as f:
#     json.dump(data,f)