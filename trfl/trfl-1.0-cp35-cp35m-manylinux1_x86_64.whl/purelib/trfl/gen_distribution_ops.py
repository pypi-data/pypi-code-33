import tensorflow as tf
_op_lib = tf.load_op_library(tf.resource_loader.get_path_to_datafile("_gen_distribution_ops.so"))
project_distribution = _op_lib.project_distribution
del _op_lib, tf
