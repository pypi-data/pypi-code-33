from ngramtg.ngram import NgramTextGen
from ngramtg.exceptions import \
    AccessViolationException, \
    InvalidCorpusFile, \
    NoCorpus, \
    NoUnprocessedCorpus

import pytest


@pytest.fixture
def with_test_instance():
    test_instance = NgramTextGen()
    return test_instance


def test_get_corpus_filename_set_with_constructor(tmp_path):
    test_dir = tmp_path / "corpus_file"
    test_dir.mkdir()
    test_file = test_dir / "corpus.txt"
    test_file.write_text("one fish two fish red fish blue fish")
    test = NgramTextGen(test_file)

    assert test.corpus_filename() == test_file


def test_filename_setter_and_getter(tmp_path, with_test_instance):
    test_dir = tmp_path / "corpus_file"
    test_dir.mkdir()
    test_file = test_dir / "corpus.txt"
    test_file.write_text("one fish two fish red fish blue fish")

    # By default there shouldn't be a file name
    assert with_test_instance.corpus_filename() is None

    # Test that we can set the file name to a valid file
    with_test_instance.set_corpus_filename(test_file)
    assert with_test_instance.corpus_filename() == test_file

    # Calling the setter without arguments shouldn't do anything
    with_test_instance.set_corpus_filename()
    assert with_test_instance.corpus_filename() == test_file

    with pytest.raises(InvalidCorpusFile) as err:
        with_test_instance.set_corpus_filename("/non-existing/path/and/file/")
        assert err.value == 0
        assert err.errisinstance(InvalidCorpusFile)

        # The file name should still be what we set before the exception
        assert with_test_instance.corpus_filename() == test_file

    # Calling the setter without arguments still shouldn't do anything
    with_test_instance.set_corpus_filename()
    assert with_test_instance.corpus_filename() == test_file


def test_preprocessing_of_corpus(with_test_instance):
    # Calling preprocess_corpus with no argument should return None
    assert with_test_instance.preprocess_corpus() is None

    test_corpus = ["One fish, two fish. red fish? blue fish!"]
    expected = ["One fish , two fish . red fish ? blue fish !"]

    assert with_test_instance.preprocess_corpus(test_corpus) == expected


def test_ngram_length(with_test_instance):
    # By default we want bigrams, so length should be 2
    assert with_test_instance.ngram_length() is 2

    # We can change the value
    with_test_instance.set_ngram_length(5)
    assert with_test_instance.ngram_length() == 5

    # We can change the value again
    with_test_instance.set_ngram_length(42)
    assert with_test_instance.ngram_length() == 42

    # Calling the setter without a value doesn't change anything
    with_test_instance.set_ngram_length()
    assert with_test_instance.ngram_length() == 42

    # Calling the setter with a negative value raises an exception
    with pytest.raises(ValueError) as err:
        with_test_instance.set_ngram_length(-1)
        assert err.errisinstance(ValueError)
        assert err.value == "Length `n` must be a positive number."


def test_corpus_setter_and_getter(with_test_instance):
    # Default corpus is empty
    assert with_test_instance.corpus() is None

    # Setter won't set anything if called without a value
    with_test_instance.set_corpus()
    assert with_test_instance.corpus() is None

    # Setting corpus to a list of tokens works is allowed
    with_test_instance.set_corpus(
        ["::START", "One", "fish",
         "two", "fish", "red", "fish",
         "blue", "fish", "::END"])
    expected_corpus = ["::START", "One", "fish", "two", "fish",
                       "red", "fish", "blue", "fish", "::END"]

    assert with_test_instance.corpus() is not None
    assert with_test_instance.corpus() == expected_corpus

    # Setter still won't set anything if called without a value
    with_test_instance.set_corpus()
    assert with_test_instance.corpus() == expected_corpus

    # Calling the setter with the wrong data type raises an exception
    with pytest.raises(AccessViolationException) as ave:
        with_test_instance.set_corpus("One fish two fish red fish blue fish")

        assert ave.errisinstance(AccessViolationException)


def test_ngrams_setter_and_getter(with_test_instance):
    # Default constructed instance shouldn't have any n-grams
    assert with_test_instance.ngrams() is None

    # Calling the setter without arguments shouldn't do anything
    with_test_instance.set_ngrams()
    assert with_test_instance.ngrams() is None

    test_ngrams = [['::START', 'One'], ['One', 'fish'], ['fish', 'two'],
                   ['two', 'fish'], ['fish', 'red'], ['red', 'fish'],
                   ['fish', 'blue'], ['blue', 'fish'], ['fish', '::END']]

    with_test_instance.set_ngrams(test_ngrams)
    assert with_test_instance.ngrams() == test_ngrams

    # Calling the setter without arguments still shouldn't do anything
    with_test_instance.set_ngrams()
    assert with_test_instance.ngrams() == test_ngrams


def test_sentence_getter_and_setter(with_test_instance):
    # Default constructed instance shouldn't have any sentences
    assert with_test_instance.sentence() is None

    # Calling the setter without arguments shouldn't do anything
    with_test_instance.set_sentence()
    assert with_test_instance.sentence() is None

    test_sentence = "Test"

    with_test_instance.set_sentence(test_sentence)
    assert with_test_instance.sentence() == test_sentence

    # Calling the setter without arguments still shouldn't do anything
    with_test_instance.set_sentence()
    assert with_test_instance.sentence() == test_sentence


def test_unprocessed_corpus_getter_and_setter(with_test_instance):
    # Default constructed instance shouldn't have an unprocessed corpus
    assert with_test_instance.unprocessed_corpus() is None

    # Calling the setter without arguments shouldn't do anything
    with_test_instance.set_unprocessed_corpus()
    assert with_test_instance.unprocessed_corpus() is None

    test_corpus = "This is content for a test only.\n" \
                  "One fish two fish red fish blue fish!"

    with_test_instance.set_unprocessed_corpus(test_corpus)
    assert with_test_instance.unprocessed_corpus() == test_corpus

    # Calling the setter without arguments still shouldn't do anything
    with_test_instance.set_unprocessed_corpus()
    assert with_test_instance.unprocessed_corpus() == test_corpus


def test_adding_structural_tokens(with_test_instance):
    # Calling add_structural_tokens on None raises exception
    with pytest.raises(NoUnprocessedCorpus) as err:
        with_test_instance.add_structural_tokens()
        assert err.errisinstance(NoUnprocessedCorpus)

    as_list = ["One fish two fish red fish blue fish"]
    expected = ["::START One fish two fish red fish blue fish ::END"]

    assert with_test_instance.add_structural_tokens(as_list) == expected


def test_auto_mode(tmp_path):
    test_dir = tmp_path / "corpus_file"
    test_dir.mkdir()
    test_file = test_dir / "corpus.txt"
    test_file.write_text("One fish two fish red fish blue fish\n")

    test_instance = NgramTextGen(test_file, auto=True)

    expected_frequency_map = {
        '::START': {'One': 1},
        'One': {'fish': 1},
        'fish': {'two': 1, 'red': 1, 'blue': 1, '::END': 1},
        'two': {'fish': 1}, 'red': {'fish': 1}, 'blue': {'fish': 1}}
    assert test_instance.frequency_map() == expected_frequency_map

    with pytest.raises(NoCorpus) as err:
        test_no_corpus = NgramTextGen(auto=True)
        assert test_no_corpus.corpus_filename() is None
        assert err.errisinstance(NoCorpus)

    test_manual_call = NgramTextGen(test_file, auto=False)
    test_manual_call.setup_everything()

    expected_ngrams = [['::START', 'One'], ['One', 'fish'], ['fish', 'two'],
                       ['two', 'fish'], ['fish', 'red'], ['red', 'fish'],
                       ['fish', 'blue'], ['blue', 'fish'], ['fish', '::END']]
    assert test_manual_call.ngrams() == expected_ngrams


def test_read_corpus_file(tmp_path, with_test_instance):
    test_dir = tmp_path / "corpus_file"
    test_dir.mkdir()
    test_file = test_dir / "corpus.txt"
    test_file.write_text("one fish two fish red fish blue fish\n"
                         "blue fish red fish two fish one fish")

    # Calling reader without a file name returns None
    assert with_test_instance.read_corpus_file() is None

    expected = ["one fish two fish red fish blue fish",
                "blue fish red fish two fish one fish"]
    assert with_test_instance.read_corpus_file(test_file) == expected


def test_frequency_map_getter_and_setter(with_test_instance):
    # Calling getter on default object returns None
    assert with_test_instance.frequency_map() is None

    # Calling setter without passing anything does nothing
    with_test_instance.set_frequency_map()
    assert with_test_instance.frequency_map() is None

    with_test_instance.set_unprocessed_corpus(
        ['One fish two fish red fish blue fish'])

    expected = {
        '::START': {'One': 1},
        'One': {'fish': 1},
        'fish': {'two': 1, 'red': 1, 'blue': 1, '::END': 1},
        'two': {'fish': 1}, 'red': {'fish': 1}, 'blue': {'fish': 1}}
    with_test_instance.set_frequency_map(expected)
    assert with_test_instance.frequency_map() == expected

    # Calling setter without passing anything still does nothing
    with_test_instance.set_frequency_map()
    assert with_test_instance.frequency_map() == expected


def test_create_sentence_sets_sentence_and_returns_it(tmp_path):
    test_dir = tmp_path / "corpus_file"
    test_dir.mkdir()
    test_file = test_dir / "corpus.txt"
    test_file.write_text("one fish two fish")

    test_instance = NgramTextGen(test_file, auto=True)

    assert test_instance.create_sentence() == test_instance.sentence()


def test_is_duplicate(tmp_path, with_test_instance):
    test_dir = tmp_path / "corpus_file"
    test_dir.mkdir()
    test_file = test_dir / "corpus.txt"
    test_file.write_text("One fish two fish red fish blue fish\n")

    test_instance = NgramTextGen(test_file, auto=True)

    assert test_instance.is_duplicate("One fish two fish red fish blue fish")
    assert not test_instance.is_duplicate("One fish")

    assert test_instance.is_duplicate("A fish", ["A fish"])
    assert not with_test_instance.is_duplicate("A fish")


def test_create_ngrams(with_test_instance):
    # Calling create_ngrams without a token list doesn't do anything
    assert with_test_instance.create_ngrams() is None


def test_tokenize(with_test_instance):
    # Calling tokenize without a corpus doesn't do anything
    assert with_test_instance.tokenize() is None


def test_module_():
    import ngramtg
    assert ngramtg.name == "ngramtg"
    assert ngramtg.author == "Paul Wicking"
    assert ngramtg.version == "2019.01"
    assert isinstance(ngramtg.version, str)
