#!/usr/bin/env python3

import sys
import re
import itertools
import collections

__doc__ = """
Usage: {} [options] <number>...

<number>...                Numbers to turn into words
                           If -, take <number>... from STDIN.

Options:
  -d, --dict=<filename>    Dictionary file to use
                           [DEFAULT: /usr/share/dict/words]
  -m, --max-words=<number> Maximum number of words to split into
                           [DEFAULT: 3]
""".format(sys.argv[0])

from docopt import docopt


def numeric_partitions(number, max_partitions):
  for partition in partitions(str(number), max_partitions):
    yield [int(x) for x in partition]


def regex_component(i):
  if i == 0:
    return r'[sSzZ]+'
  if i == 1:
    return r'[tTdD]+'
  if i == 2:
    return r'[nN]+'
  if i == 3:
    return r'[mM]+'
  if i == 4:
    return r'[rR]+'
  if i == 5:
    return r'[lL]+'
  if i == 6:
    return r'(j|J|sh|SH|ch|CH)'
  if i == 7:
    return r'[kKgGcC]+'
  if i == 8:
    return r'[fFvV]+'
  if i == 9:
    return r'[PpBb]+'
  if i == None:
    return r'[AaEeIiOoUuWwHhYy]*'
  raise ValueError("Expected a single digit or None")


def major_words(dictfile, number):
  # If it's something that can only be iterated through once (like a file
  # pointer), reset to the beginning again
  if isinstance(dictfile, collections.Iterator):
    dictfile.seek(0)
  regex = r'^' + regex_component(None)
  for character in str(number):
    regex += regex_component(int(character)) + regex_component(None)
  regex += r'$'
  for line in dictfile:
    if re.match(regex, line):
      yield line.strip()


def phrases_from_partition(dictfile, partition):
  word_collection = []
  for part in partition:
    words = major_words(dictfile, part)
    word_collection.append(words)
  for tup in itertools.product(*word_collection):
    yield " ".join(tup)


def phrases(dictfile, number, max_words):
  for numeric_partition in numeric_partitions(number, max_words):
    print(numeric_partition)
    for phrase in phrases_from_partition(dictfile, numeric_partition):
      yield phrase


def ordered_tuples(tuple_length, num_elts):
  if tuple_length == 1:
    for i in range(1, num_elts):
      yield (i,)
  else:
    for tup in ordered_tuples(tuple_length - 1, num_elts):
      for i in range(tup[-1] + 1, num_elts):
        yield tup + (i,)


def partitions(arr, max_partitions=None):
  num_elts = len(arr)
  # length 1
  to_return = [[arr]]
  # higher lengths
  for partition_length in range(2, num_elts + 1):
    tuple_length = partition_length - 1
    for tup in ordered_tuples(tuple_length, num_elts):
      partition = []
      partition.append(arr[0:tup[0]])
      for i in range(0, tuple_length - 1):
        partition.append(arr[tup[i]:tup[i + 1]])
      partition.append(arr[tup[-1]:num_elts])
      to_return.append(partition)
  return to_return


def main():
  args = docopt(__doc__)
  with open(args['--dict'], 'r') as dictfile:
    for number in args['<number>']:
      print("{}:".format(number))
      for phrase in phrases(dictfile, int(number), args['--max-words']):
        print("  " + phrase.strip())


if __name__ == "__main__":
  main()
