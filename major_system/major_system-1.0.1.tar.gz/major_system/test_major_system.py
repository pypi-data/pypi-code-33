from major_system import major_system as ms
import pytest

@pytest.fixture
def dictfile():
  return ['abc', 'dog', 'Cat', 'tag', 'toggle', 'at', 'yell', 'well',
      'what', 'tall', 'deal', 'gill', 'gal', 'ick']

def assert_equal_except_order(left, right):
  assert len(left) == len(right)
  for i in left:
    assert i in right

def test_partitions():
  assert ms.partitions("a") == [["a"]]
  assert ms.partitions("ab") == [["ab"], ["a", "b"]]
  assert ms.partitions("abc") == [["abc"], ["a", "bc"], ["ab", "c"], ["a", "b", "c"]]
  assert ms.partitions("abcd") == [["abcd"], ["a", "bcd"], ["ab", "cd"], ["abc", "d"], ["a", "b", "cd"], ["a", "bc", "d"], ["ab", "c", "d"], ["a", "b", "c", "d"]]
  assert ms.partitions("a", 0) == []
  assert ms.partitions("ab", 1) == [["ab"]]
  assert ms.partitions("abc", 0) == []
  assert ms.partitions("abc", 1) == [["abc"]]
  assert ms.partitions("abc", 2) == [["abc"], ["a", "bc"], ["ab", "c"]]
  assert ms.partitions("abc", 3) == [["abc"], ["a", "bc"], ["ab", "c"], ["a", "b", "c"]]
  assert ms.partitions("abc", 4) == [["abc"], ["a", "bc"], ["ab", "c"], ["a", "b", "c"]]
  assert ms.partitions("abc", 5) == [["abc"], ["a", "bc"], ["ab", "c"], ["a", "b", "c"]]
  assert ms.partitions("abc", 6) == [["abc"], ["a", "bc"], ["ab", "c"], ["a", "b", "c"]]
  assert ms.partitions("abc", 7) == [["abc"], ["a", "bc"], ["ab", "c"], ["a", "b", "c"]]
  assert ms.partitions("abc", None) == [["abc"], ["a", "bc"], ["ab", "c"], ["a", "b", "c"]]
  assert ms.partitions("abcd") == [["abcd"], ["a", "bcd"], ["ab", "cd"], ["abc", "d"], ["a", "b", "cd"], ["a", "bc", "d"], ["ab", "c", "d"], ["a", "b", "c", "d"]]


def test_major_words(dictfile):
  assert [x for x in ms.major_words(dictfile, 17)] == ["dog", 'tag']
  assert [x for x in ms.major_words(dictfile, 175)] == ["toggle"]
  assert [x for x in ms.major_words(dictfile, 8)] == []
  assert [x for x in ms.major_words(dictfile, 5)] == ['yell', 'well']


def test_phrases_from_partition(dictfile):
  partition = [175]
  phrases = [x for x in ms.phrases_from_partition(dictfile, partition)]
  assert phrases == ['toggle']
  partition = [17, 5]
  phrases = [x for x in ms.phrases_from_partition(dictfile, partition)]
  assert phrases == ['dog yell', 'dog well', 'tag yell', 'tag well']
  partition = [1, 75]
  phrases = [x for x in ms.phrases_from_partition(dictfile, partition)]
  assert phrases == ['at gill', 'at gal', 'what gill', 'what gal']
  partition = [1, 7, 5]
  phrases = [x for x in ms.phrases_from_partition(dictfile, partition)]
  assert phrases == ['at ick yell', 'at ick well', 'what ick yell',
      'what ick well']
  partition = [15]
  phrases = [x for x in ms.phrases_from_partition(dictfile, partition)]
  assert phrases == ['tall', 'deal']
  partition = [7]
  phrases = [x for x in ms.phrases_from_partition(dictfile, partition)]
  assert phrases == ['ick']
  partition = [1, 5]
  phrases = [x for x in ms.phrases_from_partition(dictfile, partition)]
  assert phrases == ['at yell', 'at well', 'what yell', 'what well']
  partition = [1]
  phrases = [x for x in ms.phrases_from_partition(dictfile, partition)]
  assert phrases == ['at', 'what']
  partition = [5]
  phrases = [x for x in ms.phrases_from_partition(dictfile, partition)]
  assert phrases == ['yell', 'well']


def test_phrases(dictfile):
  phrases = [x for x in ms.phrases(dictfile, 15)]
  assert phrases == [
    'tall', 'deal', 'at yell', 'at well', 'what yell', 'what well'
  ]
  phrases = [x for x in ms.phrases(dictfile, 175)]
  assert set(phrases) == set([
    'toggle',
    'dog yell', 'dog well', 'tag yell', 'tag well',
    'at gill', 'at gal', 'what gill', 'what gal',
    'at ick yell', 'at ick well', 'what ick yell',
    'what ick well',
  ])
