## Note: this file should be the main user entry point.
# Therefore, don't use any f-strings here because this file should be syntactically parsable in any Python env < 3.6, including 2.
# That way we can at least throw an exception that tells the user to use Python 3.6.
import sys

# Python 3.6 check
if (sys.version_info < (3, 6)):
  raise Exception('Please install Datamode in a Python 3.6+ environment. Current Python version: ' + str(sys.version_info))

from .entry import execute_transforms, run_transforms, show_results, quickshow

# Todo: currently this will import log from transforms, which we don't want. We should import by hand.
# pylint: disable=unused-wildcard-import,wildcard-import
from .transforms.transforms import *
from .transforms.db_transforms import *
from .transforms.nlp import *
from .transforms.expressions.expression_transform import Expression
