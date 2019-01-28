import math,random
import pickle
import matrix


#activation functions
def sigmoid(x):
	return 1/(1+math.exp(-x))
def d_sigmoid(y):
	return y*(1-y)

class NeuralNetwork:
	def __init__(self,numI,numH,numO):
		self.input_nodes = numI
		self.hidden_nodes = numH
		self.lr = 0.1
		self.output_nodes = numO

		self.weight_ih = Matrix(self.hidden_nodes,self.input_nodes)
		self.weight_ih.randomize()
		self.weight_ho = Matrix(self.output_nodes,self.hidden_nodes)
		self.weight_ho.randomize()

		self.bias_h = Matrix(self.hidden_nodes,1)
		self.bias_h.randomize()
		self.bias_o = Matrix(self.output_nodes,1)
		self.bias_o.randomize()

        #Change Learning Rate
	def setLearningRate(self,nlr):
                self.lr = nlr


        #Making Predictions
        #Feed Forward Algorithm
	def predict(self,arr):

		#Generating hidden outputs
		nputs = Matrix.fromArray(arr)
		hidden = Matrix.matrix_mult(self.weight_ih,nputs)
		hidden.add(self.bias_h)
		hidden.map(sigmoid)

		output = Matrix.matrix_mult(self.weight_ho,hidden)
		output.add(self.bias_o)
		output.map(sigmoid)

		#sending the prediction
		return output.toArray()

        #just to know about model structure
	def summary(self):
		print()
		print('--------------')
		print('Input Nodes: '+str(self.input_nodes))
		print('--------------')
		print('Hidden Nodes: '+str(self.input_nodes))
		print('--------------')
		print('Output Nodes: '+str(self.input_nodes))
		print('--------------')
		print()

        #Training Process
	#BackPropagation algorithm
	def train(self,nputs_arr,targets_arr):
		nputs = Matrix.fromArray(nputs_arr)
		hidden = Matrix.matrix_mult(self.weight_ih,nputs)
		hidden.add(self.bias_h)
		hidden.map(sigmoid)

		outputs = Matrix.matrix_mult(self.weight_ho,hidden)
		outputs.add(self.bias_o)
		outputs.map(sigmoid)

		targets = Matrix.fromArray(targets_arr)

		#error = target-outputs
		output_errors = Matrix.subtract(targets,outputs)

		#calc gradients
		gradients = Matrix.s_map(outputs,d_sigmoid)
		gradients.multiply(output_errors)
		gradients.multiply(self.lr)

		#calc deltas
		hidden_T = Matrix.transpose(hidden)
		weight_ho_deltas = Matrix.matrix_mult(gradients,hidden_T)
		self.weight_ho.add(weight_ho_deltas)

		self.bias_o.add(gradients)

		#hiden layer error
		w_ho_t = Matrix.transpose(self.weight_ho)
		hidden_errors = Matrix.matrix_mult(w_ho_t,output_errors)

		#CALC hidden gradient
		hidden_gradient = Matrix.s_map(hidden,d_sigmoid)
		hidden_gradient.multiply(hidden_errors)
		hidden_gradient.multiply(self.lr)

		#calc input->hidden deltas
		inputs_T = Matrix.transpose(nputs)
		weight_ih_deltas = Matrix.matrix_mult(hidden_gradient,inputs_T)

		self.weight_ih.add(weight_ih_deltas)

		self.bias_h.add(hidden_gradient)

def save_model(ob,fname):
	f = open(fname,'wb')
	pickle.dump(ob,f)

def load_model(fname):
	f = open(fname,'rb')
	return pickle.load(f)
