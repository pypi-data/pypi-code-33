"""Tests for digest.py"""
import pytest
from .context import rpg
from rpg import enzyme
from rpg import rule

def test_enzyme(tmpdir):
    """Test class 'Enzyme'"""
    # First enzyme: cut after D not precedeed by S
    dict_rule = {}
    rule_txt = "(D,)"
    dict_rule[rule_txt] = True
    exc_txt = "(S)(D,)"
    dict_rule[exc_txt] = False
    all_rules = rule.create_rules(dict_rule)
    enz0 = enzyme.Enzyme(-1, "fake_enzyme1", all_rules)

    # Test function '__repr__()'
    res = enz0.__repr__()
    assert res == "Id: -1\nName: fake_enzyme1\nRatio Miscleavage: 0.00%\nR"\
                  "ules: [index=0\nletter=D\ncut=True\npos=1\n\tindex=-1\n\tl"\
                  "etter=S\n\tcut=False\n\tpos=-1\n]\n"

    dict_rule = {}
    rule_txt = "(D,)"
    dict_rule[rule_txt] = True
    exc_txt = "(S)(D,)"
    dict_rule[exc_txt] = False
    all_rules = rule.create_rules(dict_rule)
    enz1 = enzyme.Enzyme(-1, "fake_enzyme1", all_rules)
    # Second enzyme: cut after S
    dict_rule = {}
    rule_txt = "(S,)"
    dict_rule[rule_txt] = True
    all_rules = rule.create_rules(dict_rule)
    enz2 = enzyme.Enzyme(-1, "fake_enzyme2", all_rules)

    # Test function '__eq__()'
    assert enz0 == enz1
    assert enz0 != enz2

    """Test function
    'write_enzyme_in_user_file(self, enz_file=DEFUSERENZFILE)'
    """
    output_file = tmpdir.join("test_enzuser.py")
    dict_rule = {}
    rule_txt = "(D)(E,)"
    dict_rule[rule_txt] = True
    all_rules = rule.create_rules(dict_rule)
    new_enz = enzyme.Enzyme(-1, "fake_enzyme", all_rules)
    new_enz.write_enzyme_in_user_file(str(output_file))
    assert output_file.read() == '\n\n\n# User-defined enzyme fake_enzyme\nEN'\
                                 'Z = []\n\nE_1 = rule.Rule(0, "E", False, 1)'\
                                 ' # Never cleaves after E, except...\nD_E_1M'\
                                 '1 = rule.Rule(-1, "D", True, -1) # Always c'\
                                 'leaves after E, preceded by D, except...\nE'\
                                 '_1.rules.append(D_E_1M1)\nENZ.append(E_1)\n'\
                                 '\nENZYME = enzyme.Enzyme(CPT_ENZ, "fake_enz'\
                                 'yme", ENZ, 0)\n# Add it to available enzyme'\
                                 's\nAVAILABLE_ENZYMES_USER.append(ENZYME)\nC'\
                                 'PT_ENZ += 1\n'

def test_check_enzyme_name():
    """Test function 'check_enzyme_name(name_new_enz, all_name_enz)'."""

    # Already taken names
    all_name = ["pwet", "poulpe"]

    # Correct name
    seq_name = "0AzeRTY"
    res = enzyme.check_enzyme_name(seq_name, all_name)
    assert res is True

    # The enzyme name is already taken
    seq_name = "pwet"
    res = enzyme.check_enzyme_name(seq_name, all_name)
    assert res is False

    # No \t \n \r \f \v
    not_allowed = ["\t", "\\t", "\n", "\\n", "\r", "\\r", "\f", "\\f", "\v",
                   "\\v", " "]
    for i in not_allowed:
        seq_name = "AZE" + i + "RTY"
        res = enzyme.check_enzyme_name(seq_name, all_name)
        assert res is False

    # The enzyme name is empty
    seq_name = ""
    res = enzyme.check_enzyme_name(seq_name, all_name)
    assert res is False

'''
def test_user_creation_enzyme(capsys, monkeypatch):
    """Test function 'user_creation_enzyme()'"""
    monkeypatch.setattr(builtins.input, "Mark")
    i = input("What is your name?")
    assert i == "Mark"

    
    inputs = [10, 'y']
    input_generator = (i for i in inputs)
    monkeypatch.setitem('__builtins__.input', lambda prompt: next(input_generator))
    core.user_creation_enzyme()
    out, err = capsys.readouterr()
    print(out)
    print(err)
    assert input('how many?') == 10
    assert input('you sure?') == 'y'
'''
