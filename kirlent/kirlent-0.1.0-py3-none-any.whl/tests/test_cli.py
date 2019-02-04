from pytest import raises

import re

from pkg_resources import get_distribution

from kirlent import cli


def test_help_should_print_usage_and_exit(capsys):
    with raises(SystemExit):
        cli.main(argv=["kirlent", "--help"])
    out, err = capsys.readouterr()
    assert out.startswith("usage: ")


def test_version_should_print_version_number_and_exit(capsys):
    version = get_distribution("kirlent").version
    with raises(SystemExit):
        cli.main(argv=["kirlent", "--version"])
    out, err = capsys.readouterr()
    assert out == "kirlent %(ver)s\n" % {"ver": version}


# TODO: Add test for the case when src directory is given
# TODO: Add test for the case when out directory is given


def test_missing_command_should_print_usage_and_exit(capsys):
    with raises(SystemExit):
        cli.main(argv=["kirlent"])
    out, err = capsys.readouterr()
    assert re.match(r"^usage: .*required: command.*", err, re.DOTALL)


def test_invalid_command_should_print_usage_and_exit(capsys):
    with raises(SystemExit):
        cli.main(argv=["kirlent", "foo"])
    out, err = capsys.readouterr()
    assert re.match(r"^usage: .*invalid choice: 'foo'.*", err, re.DOTALL)


def test_unrecognized_argument_should_print_usage_and_exit(capsys):
    with raises(SystemExit):
        cli.main(argv=["kirlent", "--foo", "clean", "unit1"])
    out, err = capsys.readouterr()
    assert re.match(r"^usage: .*unrecognized arguments: --foo.*", err, re.DOTALL)


# TODO: Add test for rv command with unit glob
# TODO: Add test for rv command without unit glob


def test_rv_unrecognized_argument_should_print_usage_and_exit(capsys):
    with raises(SystemExit):
        cli.main(argv=["kirlent", "--foo", "rv", "unit1"])
    out, err = capsys.readouterr()
    assert re.match(r"^usage: .*unrecognized arguments: --foo.*", err, re.DOTALL)


# TODO: Add test for dt command with unit glob
# TODO: Add test for dt command without unit glob


def test_dt_unrecognized_argument_should_print_usage_and_exit(capsys):
    with raises(SystemExit):
        cli.main(argv=["kirlent", "--foo", "dt", "unit1"])
    out, err = capsys.readouterr()
    assert re.match(r"^usage: .*unrecognized arguments: --foo.*", err, re.DOTALL)


# TODO: Add test for clean command with unit glob
# TODO: Add test for clean command without unit glob


def test_clean_unrecognized_argument_should_print_usage_and_exit(capsys):
    with raises(SystemExit):
        cli.main(argv=["kirlent", "--foo", "clean", "unit1"])
    out, err = capsys.readouterr()
    assert re.match(r"^usage: .*unrecognized arguments: --foo.*", err, re.DOTALL)


# TODO: Add test for task command with valid task name


def test_task_invalid_name_should_print_error_and_exit(capsys):
    with raises(SystemExit):
        cli.main(argv=["kirlent", "task", "foo"])
    out, err = capsys.readouterr()
    assert re.match(r'^ERROR: .*invalid parameter: "foo".*', err, re.DOTALL)


def test_task_missing_name_should_print_usage_and_exit(capsys):
    with raises(SystemExit):
        cli.main(argv=["kirlent", "--foo", "task"])
    out, err = capsys.readouterr()
    assert re.match(r"^usage: .*required: name.*", err, re.DOTALL)


def test_task_unrecognized_argument_should_print_usage_and_exit(capsys):
    with raises(SystemExit):
        cli.main(argv=["kirlent", "--foo", "task", "create_build_folders"])
    out, err = capsys.readouterr()
    assert re.match(r"^usage: .*unrecognized arguments: --foo.*", err, re.DOTALL)
