from os.path import join
from tempfile import NamedTemporaryFile, TemporaryDirectory

import pytest
from shapely.geometry import Point

from spaten import Feature, File


def test_parse():
    with File('spaten/testfiles/polygon.spaten') as f:
        for feature in f:
            assert isinstance(feature, Feature)

    with File('spaten/testfiles/two_blocks.spaten') as f:
        for feature in f:
            assert isinstance(feature, Feature)


def test_tag_serializer():
    with NamedTemporaryFile() as tmp:
        f = File(tmp.name)
        r = f.serialize_tags({'banana': 1})
        assert r[0].key == 'banana'
        assert r[0].type == 1


def test_empty():
    with NamedTemporaryFile() as tmp:
        with File(tmp.name):
            pass
        assert tmp.read(4) == b'SPAT'


def test_empty_readonly():
    with NamedTemporaryFile() as tmp:
        with pytest.raises(EOFError):
            with File(tmp.name, readonly=True):
                pass


def test_write_file_stream():
    with NamedTemporaryFile() as tmp:
        with File(tmp):
            pass
        tmp.seek(0, 0)
        assert tmp.read(4) == b'SPAT'


def test_new_file_path():
    with TemporaryDirectory() as td:
        with File(join(td, 'foo.spaten')) as spat:
            spat.append(Feature(Point(10, 10), {}))


def test_append():
    with NamedTemporaryFile() as tmp:
        with File(tmp) as spat:
            spat.append(Feature(Point(10, 10), {}))


def test_flush_block():
    with NamedTemporaryFile() as tmp:
        with File(tmp) as f:
            for n in range(File.blocksize):
                f.append(Feature(Point(0, 0), {}))

            assert f._wr_buf == []


def test_direct_iteration():
    for feature in File('spaten/testfiles/polygon.spaten'):
        assert isinstance(feature, Feature)
