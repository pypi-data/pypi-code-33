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
    return title + '\n' + '-'*(len(title)-1) + '\n'


def process_file(file, N=10, case_sensitive=False):
    """
    process_file(file, N=10)

    Process a file and return some text giving the top
    N words in the file.
    """
    stats_text = underline(f"File \"{file}\" Top {N} Word Frequencies")

    frequency_dict = fp.parse(file, case_sensitive=case_sensitive,
                              sort=True)

    freqs = top_frequencies(frequency_dict, nterms=N)
    stats_text += _dict_to_text(freqs)

    return stats_text, frequency_dict


def process_dir(dirname, extension, N, case):
    files = glob.glob(os.path.join(dirname, f'*.{extension}'))
    if not len(files):
        raise FileNotFoundError("No Files!")

    stats_text = underline(f"Directory \"{dirname}\" Top {N} Word Frequencies")

    dicts = []
    for file in files:
        stat, dic = process_file(file, N, case)
        stats_text += stat
        dicts.append(dic)

    combined_dict = fp.sort_dict(fp.combine_dicts(dicts))
    top_freqs = top_frequencies(combined_dict, N)
    stats_text += underline(f"All Files in {dirname} Top {N} Word Frequencies")
    stats_text += _dict_to_text(top_freqs)

    return stats_text, dicts, combined_dict
