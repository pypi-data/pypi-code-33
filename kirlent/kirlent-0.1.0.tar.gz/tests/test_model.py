from pytest import fixture

from pathlib import Path

from kirlent.model import ContentHierarchy


@fixture(scope="module")
def kirlent_content(kirlent_env):
    """A content hierarchy that stores the content sources."""
    return ContentHierarchy(kirlent_env.src)


def test_content_hierarchy_path_should_be_absolute(kirlent_content):
    assert str(kirlent_content.root)[0] == "/"


def test_content_hierarchy_should_pick_up_units(kirlent_content, unit1):
    assert kirlent_content.units.get("unit1") is not None


def test_content_hierarchy_should_ignore_non_folders_as_units(kirlent_content):
    Path(kirlent_content.root, "unit").touch()
    assert kirlent_content.units.get("unit") is None
    Path(kirlent_content.root, "unit").unlink()


def test_content_hierarchy_should_ignore_sub_folders_as_units(kirlent_content, unit1):
    Path(unit1.src, "unit1a").mkdir()
    assert kirlent_content.units.get("unit1a") is None


def test_unit_source_path_should_be_absolute(kirlent_content, unit1):
    assert str(kirlent_content.units.get("unit1").src)[0] == "/"


def test_unit_should_have_reference_to_hierarchy(kirlent_content, unit1):
    assert kirlent_content.units.get("unit1").root == kirlent_content


def test_unit_without_parts_should_have_empty_list_of_parts(kirlent_content, unit1):
    assert kirlent_content.units.get("unit1").parts == []


def test_unit_with_parts_should_have_list_of_part_slugs(kirlent_content, unit3):
    assert kirlent_content.units.get("unit3").parts == ["unit1", "unit2"]


def test_unit_slug_should_be_same_as_folder_basename(kirlent_content, unit1):
    assert kirlent_content.units.get("unit1").slug == "unit1"


def test_unit_sources_should_be_sequence_of_absolute_paths(kirlent_content, unit1):
    unit = kirlent_content.units.get("unit1")
    assert list(unit.sources(medium="slides", lang="en")) == [
        Path(unit1.src, "slides.en.rst").absolute()
    ]


def test_unit_sources_nonexisting_language_should_be_included(kirlent_content, unit1):
    unit = kirlent_content.units.get("unit1")
    assert list(unit.sources(medium="slides", lang="tr")) == [
        Path(unit1.src, "slides.tr.rst").absolute()
    ]


def test_unit_sources_with_parts_should_be_sequence_of_part_paths(
    kirlent_content, unit1, unit2, unit3
):
    unit = kirlent_content.units.get("unit3")
    assert list(unit.sources(medium="slides", lang="en")) == [
        Path(unit1.src, "slides.en.rst").absolute(),
        Path(unit2.src, "slides.en.rst").absolute(),
    ]
