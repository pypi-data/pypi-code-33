import numpy as np
import pandas as pd
import operator as op
from sklearn_pmml_model.base import PMMLBaseEstimator
from sklearn.utils.validation import check_array
from sklearn.base import ClassifierMixin
from sklearn.tree._tree import Tree, NODE_DTYPE, TREE_LEAF, TREE_UNDEFINED
from sklearn.tree import DecisionTreeClassifier

class PMMLTreeClassifier2(PMMLBaseEstimator, DecisionTreeClassifier):
  def __init__(self, pmml, flat=False, field_labels=None):
    super().__init__(pmml, field_labels=field_labels)

    self.tree = self.find(self.root, 'TreeModel')

    if self.tree is None:
      raise Exception('PMML model does not contain TreeModel.')

    if self.tree.get('splitCharacteristic') != 'binarySplit':
      raise Exception('Sklearn only supports binary classification models.')

    if self.target_field is None:
      raise Exception('PMML does not specify target.')

    self.classes_ = np.array([
      self.parse_type(e.get('value'), self.target_field, force_native=True)
      for e in self.findall(self.target_field, 'Value')
    ])

    target = self.target_field.get('name')
    fields = [ field for name, field in self.fields.items() if name != target ]

    if field_labels is not None:
      self.n_features_ = len(field_labels)
    else:
      self.n_features_ = len([field for field in fields if field.tag == f'{{{self.namespace}}}DataField'])
      
    self.n_outputs_ = 1
    self.n_classes_ = len(self.classes_)
    self.tree_ = Tree(self.n_features_, np.array([self.n_classes_]), self.n_outputs_)

    firstNode = self.find(self.tree, 'Node')
    nodes, values = self.constructTree(firstNode)

    node_ndarray = np.ascontiguousarray(nodes, dtype=NODE_DTYPE)
    value_ndarray = np.ascontiguousarray(values)
    max_depth = None
    state = {
      'max_depth': (2 ** 31) - 1 if max_depth is None else max_depth,
      'node_count': node_ndarray.shape[0],
      'nodes': node_ndarray,
      'values': value_ndarray
    }
    self.tree_.__setstate__(state)

  def constructTree(self, node, i = 0):
    childNodes = self.findall(node, 'Node')

    if len(childNodes) == 0:
      impurity = 0 # TODO: not really necessary, but do it anyway
      node_count = int(float(node.get('recordCount')))
      node_count_weighted = float(node.get('recordCount'))

      return [
        [(TREE_LEAF, TREE_LEAF, TREE_UNDEFINED, TREE_UNDEFINED, impurity, node_count, node_count_weighted)],
        np.array([[[float(e.get('recordCount')) for e in self.findall(node, 'ScoreDistribution')]]])
      ]

    left_node, left_value = self.constructTree(childNodes[0], i + 1)
    offset = len(left_node)
    right_node, right_value = self.constructTree(childNodes[1], i + 1 + offset)

    children = left_node + right_node
    distributions = np.concatenate((left_value, right_value))

    predicate = self.find(childNodes[0], 'SimplePredicate')
    column, mapping = self.field_mapping[predicate.get('field')]
    value = mapping(predicate.get('value'))
    impurity = 0 # TODO: not really necessary, but do it anyway

    distributions_children = distributions[[0, offset]]
    distribution = np.sum(distributions_children, axis=0)
    node_count = int(np.sum(distribution))
    node_count_weighted = float(np.sum(distribution))

    return [(i + 1, i + 1 + offset, column, value, impurity, node_count, node_count_weighted)] + children, \
           np.concatenate((np.array([distribution]), distributions))


class PMMLTreeClassifier(PMMLBaseEstimator, ClassifierMixin):
  def __init__(self, pmml):
    super(PMMLTreeClassifier, self).__init__(pmml)

    self.tree = self.find(self.root, 'TreeModel')

    if self.tree is None:
      raise Exception('PMML model does not contain TreeModel.')

    if self.target_field is not None:
      self.classes_ = np.array([
        e.get('value')
        for e in self.findall(self.target_field, 'Value')
      ])

      self.tree_ = Tree(len(self.fields), np.array([len(self.classes_)]), 1)
      self.tree_.node_count = len([x for x in self.tree.iter(f'{{{self.namespace}}}Node')])

  def evaluate_node(self, node, instance):
    predicates = {
      'True': lambda *_: True,
      'False': lambda *_: False,
      'SimplePredicate': self.evaluate_simple_predicate,
      'CompoundPredicate': lambda *_: (_ for _ in ()).throw(Exception('Predicate not implemented')),
      'SimpleSetPredicate': lambda *_: (_ for _ in ()).throw(Exception('Predicate not implemented'))
    }

    for predicate, evaluate in predicates.items():
      element = self.find(node, predicate)
      if element is not None:
        return evaluate(element, instance)

    return False

  def evaluate_simple_predicate(self, element, instance):
    """
    Evaluate <SimplePredicate> PMML tag.

    Parameters
    ----------
    element : xml.etree.ElementTree.Element
        XML Element with tag <SimplePredicate>.

    instance : pd.Series
        Instance we want to evaluate the predicate on.

    Returns
    -------
    bool
        Indicating whether the predicate holds or not.

    """
    field = element.get('field')

    column, mapping = self.field_mapping[field]
    a = mapping(instance[column])
    operator = element.get('operator')
    b = mapping(element.get('value'))

    operators = {
      'equal': op.eq,
      'notEqual': op.ne,
      'lessThan': op.lt,
      'lessOrEqual': op.le,
      'greaterThan': op.gt,
      'greaterOrEqual': op.ge,
      'isMissing': lambda *_: (_ for _ in ()).throw(Exception('Operator not implemented')),
      'isNotMissing': lambda *_: (_ for _ in ()).throw(Exception('Operator not implemented')),
    }

    return operators[operator](a, b)

  def predict(self, X):
    """
    Predict instances in X.

    Parameters
    ----------
    X : pd.DataFrame
        The data to be perdicted. Should have the same format as the training data.

    Returns
    -------
    numpy.ndarray
        Array of size len(X), where every row contains a prediction for the
        corresponding row in X.

    """
    X = check_array(X)

    return np.ma.apply_along_axis(lambda x: self.predict_instance(x), 1, X)

  def predict_proba(self, X):
    """
    Predict instances in X.

    Parameters
    ----------
    X : pd.DataFrame
        The data to be perdicted. Should have the same format as the training data.

    Returns
    -------
    numpy.ndarray
        Array of size len(X), where every row contains a probability for each class
        for the corresponding row in X.

    """
    X = check_array(X)

    return np.apply_along_axis(lambda x: self.predict_instance(x, probabilities=True), 1, X)

  def predict_instance(self, instance, probabilities=False):
    """
    Prediction for a single instance.

    Parameters
    ----------
    instance : pd.Series
        Instance to be classified.

    probabilities : bool (default: False)
        Whether the method should return class probabilities or just the predicted class.

    Returns
    -------
    Any
        Prediction values or class probabilities.

    """
    node = self.tree

    while True:
      childNodes = self.findall(node, 'Node')

      if len(childNodes) == 0:
        if probabilities:
          return pd.Series([
            float(e.get('recordCount')) / float(node.get('recordCount'))
            for e in self.findall(node, 'ScoreDistribution')
          ])
        else:
          return node.get('score')

      for childNode in childNodes:
        if self.evaluate_node(childNode, instance):
          node = childNode
          break
