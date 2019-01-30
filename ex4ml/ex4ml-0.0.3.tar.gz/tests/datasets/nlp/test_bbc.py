"""Test out loading bbc data
"""

from ex4ml.datasets.nlp.bbc import load_bbc, load_bbc_sport


def test_load_bbc():
    """Test loading bbc dataset
    """
    bbc = load_bbc()
    for article in bbc:
        assert isinstance(article.value, str)
        assert article.targets["topic"] in ["business", "entertainment", "politics", "sport", "tech"]
    assert len(bbc) == 2225


def test_load_bbc_sport():
    """Test loading bbc sport dataset
    """
    sport = load_bbc_sport()
    for article in sport:
        assert isinstance(article.value, str)
        assert article.targets["topic"] in ["athletics", "cricket", "football", "rugby", "tennis"]
    assert len(sport) == 737
