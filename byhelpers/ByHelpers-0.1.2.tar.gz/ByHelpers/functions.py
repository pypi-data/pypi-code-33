#-*- coding: utf-8-*-
import unicodedata
import string



def key_format(data):
    '''
    Normaliza textos a formatos sin acentos o con formato
    para keys a base de datos
    '''
    if not isinstance(data, str):
        return None
    return ''.join(x for x in unicodedata.normalize('NFKD', data) if x in string.ascii_letters or x == " ").lower().replace(" ","_").replace("_y_","_").replace("_e_","_")


def clean_list(list_, remove_duplicates=True):
    if list_:
        output = [elem.strip() for elem in list_ if elem.strip()]
        if remove_duplicates is True:
            return list(set(output))
        else:
            return output
    else:
        return []


