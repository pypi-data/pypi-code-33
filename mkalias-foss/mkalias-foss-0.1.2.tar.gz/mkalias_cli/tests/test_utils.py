from mkalias_cli import utils


def test_check_path_of_dir_exists(tmpdir):
    assert utils.Path.check_path(tmpdir) == True


def test_check_path_of_file_exists(tmp_path):
    f = tmp_path / "test_file01"
    f.write_text("content")
    assert utils.Path.check_path(f) == True


def test_check_path_of_dir_not_exists(tmp_path):
    d = tmp_path / "foo"
    assert utils.Path.check_path(d) == False


def test_check_path_of_file_not_exists(tmp_path):
    f = tmp_path / "test_file01"
    assert utils.Path.check_path(f) == False
