import pyparsing
from collections.abc import Iterable

from .set_functions import get_func_by_name

from datamode.utils.utils import get_logger
log = get_logger(__name__)

from .tablecolumn import TableColumnManager


class ExpressionNode():
  def __init__(self, tcm, seed):
    self.tcm = tcm

    self.left = None
    self.right = None
    self.seed = seed

    self.op_fn = None

    # Infix nodes get special treatment - we want to seed with the infix's contents.
    if type(self.seed) == pyparsing.ParseResults and self.seed.infix:
      self.seed = self.seed.infix

    self.process_seed()


  # Build a subtree:
  #   Right subtree: the last element
  #   Current node: the second-last element (which should always be an operator)
  #   Left subtree: all remaining elements.
  def process_seed(self):
    tables_set = self.get_tables_present()

    if type(self.seed) == list and len(self.seed) == 1:
      # Here we'll have a list of 1 element, if we previously sliced the parseResults.
      # Extract the internal parseResults element from the list.
      if type(self.seed) == list:
        self.seed = self.seed[0]

    # If we still have only one element, use that to set the seed.
    if len(self.seed) == 1:
      self.set_contents(self.seed)
      return

    if len(self.seed) == 2:
      raise Exception('ExpressionNode: Infix operator count should be odd')

    # Operates on one element
    self.right = ExpressionNode(self.tcm, self.seed[-1])

    # Operates on one element
    self.set_contents(self.seed[-2])

    # Operates on 1+ elements
    self.left = ExpressionNode(self.tcm, self.seed[:-2])

  # Get the list of raw tables in an infix expression.
  # Only include tables at the base expression level (not those that are in lower node levels)
  def get_tables_present(self):
    tables_set = set()

    if not isinstance(self.seed, Iterable):
      return tables_set

    for item in self.seed:
      if type(item) == pyparsing.ParseResults:
        if item.tableColumn or item.column:
          tc = self.tcm.get_tablecolumn_from_raw_construct(item)
          if tc.table is None:
            raise Exception(f'ExpressionNode: column {tc.column} not found in existing tables.')
          tables_set.add(tc.table)

    return tables_set


  # Note that we'll never visit an infix node by itself.
  # Its elements will always be used to build a subtree instead.
  def set_contents(self, seed):
    self.determine_type(seed)

    if self.type == 'func':
      self.value = seed.func.name
      self.func_fn = get_func_by_name(self.value)

      self.left = ExpressionNode(self.tcm, self.seed.func.funcSingleArg)
    elif self.type == 'tableColumn':
      self.value = self.tcm.get_tablecolumn_from_raw_construct(seed)
    elif self.type == 'primitive':
      self.value = seed.primitive
    elif self.type == 'operator':
      self.value = seed
    else:
      raise Exception(f'ExpressionNode: self.type: {self.type} not understood')


  # Note that infix nodes should have been turned into a list of elements in the constructor.
  def determine_type(self, seed):
    if type(seed) == pyparsing.ParseResults:
      if seed.func:
        self.type = 'func'
      elif seed.column or seed.tableColumn:
        self.type = 'tableColumn'
      elif seed.primitive:
        self.type = 'primitive'
      else:
        self.type = f'ERROR-name:{seed.getName()}'
    else:
      # This happens when infixNotation is returning an operator.
      self.type = 'operator'



  # The main entry point to run this tree algorithm.
  def postorder_traversal(self, visit_fn, level=0, side='T'):
    left = None
    right = None

    if self.left:
      left = self.left.postorder_traversal(visit_fn, level + 1, 'L')

    if self.right:
      right = self.right.postorder_traversal(visit_fn, level + 1, 'R')

    # This is controlled outside the class.
    return visit_fn(side, level, self, left, right)


  def dump(self, indent=0, header='Top', _print=True):
    has_childs = self.left or self.right
    prefix = ' ' * indent
    colon = ':' if has_childs else ''

    output = ''
    # if header:
    #   output += f'{prefix}{header}: '

    output += f'{prefix}{header} {self.type}/{self.value}{colon}\n'

    if self.left:
      output += self.left.dump(indent + 2, header='Left')

    if self.right:
      output += self.right.dump(indent + 2, header='Right')

    # For debugging
    if indent == 0 and _print:
      print(output)

    return output

  def __str__(self):
    return f'type={self.type}, value= {self.value}'

  def __repr__(self):
    return f'<{self.__class__.__name__}: {self.__str__()}>'
