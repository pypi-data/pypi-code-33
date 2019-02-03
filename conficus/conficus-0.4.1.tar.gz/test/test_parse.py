import conficus
from conficus.parse import ConfigDict
from conficus.parse import ConfigValue
from conficus.parse import parse


def test_dict_contains():

    d = ConfigDict()
    d['one'] = ConfigDict()
    d['one']['two'] = ConfigDict()
    d['one']['two']['name'] = 'name'

    assert 'one' in d
    assert 'two' not in d
    assert 'one.two' in d
    assert 'one.three' not in d
    assert 'one.two.name' in d
    assert 'one.two.who' not in d


# TODO: Do we want to do this?
# Originally had this requirement, but think we
# removed it and just let it be ignored.
# def test_invalid_indent():
#    # raw_lines = [
#        # '[section]\n',
#        # '# comment line\n',
#        # '      a line on its own.\n',
#        # ]
#
#    # with pytest.raises(Exception):
#        # parse(raw_lines)
#

def test_dict_values(raw_cfg):
    items = [i for i in raw_cfg.walk_values()]
    assert len(items) == 11
    assert items[0].value == 'true'
    assert items[1].value == 'penguins for stanley'
    assert items[10].value == '1'


def test_root_values(raw_cfg):
    assert raw_cfg['root_value'].value == 'true'


def test_section_parsing(raw_cfg):

    assert isinstance(raw_cfg, dict)

    assert 'root_section' in raw_cfg
    assert 'root.leaf' in raw_cfg
    assert 'root.leaf.sub' in raw_cfg
    assert 'with_opt' in raw_cfg


def test_section_defaults(raw_cfg):
    assert raw_cfg['root_section'] == {}

    assert raw_cfg['root']['leaf'] == {'sub': {}}
    assert raw_cfg['root']['leaf']['sub'] == {}

    assert raw_cfg['root.leaf'] == {'sub': {}}
    assert raw_cfg['root.leaf.sub'] == {}


def test_raw_option_values(raw_cfg):
    assert raw_cfg['with_opt']['name'].value == 'penguins for stanley'
    assert raw_cfg['with_opt']['hero'].value == 'crosby'
    assert raw_cfg['with_opt']['game'].value == '7'


def test_raw_multiline_option_values(raw_cfg):
    assert isinstance(raw_cfg['with_opt.multiline'], ConfigValue)
    assert raw_cfg['with_opt.multiline'].multiline


def test_root_sectionless_values():
    cfgtxt = ('name = Bartholemu Bittersnorn\n'
              'age = 45')
    cfg = parse(conficus.read_config(cfgtxt))

    assert 'name' in cfg
    assert 'age' in cfg

    assert cfg['name'].value == 'Bartholemu Bittersnorn'
    assert cfg['age'].value == '45'
