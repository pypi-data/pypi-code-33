import tensorflow as tf
from google.protobuf import text_format


def save_graph_pbtxt(fpath, graph=None):
    if fpath is None:
        return
    if graph is None:
        graph = tf.get_default_graph()

    tf.io.write_graph(graph.as_graph_def(), '.', fpath)


def load_graph_pbtxt(fpath):
    with tf.gfile.GFile(fpath, 'r') as f:
        graph_def = tf.GraphDef()
        text_format.Merge(f.read(), graph_def)
        tf.import_graph_def(graph_def, name='')


def save_graph_pb(fpath, graph=None):
    if fpath is None:
        return
    if graph is None:
        graph = tf.get_default_graph()

    with tf.gfile.GFile(fpath, "wb") as f:
        f.write(graph.as_graph_def().SerializeToString())


def load_graph_pb(fpath):
    with tf.gfile.GFile(fpath, 'rb') as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())
        tf.import_graph_def(graph_def, name='')
