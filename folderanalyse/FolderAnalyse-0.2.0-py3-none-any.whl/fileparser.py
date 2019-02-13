"""
Ryan Pepper (2018)

fileparser.py

This file contains a parser function that processes a text file.

"""
import re


def _read(filename, encodings=['ascii', 'utf-8', 'utf-16', 'latin-1']):
    """
    _read(filename)

    Try to read files and return the text regardless of their encoding.
    Raises UnicodeError on failure.

    Input:
        filename, str
            File to be read

    Output:
        str:
            Contents of the file
    """
    text = None

    for encoding in encodings:
        try:
            f = open(filename, encoding=encoding)
            text = f.read()
            f.close()
        except UnicodeDecodeError:
            f.close()
        except UnicodeError:
            f.close()
        except FileNotFoundError:
            raise FileNotFoundError("Could not open file.")

    if not text:
        raise UnicodeError(filename)

    return text


def parse(filename, case_sensitive=False, sort=False):
    """
    parse(filename, case_sensitive=False, sort=False)

    Opens a file, and reads it line by line, returning a dictionary
    containing key-value pairs of words and their frequency in the file.
    Note: newline characters are *always* removed from the file.

    Inputs:
        filename, str:
            The file to be calculate word frequencies.
        case_sensitive, bool:
            Whether processing should be case sensitive or not, i.e.
            if 'the' is the same as 'The' for counting word frequencies.
        sort, bool:
            Setting True enables sorting dict by word frequency.
            
    Outputs:
        dict:
            Dictionary containing key-value pairs of words and their
            frequency in the file.


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

    text = _read(filename)

    # If case_sensitive is true we make the text all lower case.
    if not case_sensitive:
        text = text.lower()

    # Note: we here process a word as being anything with
    # A-Z, a-z, 0-9, or any unicode characters in the 
    # range 00c00-u02b08 which is a number of weird characters
    # not normally used in English. The range was found by manually
    # looking through the table located at
    #   https://unicode-table.com/en/#ipa-extensions
    # for some common vowels that occur in other languages.
    # The motivation for this was in processing moby-dick.txt
    # in the examples where â was being misinterpreted as 
    # a word boundary by the re module.
    words = re.findall(r'\w*[\'-\u00c00-u02b08]*\w', text)

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
        dictionary, dict:
            Dictionary with integer values.
        
    Outputs:
        dictionary, dict:
            Dictionary sorted by value.
            

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
            
    Outputs:
        dict:
            A combined dictionary with summed values.

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
