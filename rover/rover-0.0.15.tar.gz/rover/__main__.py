from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

from future import standard_library
standard_library.install_aliases()
from rover import main

# this is the command executed when the module is invoked
# using 'python -m rover'

main()
