from auto_corrector.nlp_parser import NLP_COUNTS
from auto_corrector.word import Word, common, exact, known, get_case
from auto_corrector.utils import local_dict, Global_dict, alphanumeric, symbols
import re

def spell(word):
    """most likely correction for everything up to a double typo"""
    w = Word(word)
    candidates = (common([word]) or exact([word]) or known([word]) or
                  known(w.typos()) or common(w.double_typos()) or
                  [word])
    correction = max(candidates, key=NLP_COUNTS.get)
    return get_case(word, correction)


def correct(sent):
    word_list = list(filter(None, sent.split(" ")))
    new_sent_list = []
    for wor in word_list:
        wor = wor.strip()
        org_word = wor

        if wor.isupper() or wor.lower() in Global_dict or wor.lower() in local_dict or \
                re.search(alphanumeric, wor) or wor.isnumeric() or org_word.__contains__(".com"):
            new_sent_list.append(org_word)

        else:
            if re.findall(symbols, wor):
                for s in re.findall(symbols, wor):
                    wor = wor.replace(s, " ").strip()

            if wor.isupper() or wor.lower() in Global_dict or wor.lower() in local_dict or \
                    re.search(alphanumeric, wor) or wor.isnumeric() or org_word.__contains__(".com"):
                new_sent_list.append(org_word)
            else:
                cor_wor = spell(wor)
                if re.findall(symbols, org_word):
                    for s in re.findall(symbols, org_word):
                        if org_word.endswith(s):
                            cor_wor = cor_wor + s
                            break
                        elif org_word.startswith(s):
                            cor_wor = s + cor_wor
                            break
                        else:
                            cor_wor = cor_wor

                new_sent_list.append(cor_wor)

    corrected_sent = " ".join(new_sent_list).strip()
    return corrected_sent