"""
Ryan Pepper (2018)

fileparser.py

This file contains a parser function that processes a text file.

"""
import re
import logging



def parse(filename, case_sensitive=False, sort=False):
    """
    parse(filename, case_sensitive=False, sort=False)
    
    Opens a file, and reads it line by line, returning a dictionary
    containing key-value pairs of words and their frequency in the file.
    Note: newline characters are *always* removed from the file.

    Inputs:

    filename, str
        The file to be calculate word frequencies.

    Examples:

    >>> text = "The quick brown fox jumped over the lazy dog."
    >>> f = open('example.txt', 'w')
    >>> f.write(text)
    >>> f.close()
    >>> FolderAnalyse.fileparser.parse('example.txt', case_sensitive=False)
    {'the': 2, 'quick': 1, 'brown': 1, 'fox': 1, 'jumped': 1,
     'over: 1, 'the': 1, 'lazy': 1, 'dog.': 1}

    >>> FolderAnalyse.fileparser.parse('example.txt', case_sensitive=False)
    {'the': 2, 'quick': 1, 'brown': 1, 'fox': 1, 'jumped': 1,
     'over: 1, 'the': 1, 'lazy': 1, 'dog.': 1}
    """

    try:
        f = open(filename, 'r')
    except FileNotFoundError:
        raise FileNotFoundError("Could not open file - are you sure it exists?")
    except UnicodeDecodeError:
        try:
            f = open(filename, 'r', encoding='utf-8')
        except:
            pass
        try:
            f = open(filename, 'r', encoding='utf-16')
        except:
            raise UnicodeError(filename)

    # Here we make the assumption that the files are independently
    # small enough to fit in memory. This may not be the case, but can be
    # handled. I use regular expressions to match at word boundaries, but 
    # treat apostrophes and hyphens as part of a word - i.e.
    # the regular expression will match "Claire's dogs" as two words and not 
    # three.
    text = f.read()

    # If case_sensitive is true we make the text all lower case.
    if not case_sensitive:
        text = text.lower()

    words = re.findall(r'\w*[\'-]*\w', text)

    frequency_dict = {word: 0 for word in words}
    # Do it this way rather than using count, because it avoids
    # doing len(words) lookups over the whole text.
    for word in words:
        frequency_dict[word] += 1

    if sort:
        # Sort the dictionary by the values. Dictionarys are ordered in Python
        # 3.6 and above but that is not the case for old versions where you
        # must use collections.OrderedDict.
        frequency_dict = sort_dict(frequency_dict)


    return frequency_dict


def sort_dict(frequency_dict, reverse=True):
    """
    sort_dict(dictionary)

    Sorts a dictionary based on the numerical values stored in the dict.

    Inputs:

    dictionary, dict
        Dictionary with integer values.

    Examples:

    >>> a = {'a': 2, 'b': 1, 'c': 5}
    >>> FolderAnalyse.fileparser.sort_dict(a, reverse=True)
    {'c': 5, 'a': 2, 'b': 1}
    >>> FolderAnalyse.fileparser.sort_dict(a, reverse=False)
    {'b': 1, 'a': 2, 'c': 5}

    Notes:

    Dictionarys are ordered in Python 3.6 and above but that is not the
    case for old versions where you must use collections.OrderedDict.
    """
    sorted_dict_keys = sorted(frequency_dict, key=frequency_dict.get,
                              reverse=reverse)
    sorted_dict = {key: frequency_dict[key] for key in sorted_dict_keys}
    return sorted_dict


def combine_dicts(dicts_list):
    """
    combine_dicts(dicts_list)

    Combines dictionaries by summing the numerical values of any keys
    which are shared between them.

    Inputs:

    dicts_list, list
        A list containing dictionaries with integer values.

    Example:

    >>> a = {'a': 2, 'b': 1, 'c': 5}
    >>> b = {'b': 4, 'c': 12, 'e': 4}
    >>> FolderAnalyse.parser.combine_dicts([a, b])
    {'a': 2, 'b': 5, 'c': 17, 'e': 4}
    """

    # Combine all dictionarys keys into a single
    # list and find the unique set of them.
    all_keys = []
    for freq_dict in dicts_list:
        all_keys += list(freq_dict.keys())
    keys = set(all_keys)

    # Generate the new dictionary with all keys
    combined_dict = {key: 0 for key in keys}

    # Iterate over the list of keys so that
    # the memory access pattern to the combined_dict
    # avoids jumping around. If key is not found in
    # a given fdict, just pass over.
    for key in keys:
        for fdict in dicts_list:
            try:
                combined_dict[key] += fdict[key]
            except:
                pass

    return combined_dict
