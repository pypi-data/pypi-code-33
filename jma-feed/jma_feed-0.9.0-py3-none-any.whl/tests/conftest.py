"""Unit tests configuration file."""
import log
import pytest
from pkg_resources import resource_string


def pytest_configure(config):
    """Disable verbose output when running tests."""
    log.init(debug=True)

    terminal = config.pluginmanager.getplugin('terminal')

    class QuietReporter(terminal.TerminalReporter):  # type: ignore
        """Reporter that only shows dots when running tests."""

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.verbosity = 0
            self.showlongtestinfo = False
            self.showfspath = False

    terminal.TerminalReporter = QuietReporter


@pytest.fixture()
def feed_samples():
    sample_regular_feed = resource_string('jma_feed.tests.resources', 'sample_regular.xml').decode(
        'utf-8'
    )
    yield (sample_regular_feed,)


@pytest.fixture()
def report_samples():
    sample_mete1 = resource_string('jma_feed.tests.resources', 'sample_mete1.xml').decode('utf-8')
    sample_mete2 = resource_string('jma_feed.tests.resources', 'sample_mete2.xml').decode('utf-8')
    sample_seis1 = resource_string('jma_feed.tests.resources', 'sample_seis1.xml').decode('utf-8')
    sample_volc1 = resource_string('jma_feed.tests.resources', 'sample_volc1.xml').decode('utf-8')
    yield (sample_mete1, sample_mete2, sample_seis1, sample_volc1)
