import os
import sys
import json
import helper
from elcato import settings
from elcato.helpers import load_template, loadconfig
from elcato import build_file, build
from elcato.helpers import handle_config


# TODO take out hard coded posts folder
def test_parse_single_file_to_json():
    destination, config = helper.test_setup(
        "parse-single-json-file/", "elcato-json.yaml"
    )

    source = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(source, "fixtures", "test_document_01_valid.org")

    settings.IGNORED_TAGS = ""
    doc = build_file(filename, source, destination, ext=settings.TEMPLATE.EXT)
    settings.IGNORED_TAGS = "draft"

    destination_full = f"{destination}posts/fixtures/test-document-01-valid.json"
    with open(destination_full, "r") as fp:
        value = json.loads(fp.read())
        assert value.get("title") == " Test document"

    assert doc.path == "/posts/fixtures"
    assert doc.relative == "../../"
    assert doc.absolute == "posts/fixtures"


# TODO take out hard coded posts folder
def test_enaml_template():
    source = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(source, "fixtures")
    for ext in ["json", "enaml", "jinja"]:
        config = loadconfig(config_path, name=f"elcato-{ext}.yaml")
        print(ext)
        assert settings.TEMPLATE is not None
        root = os.path.abspath(f"{source}/../")
        build(root, f"/tmp/{ext}/", config)


# TODO take out hard coded posts folder
def test_parse_to_json_index():
    source = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(source, "fixtures")
    config = loadconfig(config_path, name="elcato-json.yaml")
    destination = "/tmp/"
    root = os.path.abspath(f"{source}/../")
    build(root, destination, config)
    assert settings.IGNORED_TAGS == "draft"
    index_path = f"{destination}index.json"
    with open(index_path, "r") as fp:
        value = json.loads(fp.read())
        assert value.get("title") == "Index"
        assert len(value.get("cards")) == 4
        paths = [p.get("path") for p in value.get("cards")]
        absolute = [p.get("absolute") for p in value.get("cards")]
        relative = [p.get("relative") for p in value.get("cards")]

        assert paths == [
            "/posts/elcato/posts",
            "/posts/elcato/posts",
            "/posts/elcato/posts",
            "/posts/",
        ]
        assert absolute == [
            "posts/elcato/posts",
            "posts/elcato/posts",
            "posts/elcato/posts",
            "posts/",
        ]
        assert relative == ["../../", "../../", "../../", "../../"]


# TODO take out hard coded posts folder
def test_parse_to_json_pages():
    source = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(source, "fixtures")
    config = loadconfig(config_path, name="elcato-json.yaml")
    destination = "/tmp/"
    root = os.path.abspath(f"{source}/../")
    build(root, destination, config)

    pages = {
        "blog-hosting-guides.json": {
            "title": " Hosting your Blog",
            "path": "..//posts/elcato/posts",
            "absolute": "posts/elcato/posts",
            "relative": "../../",
        },
        "org-advanced-markup-reference.json": {
            "title": " Org Markup Advanced Reference",
            "path": "..//posts/elcato/posts",
            "absolute": "posts/elcato/posts",
            "relative": "../../",
        },
        "org-markup-reference.json": {
            "title": " Org Markup Quick Reference",
            "path": "..//posts/elcato/posts",
            "absolute": "posts/elcato/posts",
            "relative": "../../",
        },
    }
    for page, expected in pages.items():
        page_path = f"{destination}posts/elcato/posts/{page}"
        with open(page_path, "r") as fp:
            value = json.loads(fp.read())
            assert value.get("title") == expected.get("title")
            assert value.get("path") == expected.get("path")
            assert value.get("relative") == expected.get("relative")
            assert value.get("absolute") == expected.get("absolute")
