import os
from elcato import build_file
from elcato.helpers import handle_config


# TODO take out hard coded posts folder
def test_parse_single_file():
    source = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(source, 'fixtures', 'test_document_01.org')
    handle_config(os.path.join(source, 'fixtures', 'elcato.yaml'))
    doc = build_file(filename, source, '/tmp/')
    assert doc.path == '/posts/fixtures'
    assert doc.relative == '../../'
    assert doc.absolute == 'posts/fixtures'

