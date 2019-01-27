from atila import Atila
import tfserver
import tensorflow as tf
from tfserver import prediction_service_pb2, predict_pb2
from tensorflow.python.framework import tensor_util, dtypes
import numpy as np
import os

app = Atila (__name__)
app.debug = False
app.use_reloader = False
app.access_control_allow_origin = ["127.0.0.1"]

@app.before_mount
def before_mount (wasc):
	for alias, params in app.config.tf_models.items ():
		config = None
		if isinstance (params, str):
			model_dir = params
		elif len (params) == 1:
			model_dir = params [0] 
		else:
			model_dir, config = params
		wasc.logger ("app", "serve tensorflow model '{}' on {}".format (alias, model_dir), 'info')	
		tfserver.load_model (alias, model_dir, config)
			
@app.umounted
def umounted (wasc):
	tfserver.close ()

@app.route ("/tensorflow.serving.PredictionService/Predict")
def Predict (was, request, timeout = 10):
	sess = tfserver.tfsess.get (request.model_spec.name)
	interp = sess.interp
	signature_name = request.model_spec.signature_name
	
	feed_dict = {}
	for k, v in request.inputs.items ():
		tensor_name, tensor, dtype, shape = interp.input_map [signature_name][k]
		v = tensor_util.MakeNdarray (v)
		if k == "x": v = interp.normalize (v)
		feed_dict [tensor] = v
		
	predict_results = sess.run (feed_dict, signature_name)
	response = predict_pb2.PredictResponse()
	for i, result in enumerate (interp.outputs [signature_name]):
		predict_result = predict_results [i]		
		response.outputs [interp.outputs [signature_name][i][0]].CopyFrom (
			tensor_util.make_tensor_proto (predict_result, np.float32)
		)			
	return response
	
@app.route ("/predict")
def predict (was, **inputs):
	sess = tfserver.tfsess.get (request.model_spec.name)
	interp = sess.interp
	signature_name = request.model_spec.signature_name
	
	feed_dict = {}
	for k, v in inputs.items ():
		tensor_name, tensor, dtype, shape = interp.input_map [signature_name][k]
		v = np.array (v)
		if k == "x": v = interp.normalize (v)
		feed_dict [tensor] = v
	predict_results = sess.run (feed_dict, signature_name)
	
	response = {}
	for i, result in enumerate (interp.outputs [signature_name]):
		predict_result = predict_results [i]
		response [interp.outputs [signature_name][i][0]] = predict_result.astype ("float32").tolist ()		
	return was.response.api (response)

@app.route ("/model/<model>/version")
def version (was, model):	
	sess = tfserver.tfsess.get (model)
	if sess is None:
		return was.response ("404 Not Found")
	return was.response.api (version = sess.get_version ())
