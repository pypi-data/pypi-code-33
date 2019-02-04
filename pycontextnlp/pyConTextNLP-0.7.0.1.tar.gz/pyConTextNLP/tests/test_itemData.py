import pyConTextNLP.itemData as itemData
from pyConTextNLP.itemData import contextItem
from pathlib import PurePath
import os
import pytest


@pytest.fixture(scope="session")
def get_tmp_dirs():
    pass

def test_get_fileobj_1():
    fobj = PurePath(PurePath(os.path.abspath(__file__)).parent, "..", "..", "KB", "test.yml")
    yaml_fo = itemData._get_fileobj(str(fobj))
    assert yaml_fo

def test_get_fileobj_2():
    wdir = PurePath(os.path.abspath(__file__))#, "..", "..", "KB")
    fobj = PurePath(wdir.parent, "..", "..", "KB", "test.yml")
    yfo = itemData._get_fileobj("file://"+str(fobj))
    assert yfo

def test_get_fileobj_3():
    yfo = itemData._get_fileobj(
            "https://raw.githubusercontent.com/chapmanbe/pyConTextNLP/master/KB/test.yml")
    assert yfo

def test_get_items():
    items = itemData.get_items(str(PurePath(PurePath(os.path.abspath(__file__)).parent, "..", "..", "KB", "test.yml")))
    assert isinstance(items,list)

def test_get_items_2():
    items = itemData.get_items(str(PurePath(PurePath(os.path.abspath(__file__)).parent, "..", "..", "KB", "test.yml")))
    assert isinstance(items[0],contextItem)

def test_get_instantiateFromCSVtoitemData_1():
    items = itemData.instantiateFromCSVtoitemData(str(PurePath(PurePath(os.path.abspath(__file__)).parent, "..", "..", "KB", "test.tsv")))
    assert isinstance(items,list)
def test_get_instantiateFromCSVtoitemData_2():
    items = itemData.instantiateFromCSVtoitemData(str(PurePath(PurePath(os.path.abspath(__file__)).parent, "..", "..", "KB", "test.tsv")))
    assert isinstance(items[0],contextItem)
