import pytest
import sys
from collections import MutableMapping
from clav.data import attr, dattr, rattr, ottr, dottr, rottr, remap, \
  merge, isexc, asbool
from clav.__tests__.datasets import name_dict

pytestmark = pytest.mark.smoke

# standard test data
_ = name_dict.copy()
_.update({
  'foo': 987, 'bar': [1,2,3,4], 'baz': {5,9,1,4,3},
  'zab': {'ricky': 'bobby', 'billy': 'ray'}, 123: 456, 1.23: 4.56,
  object(): object(), None: object(), object(): None, True: False, False: True
})

# (type, ctor_args, data_set)

# all standard tests are run on these
_standard = [
  (attr, (_,), _),
  (dattr, (None, _), _),
  (ottr, (_,), _),
  (dottr, (None, _), _),
]

# all standard tests except for _invalid tests are run on these, cf. TestDefault
_standard_default = _standard + [
  (dattr, (list, _), _),
  (dattr, (dict, _), _),
  (dattr, (set, _), _),
  (rattr, (_,), _),
  (dottr, (list, _), _),
  (dottr, (dict, _), _),
  (dottr, (set, _), _),
  (rottr, (_,), _),
]

@pytest.fixture(params = _standard)
def standard(request):
  '''
  Standard attribute types that don't do anything weird with missing attributes.
  '''
  return request.param

@pytest.fixture(params = _standard_default)
def standard_default(request):
  '''
  Standard attribute types plus the ones that do weird stuff with missing
  attributes.
  '''
  return request.param

class TestStandard:
  'Standard test for attributes classes.'

  def construct(self, args):
    cls, args, data = args
    return cls(*args), data

  def test_getitem_valid(self, standard_default):
    obj, data = self.construct(standard_default)
    for _ in data:
      assert obj[_] == data[_]

  def test_getitem_invalid(self, standard):
    obj, data = self.construct(standard)
    for _ in 'FOO', 'BAR':
      assert _ not in data
      with pytest.raises(KeyError):
        obj[_]

  def test_getattr_valid(self, standard_default):
    obj, data = self.construct(standard_default)
    for _ in data:
      if isinstance(_, str):
        assert getattr(obj, _) == data[_]

  def test_getattr_invalid(self, standard):
    obj, data = self.construct(standard)
    for _ in 'FOO', 'BAR':
      assert _ not in data
      with pytest.raises(AttributeError):
        getattr(obj, _)

  def test_get_valid(self, standard_default):
    obj, data = self.construct(standard_default)
    for _ in data:
      assert obj.get(_) == data.get(_)

  def test_get_invalid(self, standard):
    obj, data = self.construct(standard)
    for _ in 'FOO', 'BAR':
      assert _ not in data
      assert obj.get(_) == None

  def test_get_invalid_default(self, standard_default):
    obj, data = self.construct(standard_default)
    for (key, default) in ('FOO', 12321), ('BAR', 32123):
      assert key not in data
      assert obj.get(key, default) == default

  def test_copy(self, standard_default):
    obj, data = self.construct(standard_default)
    copy = obj.copy()
    assert isinstance(copy, obj.__class__)
    assert len(copy) == len(data)
    for _ in data:
      assert copy[_] == data[_]

@pytest.fixture(
  params = [
    # (type, ctor_args, factory, data_set)
    (dattr, (list, _), list, _),
    (dattr, (dict, _), dict, _),
    (dattr, (set, _), set, _),
    (dottr, (list, _), list, _),
    (dottr, (dict, _), dict, _),
    (dottr, (set, _), set, _),
    (rattr, (_,), rattr, _),
    (rottr, (_,), rottr, _),
  ],
)
def default(request):
  return request.param

class TestDefault:
  'Specialized invalid tests for default attributes classes.'

  def construct(self, args):
    cls, args, factory, data = args
    return cls(*args), factory, factory().__class__, data

  def test_getitem_invalid(self, default):
    obj, factory, factory_cls, data = self.construct(default)
    for _ in ('FOO', 'BAR'):
      assert _ not in data
      assert isinstance(obj[_], factory_cls)

  def test_getattr_invalid(self, default):
    obj, factory, factory_cls, data = self.construct(default)
    for _ in ('FOO', 'BAR'):
      assert _ not in data
      assert isinstance(obj[_], factory_cls)

  def test_get_invalid(self, default):
    obj, factory, factory_cls, data = self.construct(default)
    for _ in 'FOO', 'BAR':
      assert _ not in data
      assert isinstance(obj[_], factory_cls)

@pytest.fixture(
  params = [
    attr,
    ottr,
    lambda *_, **__: dattr(None, *_, **__),
    lambda *_, **__: dottr(None, *_, **__),
    rattr,
    rottr,
  ],
)
def remap_factory(request):
  return request.param

@pytest.fixture
def nested_dict1():
  return {
    'foo': {
      'bar': {
        'baz': 'boz',
      },
    },
    'oof': {
      'rab': {
        'zab': 'zob',
      },
    },
  }

@pytest.fixture
def nested_dict2():
  return {
    'crow': {
      'servo': {
        'gypsy': 'cambot',
      },
    },
    'septapus': {
      'brainulo': {
        'catclops': 'BRRRRRRICK FROG',
      },
    },
  }

class TestRemap:
  'Test remap().'

  def test_remap(self, remap_factory, nested_dict1):
    cls = type(remap_factory())
    data = nested_dict1
    rdata = remap(data, remap_factory)
    assert isinstance(rdata, cls)
    assert isinstance(rdata['foo'], cls)
    assert isinstance(rdata['foo']['bar'], cls)
    assert isinstance(rdata['foo']['bar']['baz'], str)
    assert rdata['foo']['bar']['baz'] == data['foo']['bar']['baz']
    assert isinstance(rdata['oof'], cls)
    assert isinstance(rdata['oof']['rab'], cls)
    assert isinstance(rdata['oof']['rab']['zab'], str)
    assert rdata['oof']['rab']['zab'] == data['oof']['rab']['zab']

class TestMerge:
  'Test merge().'

  def cmp(self, d1, d2):
    for _ in d1:
        assert _ in d2
        if isinstance(_, MutableMapping):
          self.cmp(d1[_], d2[_])
        else:
          assert d1[_] == d2[_]

  def test_clean_merge(self, nested_dict1, nested_dict2):
    d1 = nested_dict1
    d2 = nested_dict2
    d3 = merge(d1, d2)
    self.cmp(d1, d3)

  def test_dirty_merge(self, nested_dict1, nested_dict2):
    d1 = nested_dict1
    d2 = nested_dict2
    d2['foo'] = {'bar': 'goblorse'}
    d2['oof'] = {'rab': {'zab': 'wena'}}
    d3 = merge(d1, d2)
    with pytest.raises(AssertionError):
      self.cmp(d1, d3)
    self.cmp(d2, d3)

@pytest.fixture(params=[
  (None, None, None),
  ('abc', 123, 'u&me'),
  (123),
  ('stump'),
  (object()),
])
def invalid_exc(request):
  return request.param

class TestIsExc:
  'Test isexc().'

  def test_valid(self):
    _ = None
    try:
      raise Exception()
    except Exception:
      _ = sys.exc_info()
    assert isexc(_) == True

  def test_invalid(self, invalid_exc):
    assert isexc(invalid_exc) == False

@pytest.fixture(params = [
  ('', False),
  ('no', False),
  ('yes', True),
  ('0', False),
  ('1', True),
  ('off', False),
  ('on', True),
  (0, False),
  (1, True),
  (-1, True),
  (0.0, False),
  (0.1, True),
  (-0.1, True),
  (None, False),
  (object(), True),
])
def passing_bool(request):
  return request.param

@pytest.fixture(params = [
  'foo',
  'negative',
  'disable',
  'aksdjaslkdjalkdjadlja',
])
def failing_bool(request):
  return request.param

class TestAsBool:
  'Test asbool().'

  def test_valid(self, passing_bool):
    value, result = passing_bool
    assert asbool(value) == result

  def test_invalid(self, failing_bool):
    with pytest.raises(ValueError):
      asbool(failing_bool)
