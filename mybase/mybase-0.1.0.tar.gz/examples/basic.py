
# =========================================
#       IMPORTS
# --------------------------------------

import rootpath

rootpath.append()


# =========================================
#       EXAMPLE
# --------------------------------------

from mybase import Base

class Foo(Base):

    def hello():
        self.logger.log('hello from instance: `{0}`'.format(self))

foo = Foo()

# logs using default logger - with colors unless disabled via `COLORS` / `LOGGER_COLORS` env variables
foo.hello()
foo.logger.log('hello world 1')

print(foo.name)
print(repr(foo))
print(str(foo))

import logging

foo2 = Foo(logger = logging.get_logger('custom'))

# logs using custom logger
foo.hello()
foo.logger.log('hello world 2')

foo3 = Foo(logger = False)

# logs nothing
foo.hello()
foo.logger.log('hello world 3')
