import glob
import os
from FolderAnalyse import fileparser as fp


def top_frequencies(freq_dict, nterms=10):
    """
    top_frequencies(freq_dict, name, nterms)

    Returns the first nterms in the dictionary.

    Note:
    This wrapper is needed just to handle
    files with less than 10 words.
    """
    items = list(freq_dict.items())
    if len(items) < nterms:
        return dict(items)
    else:
        return dict(items[:nterms])


def _dict_to_text(freq_dict):
    """
    _dict_to_text(freq_dict):

    Internal routine to print items and values
    in a sorted dictionary, to avoid duplicating
    this code in process_file and in process_dir.
    """
    stats_text = ""
    for i, (key, value) in enumerate(freq_dict.items()):
        stats_text += f"{i+1}. {key}, {value}\n"
    stats_text += '\n'
    return stats_text


def underline(title):
    """
    Returns title but with another line matching the
    length as in restructured text format.

    >>> print(FolderAnalyse.process.underline('Hello'))
    Hello
    -----
    """
    return title + '\n' + '-'*(len(title)) + '\n'


def process_file(filename, N=10, case_sensitive=False):
    """
    process_file(filename, N=10, case_sensitive=False)

    Process a file and return some text giving the top
    N words in the file and the original frequency dictionary.
    
    Inputs:
        file

    Example:
    >>> f = open('test.txt', 'w')
    >>> f.write("The quick brown fox jumped over the lazy dog.")
    >>> f.close()
    >>> text, freq_dict = FolderAnalyse.process.process_file("test.txt")
    >>> print(freq_dict['the'])
    2
    """
    stats_text = underline(f"File \"{filename}\" Top {N} Word Frequencies")

    frequency_dict = fp.parse(filename, case_sensitive=case_sensitive,
                              sort=True)

    freqs = top_frequencies(frequency_dict, nterms=N)
    stats_text += _dict_to_text(freqs)

    return stats_text, frequency_dict, top_freq


def process_dir(dirname, extension="txt", N=10, case_sensitive=False):
    """
    process_dir(dirname, extension, N=10, case_sensitive=False)

    Processes all files in the given directory, and calls 
    process_file on each of them. It then returns a report along with
    the data used to construct this.
    
    Inputs:
        
    dirname, str:
        Directory to be processed
    extension, str:
        File extension to process in the directory.
    N, int:
        How many top frequencies should be calculated.
    case_sensitive, bool:
        Whether processing should be case sensitive or not, i.e.
        if 'the' is the same as 'The' for counting word frequencies.
    
    Outputs:
        str:
            Text report detailing the word frequencies for displaying.
        list of dicts:
            The full word frequency dicts for each file.
        list of dicts:
            The reduced top frequency dicts with N entries.
        dict:
            The combined frequency dict across all files.
        dict:
            The top N word frequencies across all files.

    Example:

    >>> f1 = open('test1.txt', 'w')
    >>> f1.write("The quick brown fox jumped over the lazy dog.")
    >>> f1.close()
    >>> f2 = open('test2.txt', 'w')
    >>> f2.write("This is a second file, the most common word will "
                 "still be the word the")
    >>> f2.close()

    >>> text, freq_dicts, combined = FolderAnalyse.process.process_dir(".")
    >>> print(combined['the'])
    5
    """
    files = glob.glob(os.path.join(dirname, f'*.{extension}'))
    if not len(files):
        raise FileNotFoundError("No Files!")

    stats_text = underline(f"Directory \"{dirname}\" Top {N} Word Frequencies")

    dicts = []
    top_dicts = []
    for file in files:
        stat, dic, top_dict = process_file(file, N, case_sensitive)
        stats_text += stat
        dicts.append(dic)
        top_dicts.append(top_dict)

    combined_dict = fp.sort_dict(fp.combine_dicts(dicts))
    top_combined = top_frequencies(combined_dict, N)
    stats_text += underline(f"All Files in {dirname} Top {N} Word Frequencies")
    stats_text += _dict_to_text(top_combined)

    return stats_text, dicts, top_dicts, combined_dict, top_combined
