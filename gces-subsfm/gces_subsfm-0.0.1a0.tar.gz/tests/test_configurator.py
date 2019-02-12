from gces_subsfm import Configurator

def test_dummy():
    """ Dummy test to get CI rolling."""
    config = Configurator()
    assert config.subscribers == []
