import os
import helper
from elcato import settings
from elcato import build_file
from elcato.helpers import handle_config


# TODO take out hard coded posts folder
def test_parse_single_file():
    destination, config = helper.test_setup("parsing/", "elcato.yaml")

    source = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(source, "fixtures", "test_document_01_valid.org")
    #handle_config(os.path.join(source, "fixtures", "elcato.yaml"))
    settings.IGNORED_TAGS = ""
    doc = build_file(filename, source, "/tmp/")
    settings.IGNORED_TAGS = "draft"

    assert doc is not None
    assert doc.path == "/posts/fixtures"
    assert doc.relative == "../../"
    assert doc.absolute == "posts/fixtures"
