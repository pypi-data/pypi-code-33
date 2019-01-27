import os
import tensorflow as tf
import time
import pickle

__version__ = "0.2.0.4"

class Session:
    def __init__ (self, model_dir, tfconfig = None):
        from dnn import saved_model
        
        self.model_dir = model_dir
        try:
            self.version = int (os.path.basename (model_dir))
        except:
            self.version = 0    
        self.tfconfig = tfconfig
        self.graph = tf.Graph ()
        self.tfsess = tf.Session (config = tfconfig, graph = self.graph)
        self.interp =  saved_model.load (model_dir, self.tfsess)
                                            
    def get_version (self):
        return self.version
            
    def run (self, feed_dict, signature_def_name = tf.saved_model.signature_constants.DEFAULT_SERVING_SIGNATURE_DEF_KEY):
        return self.interp._run (feed_dict, signature_def_name)
        
    def close (self):
        self.tfsess.close ()
        
tfsess = {}
def load_model (alias, model_dir, tfconfig = None):
    global tfsess
    tfsess [alias] = Session (model_dir, tfconfig)
    
def close ():
    global tfsess
    
    for sess in tfsess.values ():
        sess.close ()
    tfsess = {}
