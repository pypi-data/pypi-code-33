import conficus


def test_wild_multiline_sql(cfg_pth):

    lines = conficus.read_config(str(cfg_pth['wilderness']))
    config = conficus._parse(lines)

    value = config['config.sequence_po_sql']

    assert value.multiline is True
    assert len(value.raw_value) == 9
    assert value.raw_value[8].startswith('FFD.')
