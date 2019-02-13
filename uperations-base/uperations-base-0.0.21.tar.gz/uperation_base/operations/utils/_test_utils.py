
from ..utils import *
import os
from contracts.interface import ContractNotRespected
import shutil
from vendors.uperations.operations.library import LibraryException

def test_library_exists_false(tmpdir):
    p = tmpdir.mkdir("tmp_operations")
    assert len(p.listdir()) == 0
    assert not library_exists('new_library',os.path.dirname(p))
    return

def test_library_exists_true(tmpdir):
    p = tmpdir.mkdir("tmp_operations")
    p.mkdir('new_library')
    assert library_exists('new_library',str(p))
    return

def test_library_exists_missing_dir(tmpdir):
    p = tmpdir.mkdir("tmp_operations")
    try:
        library_exists('new_library', os.path.join(p,'tmp'))
    except FileNotFoundError:
        assert True
    return

def test_library_exists_no_missing_dir(tmpdir):
    p = tmpdir.mkdir("tmp_operations")
    p.mkdir('tmp')
    try:
        library_exists('new_library', os.path.join(p,'tmp'))
        assert True
    except FileNotFoundError:
        assert False
    return

def test_library_exists_name_int(tmpdir):
    p = tmpdir.mkdir("tmp_operations")
    p.mkdir('tmp')

    try:
        library_exists(1,os.path.join(p,'tmp'))
        assert False
    except ContractNotRespected:
        assert True
    return

def test_library_exists_name_dict(tmpdir):
    p = tmpdir.mkdir("tmp_operations")
    p.mkdir('tmp')

    try:
        library_exists({},os.path.join(p,'tmp'))
        assert False
    except ContractNotRespected:
        assert True
    return

def test_library_exists_out_dir_dict(tmpdir):
    p = tmpdir.mkdir("tmp_operations")
    p.mkdir('tmp')

    try:
        library_exists("test",{})
        assert False
    except ContractNotRespected:
        assert True
    return

def test_library_exists_out_dir_int(tmpdir):
    p = tmpdir.mkdir("tmp_operations")
    p.mkdir('tmp')

    try:
        library_exists("test",0)
        assert False
    except ContractNotRespected:
        assert True
    shutil.rmtree(p)
    return

def test_replace_placeholders_in_file(tmpdir):
    p = tmpdir.mkdir("tmp_operations").join('__init__.py')
    placeholder = "TEST_PLACECHOLDER"
    p.write(placeholder)

    replace_placeholders_in_file(str(p),{placeholder:'new_value'})

    assert 'new_value' in p.read()
    assert not 'TEST_PLACECHOLDER' in p.read()
    os.remove(p)
    return

def test_library_create(tmpdir):
    p = tmpdir.mkdir("tmp_operations")

    template = p.mkdir('template')
    out_dir = p.mkdir('out_dir')
    open(os.path.join(template,'__init__.py'),'a').close()

    assert library_create('new_library',str(out_dir)) == os.path.join(out_dir,'new_library')
    try:
        library_create('new_library',str(out_dir)) == os.path.join(out_dir,'new_library')
        assert False
    except LibraryException:
        assert True
    shutil.rmtree(p)
    return

def test_to_camel_case():
    snake_str = "snake_str"
    assert to_camel_case(snake_str) == "SnakeStr"
    return
