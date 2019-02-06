import pytest
from tempfile import NamedTemporaryFile
from clav.hash import hashf, hashs, checkhash

pytestmark = pytest.mark.smoke

data = '''
The lowercase letters 'abcdefghijklmnopqrstuvwxyz'. This value is not
locale-dependent and will not change.
'''
alg = 'sha512'
hash = 'd1da70acc74f64cf428a129a0507ed9113e1887528aadb02a7c887b40d3bdedfb3f1423b65a3a950bc5a9aad8be0eaa48ac70629b1cc9eed900bb39cb3c0574b'
no_such_file = '/asdasdasd/adasdad/qweqda/sda/dqqdada'

class TestHashs:

  def test_valid(self):
    assert hashs(data, alg) == hash

  def test_invalid(self):
    with pytest.raises(TypeError):
      hashs(object(), alg)
    with pytest.raises(ValueError):
      hashs(data, data)

@pytest.fixture
def data_file():
  with NamedTemporaryFile('w') as f:
    f.write(data)
    f.flush()
    yield f.name

class TestHashf:

  def test_valid(self, data_file):
    assert hashf(data_file, alg) == hash

  def test_invalid(self, data_file):
    with pytest.raises(FileNotFoundError):
      hashf(no_such_file, alg)
    with pytest.raises(ValueError):
      hashf(data_file, no_such_file)

class TestCheckhash:

  def test_valid(self, data_file):
    checkhash(data_file, alg, hash)

  def test_invalid(self, data_file):
    with pytest.raises(FileNotFoundError):
      checkhash(no_such_file, alg, hash)
    with pytest.raises(ValueError):
      checkhash(data_file, no_such_file, sum)
    with pytest.raises(checkhash.error):
      checkhash(data_file, alg, no_such_file)
