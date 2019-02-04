from pathlib import Path

from kirlent.utils import relative_path


def test_relative_path_target_in_same_folder_should_be_target_name():
    assert relative_path(Path("d1", "f"), Path("d1")).parts == ("f",)


def test_relative_path_target_in_child_folder_should_start_with_child():
    assert relative_path(Path("d1", "d2", "f"), Path("d1")).parts == ("d2", "f")


def test_relative_path_target_in_grandchild_folder_should_start_with_two_children():
    assert relative_path(Path("d1", "d2", "d3", "f"), Path("d1")).parts == ("d2", "d3", "f")


def test_relative_path_target_in_parent_folder_should_start_with_double_dots():
    assert relative_path(Path("d1", "f"), Path("d1", "d2")).parts == ("..", "f")


def test_relative_path_target_in_grandparent_folder_should_start_with_two_double_dots():
    assert relative_path(Path("d1", "f"), Path("d1", "d2", "d3")).parts == ("..", "..", "f")


def test_relative_path_target_in_diagonal_folder_should_go_up_and_down():
    assert relative_path(Path("d1", "d2", "f"), Path("d1", "d3")).parts == ("..", "d2", "f")
