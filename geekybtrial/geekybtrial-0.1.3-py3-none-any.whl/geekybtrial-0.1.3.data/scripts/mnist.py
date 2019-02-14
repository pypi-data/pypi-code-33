import tensorflow as tf
import cv2
import sys

from keras.models import load_model
from keras.models import model_from_json

#(x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()
#print(x_train)
#x_train = x_train.reshape(x_train.shape[0], 28, 28, 1)
#x_test = x_test.reshape(x_test.shape[0], 28, 28, 1)
#input_shape = (28, 28, 1)
#x_train = x_train.astype('float32')
#x_test = x_test.astype('float32')
#x_train /= 255
#x_test /= 255

json_file = open('c:/Users/TS-3/Desktop/mnist/model.json', 'r')
loaded_model_json = json_file.read()
json_file.close()
loaded_model = model_from_json(loaded_model_json)

loaded_model.load_weights("c:/Users/TS-3/Desktop/mnist/model.h5")
print("Loaded model from disk")

def give_name(str):
	strf = str
	img = cv2.imread(strf,0)
	pred = loaded_model.predict(img.reshape(1, 28, 28, 1))
	prin = pred.argmax()
	print(prin)

	cv2.imshow("asd",img)
	cv2.waitKey(0)
	return prin

	

#image_index = 4444
#pred = loaded_model.predict(x_test[image_index].reshape(1, 28, 28, 1))
#print(pred.argmax())
#print(x_test[image_index])

#print(sys.argv[1]);


