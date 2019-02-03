from conficus.parse import ConfigValue


def test_config_value_single_line():
    cfgval = ConfigValue('random value')

    assert cfgval.multiline is False
    assert cfgval.value == 'random value'


def test_config_value_multiline():
    cfgval = ConfigValue('A multiline value')
    cfgval.add('that has multiple lines.')

    assert cfgval.multiline is True
    assert cfgval.value == 'A multiline value\nthat has multiple lines.'
