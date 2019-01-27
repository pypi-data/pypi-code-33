from click.testing import CliRunner
from rokit.__version__ import __version__
from rokit.cli import cli

def test_with_blank_argument():
    runner = CliRunner()
    result = runner.invoke(cli, None)
    assert result.exit_code == 0
    assert not result.exception

def test_full_version_option():
    runner = CliRunner()
    result = runner.invoke(cli, ['--version'])
    assert result.exit_code == 0
    assert not result.exception
    assert result.output == 'version: %s\n'% __version__

def test_short_version_option():
    runner = CliRunner()
    result = runner.invoke(cli, ['-v'])
    assert result.exit_code == 0
    assert not result.exception
    assert result.output == 'version: %s\n'% __version__


def test_single_final_url_should_return_headers():
    runner = CliRunner()
    result = runner.invoke(cli, ['https://github.com/'])
    assert result.exit_code == 0
    assert not result.exception
    assert 'Redirect 0 time(s): https://github.com/' in  result.output

def test_single_url_should_return_redirect_infos():
    runner = CliRunner()
    result = runner.invoke(cli, ['http://www.github.com'])
    assert result.exit_code == 0
    assert not result.exception
    assert 'Redirect 2 time(s): http://www.github.com -> https://www.github.com/ -> https://github.com/' in  result.output


def test_pair_url_should_match_expect_url_highlight_at_the_end():
    runner = CliRunner()
    result = runner.invoke(cli, ['http://www.github.com','https://github.com/'])
    assert result.exit_code == 0
    assert not result.exception
    assert 'Redirect 2 time(s): http://www.github.com -> https://www.github.com/ -> [https://github.com/]' in  result.output
    assert '[PASS] Request to http://www.github.com will redirect to https://github.com'

def test_pair_url_should_match_expect_url_highlight_in_the_middle():
    runner = CliRunner()
    result = runner.invoke(cli, ['http://www.github.com','https://www.github.com/'])
    assert result.exit_code == 0
    assert not result.exception
    assert 'Redirect 2 time(s): http://www.github.com -> [https://www.github.com/] -> https://github.com/' in  result.output
    assert '[PASS] Request to http://www.github.com will redirect to https://www.github.com/'

def test_pair_url_should_not_pass():
    runner = CliRunner()
    result = runner.invoke(cli, ['http://www.github.com','https://www.github.com/wizardbyron/'])
    assert result.exit_code == 1
    assert 'Redirect 2 time(s): http://www.github.com -> https://www.github.com/ -> https://github.com/' in  result.output
    assert '[FAIL] Request to http://www.github.com will not redirect to https://www.github.com/wizardbyron'