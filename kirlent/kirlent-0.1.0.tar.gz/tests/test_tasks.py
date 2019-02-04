from pytest import fixture

from pathlib import Path
from time import sleep

from kirlent.tasks import TaskManager


MTIME_DELAY = 0.1


@fixture(scope="module")
def task_manager(kirlent_env):
    """A task manager for generating and running test tasks."""
    deps = Path(kirlent_env.src.parent, "tasks.db")
    yield TaskManager(kirlent_env.src, kirlent_env.out, deps=deps)


def test_create_build_folders_should_create_non_existing_unit(task_manager, unit1):
    assert not unit1.out.exists()
    task_manager.run("create_build_folders:unit1")
    assert unit1.out.exists()


def test_create_build_folders_should_not_touch_existing_unit(task_manager, unit1):
    unit1.out.mkdir()
    mtime_orig = unit1.out.stat().st_mtime_ns
    sleep(MTIME_DELAY)
    task_manager.run("create_build_folders:unit1")
    assert unit1.out.stat().st_mtime_ns == mtime_orig


def test_create_build_folders_default_should_create_all_units(task_manager, unit1, unit2):
    assert not unit1.out.exists()
    assert not unit2.out.exists()
    task_manager.run("create_build_folders")
    assert unit1.out.exists()
    assert unit2.out.exists()


def test_clean_build_folders_should_delete_unit_with_contents(task_manager, unit1):
    unit1.out.mkdir()
    Path(unit1.out, "index.txt").touch()
    task_manager.run("clean_build_folders:unit1")
    assert not unit1.out.exists()


def test_clean_build_folders_should_not_fail_if_unit_does_not_exist(task_manager, unit1):
    assert not unit1.out.exists()
    exit_code = task_manager.run("clean_build_folders:unit1")
    assert exit_code == 0


def test_clean_build_folders_default_should_delete_all_unit_folders(task_manager, unit1, unit2):
    unit1.out.mkdir()
    unit2.out.mkdir()
    task_manager.run("clean_build_folders")
    assert not unit1.out.exists()
    assert not unit2.out.exists()


def test_generate_revealjs_sources_should_generate_file_with_extension_rv(task_manager, unit1):
    assert not unit1.out.exists()
    task_manager.run("generate_revealjs_sources:unit1")
    assert Path(unit1.out, "slides.en.rv").exists()


def test_generate_revealjs_sources_should_not_regenerate_if_sources_not_modified(
    task_manager, unit1
):
    assert not unit1.out.exists()
    task_manager.run("generate_revealjs_sources:unit1")
    mtime_orig = Path(unit1.out, "slides.en.rv").stat().st_mtime_ns
    sleep(MTIME_DELAY)
    task_manager.run("generate_revealjs_sources:unit1")
    assert Path(unit1.out, "slides.en.rv").stat().st_mtime_ns == mtime_orig


def test_generate_revealjs_sources_should_regenerate_if_sources_modified(task_manager, unit1):
    assert not unit1.out.exists()
    task_manager.run("generate_revealjs_sources:unit1")
    mtime_orig = Path(unit1.out, "slides.en.rv").stat().st_mtime_ns
    sleep(MTIME_DELAY)
    Path(unit1.src, "slides.en.rst").write_text("..")
    task_manager.run("generate_revealjs_sources:unit1")
    assert Path(unit1.out, "slides.en.rv").stat().st_mtime_ns > mtime_orig


def test_generate_revealjs_sources_should_regenerate_if_parts_file_modified(
    task_manager, unit3
):
    assert not unit3.out.exists()
    task_manager.run("generate_revealjs_sources:unit3")
    mtime_orig = Path(unit3.out, "slides.en.rv").stat().st_mtime_ns
    sleep(MTIME_DELAY)
    Path(unit3.src, "parts.txt").write_text("unit1\n")
    task_manager.run("generate_revealjs_sources:unit3")
    assert Path(unit3.out, "slides.en.rv").stat().st_mtime_ns > mtime_orig


def test_generate_revealjs_sources_should_regenerate_if_part_modified(
    task_manager, unit1, unit3
):
    assert not unit3.out.exists()
    task_manager.run("generate_revealjs_sources:unit3")
    mtime_orig = Path(unit3.out, "slides.en.rv").stat().st_mtime_ns
    sleep(MTIME_DELAY)
    Path(unit1.src, "slides.en.rst").write_text("..")
    task_manager.run("generate_revealjs_sources:unit3")
    assert Path(unit3.out, "slides.en.rv").stat().st_mtime_ns > mtime_orig
