
# =========================================
#       IMPORTS
# --------------------------------------

from __future__ import print_function # Optional: Python 2 support for `env.print`

import rootpath

rootpath.append()


# =========================================
#       EXAMPLE
# --------------------------------------

from envjoy import env

# non-casted access - never throws annoying errors

env.FOO
env.FOO = 1

del env.FOO

env.FOO = 1

# casted access - never throws annoying errors

del env['FOO']

print('---')

print(env['FOO']) # => None

env['FOO']= 1 # set value without complaints (casted to string)

print(env['FOO']) # => "1"
print(env['FOO']) # => 1

print('---')

env['FOO'] = None

print(env['FOO']) # => ''
print(env['FOO', bool]) # => False
print(env['FOO', int]) # => 0
print(env['FOO', float]) # => 0.0
print(env['FOO', str]) # => ''
print(env['FOO', tuple]) # => ()
print(env['FOO', list]) # => []
print(env['FOO', dict]) # => {}

print('---')

env['FOO'] = True

print(env['FOO']) # => 'True'
print(env['FOO', bool]) # => True
print(env['FOO', int]) # => 1
print(env['FOO', float]) # => 1.0
print(env['FOO', str]) # => 'true'
print(env['FOO', tuple]) # => (True)
print(env['FOO', list]) # => [True]
print(env['FOO', dict]) # => {}

print('---')

env['FOO'] = 'true' # => 'true'

print(env['FOO', bool]) # => True
print(env['FOO', int]) # => 1
print(env['FOO', float]) # => 1.0
print(env['FOO', str]) # => 'true'
print(env['FOO', tuple]) # => (True)
print(env['FOO', list]) # => [True]
print(env['FOO', dict]) # => {}

print('---')

env['FOO'] = 0

print(env['FOO']) # => '0'
print(env['FOO', bool]) # => False
print(env['FOO', int]) # => 0
print(env['FOO', float]) # => 0.0
print(env['FOO', str]) # => '0'
print(env['FOO', tuple]) # => (0)
print(env['FOO', list]) # => [0]
print(env['FOO', dict]) # => {}

print('---')

env['FOO'] = '0'

print(env['FOO']) # => '0'
print(env['FOO', bool]) # => False
print(env['FOO', int]) # => 0
print(env['FOO', float]) # => 0.0
print(env['FOO', str]) # => '0'
print(env['FOO', tuple]) # => (0)
print(env['FOO', list]) # => [0]
print(env['FOO', dict]) # => {}

print('---')

env['FOO'] = 1

print(env['FOO']) # => '1'
print(env['FOO', bool]) # => True
print(env['FOO', int]) # => 1
print(env['FOO', float]) # => 1.0
print(env['FOO', str]) # => '1'
print(env['FOO', tuple]) # => (1)
print(env['FOO', list]) # => [1]
print(env['FOO', dict]) # => {}

print('---')

env['FOO'] = '1'

print(env['FOO']) # => '1'
print(env['FOO', bool]) # => True
print(env['FOO', int]) # => 1
print(env['FOO', float]) # => 1.0
print(env['FOO', str]) # => '1'
print(env['FOO', tuple]) # => (1)
print(env['FOO', list]) # => [1]
print(env['FOO', dict]) # => {}

print('---')

env['FOO'] = -1

print(env['FOO']) # => '-1'
print(env['FOO', bool]) # => True
print(env['FOO', int]) # => -1
print(env['FOO', float]) # => -1.0
print(env['FOO', str]) # => '-1'
print(env['FOO', tuple]) # => (-1)
print(env['FOO', list]) # => [1]
print(env['FOO', dict]) # => {}

print('---')

env['FOO'] = '-1'

print(env['FOO']) # => '-1'
print(env['FOO', bool]) # => True
print(env['FOO', int]) # => -1
print(env['FOO', float]) # => -1.0
print(env['FOO', str]) # => '-1'
print(env['FOO', tuple]) # => (-1)
print(env['FOO', list]) # => [1]
print(env['FOO', dict]) # => {}

print('---')

env['FOO'] = 12.34

print(env['FOO']) # => '12.34'
print(env['FOO', bool]) # => True
print(env['FOO', int]) # => 12
print(env['FOO', float]) # => 12.34
print(env['FOO', str]) # => '12.34'
print(env['FOO', tuple]) # => (12.34)
print(env['FOO', list]) # => [12.34]
print(env['FOO', dict]) # => {}

print('---')

env['FOO'] = '12.34'

print(env['FOO']) # => '12.34'
print(env['FOO', bool]) # => True
print(env['FOO', int]) # => 12
print(env['FOO', float]) # => 12.34
print(env['FOO', str]) # => '12.34'
print(env['FOO', tuple]) # => (12.34)
print(env['FOO', list]) # => [12.34]
print(env['FOO', dict]) # => {}

print('---')

env['FOO'] = -12.34

print(env['FOO']) # => '-12.34'
print(env['FOO', bool]) # => True
print(env['FOO', int]) # => -12
print(env['FOO', float]) # => -12.34
print(env['FOO', str]) # => '-12.34'
print(env['FOO', tuple]) # => (-12.34)
print(env['FOO', list]) # => [-12.34]
print(env['FOO', dict]) # => {}

print('---')

env['FOO'] = '-12.34'

print(env['FOO']) # => '-12.34'
print(env['FOO', bool]) # => True
print(env['FOO', int]) # => -12
print(env['FOO', float]) # => -12.34
print(env['FOO', str]) # => '-12.34'
print(env['FOO', tuple]) # => (-12.34)
print(env['FOO', list]) # => [-12.34]
print(env['FOO', dict]) # => {}

print('---')

env['FOO'] = 'foo bar baz 1 2 3'

print(env['FOO']) # => 'foo bar baz 1 2 3'
print(env['FOO', bool]) # => True
print(env['FOO', int]) # => 123
print(env['FOO', float]) # => 123.0
print(env['FOO', str]) # => 'foo bar baz 1 2 3'
print(env['FOO', tuple]) # => ('foo bar baz 1 2 3')
print(env['FOO', list]) # => ['foo bar baz 1 2 3']
print(env['FOO', dict]) # => {}

print('---')

env['FOO'] = 'foo,bar,baz,1,2,3'

print(env['FOO']) # => 'foo,bar,baz,1,2,3'
print(env['FOO', bool]) # => True
print(env['FOO', int]) # => 123
print(env['FOO', float]) # => 123.0
print(env['FOO', str]) # => 'foo,bar,baz,1,2,3'
print(env['FOO', tuple]) # => ('foo', 'bar', 'baz')
print(env['FOO', list]) # => ['foo', 'bar', 'baz']
print(env['FOO', dict]) # => {0: 'foo', 1: 'bar', 2: 'baz'}

print('---')

env['FOO'] = ('foo', 'bar', 'baz', 1, 2, 3)

print(env['FOO']) # => '(foo,bar,baz,1,2,3)'
print(env['FOO', bool]) # => True
print(env['FOO', int]) # => 123
print(env['FOO', float]) # => 123.0
print(env['FOO', str]) # => '(foo,bar,baz,1,2,3)'
print(env['FOO', tuple]) # => ('foo', 'bar', 'baz')
print(env['FOO', list]) # => ['foo', 'bar', 'baz', 1, 2, 3]
print(env['FOO', dict]) # => {} # TODO:  {0: 'foo', 1: 'bar', 2: 'baz', 3: 1, 4: 2, 5: 3}

print('---')

env['FOO'] = ['foo', 'bar', 'baz', 1, 2, 3]

print(env['FOO']) # => '[foo,bar,baz,1,2,3]'
print(env['FOO', bool]) # => True
print(env['FOO', int]) # => 123
print(env['FOO', float]) # => 123.0
print(env['FOO', str]) # => '[foo, bar, baz, 1, 2, 3]'
print(env['FOO', tuple]) # => ('foo', 'bar', 'baz', 1, 2, 3)
print(env['FOO', list]) # => ['foo', 'bar', 'baz', 1, 2, 3]
print(env['FOO', dict]) # => {} # TODO:  {0: 'foo', 1: 'bar', 2: 'baz', 3: 1, 4: 2, 5: 3}

print('---')

env['FOO'] = {'foo': 1, 'bar': 2, 'baz': 3}

print(env['FOO']) # => '{foo:1,bar:2,baz:3}' # REVIEW: handle nested json
print(env['FOO', bool]) # => True
print(env['FOO', int]) # => 123
print(env['FOO', float]) # => 123.0
print(env['FOO', str]) # => '{foo: 1, bar: 2, baz: 3}'
print(env['FOO', tuple]) # => ({0: 'foo', 1: 'bar', 2: 'baz', 3: 1, 4: 2, 5: 3})
print(env['FOO', list]) # => [{0: 'foo', 1: 'bar', 2: 'baz', 3: 1, 4: 2, 5: 3}]
print(env['FOO', dict]) # => {'foo': 1, 'bar': 2, 'baz': 3}

# etc.

print('---')

env.inspect()

print('---')

env.print()

print('---')
