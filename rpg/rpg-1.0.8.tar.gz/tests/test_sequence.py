"""Tests for sequence.py"""
import pytest
from .context import rpg
from rpg import sequence

def test_sequence():
    """Test class 'Sequence'"""
    header = "fake_sequence"
    seq = "QWSDESDF"
    seq0 = sequence.Sequence(header, seq)

    # Test function '__repr__()'
    assert seq0.__repr__() == "Header: fake_sequence\nSequence: QWSDESDF\n"

    header = "fake_sequence"
    seq = "QWSDESDF"
    seq1 = sequence.Sequence(header, seq)

    header = "fake_sequdence"
    seq = "QWSDESDF"
    seq2 = sequence.Sequence(header, seq)

    header = "fake_sequence"
    seq = "QWSD>ESDF"
    seq3 = sequence.Sequence(header, seq)

    # Test function '__eq__()'
    assert seq0 == seq1
    assert seq0 != seq2
    assert seq0 != seq3

def test_check_sequence(capsys):
    """ Test function 'check_sequence(seq)'"""
    # Correct one
    assert sequence.check_sequence("aiHZODHUoh") == "AIHZODHUOH"

    # Bad symbol
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        sequence.check_sequence("a%HZODHUoh")
    _, err = capsys.readouterr()
    assert err == "Sequence Error: amino acid \"%\" in A%HZODHUOH not recogni"\
                  "zed.\n"
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 1
