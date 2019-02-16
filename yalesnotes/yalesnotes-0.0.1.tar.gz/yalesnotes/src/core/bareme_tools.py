import re
from collections import defaultdict

import pandas as pd


PATH_FILE_COEFS = "../../res/bareme-2017-2018.csv"


def csv_to_dict(fname=PATH_FILE_COEFS):
    """TODO : il manque des matières les rajouter"""
    df = pd.read_csv(fname)
    # df : [code, Intitulé, ECTS, Responsables, d'ouvertu, Ecrit, CC, TP, ORAL, TOTAL]
    table = df[["Code", "ECTS", "Ecrit", "CC", "TP", "Oral"]]

    coef_dict = {t.Code: {"ECTS": t.ECTS, "Ecrit": t.Ecrit / 100, "CC": t.CC /
                          100, "TP": t.TP / 100, "Oral": t.Oral / 100} for t in table.itertuples()}
    return coef_dict


def mark_evaluator(mark):
    """ take a mark and return its type (Ecrit, CC, TP, Oral)"""
    # todo : use regex to get the type
    exam_rgx = "(.)*examen(.)*"
    partiel_rgx = "((.)*partiel(.)*|(.)*examen-reparti[- _]?1(.)*)"
    tp_rgx = "((.)*tp(.)*|(.)*tme(.)*|(.)*projet(.)*)"
    cc_rgx = "((.)*cc(.)*|(.)*devoir(.)*|(.)*td(.)*|(.)*interro(.)*|(.)*participation(.)*)"
    # get epreuve that are not tp or cc therefore exam
    last_exam_rgx = "(.)*epreuve(.)"
    finale_rgx = "(.)*finale(.)*"

    regex_list = [partiel_rgx, exam_rgx, cc_rgx,
                  tp_rgx, last_exam_rgx, finale_rgx]
    result_list = ["Partiel", "Ecrit", "CC", "TP", "Ecrit", "Finale"]
    mark_string = mark.lower()
    for (rgx, res) in zip(regex_list, result_list):
        if re.match(rgx, mark_string):
            return res
    return None


def str_to_mark(mark_string):
    L = mark_string.split("/")
    if len(L) != 2:
        print("the input mark_string have a bad format expected n1 / n2, input was {}".format(mark_string))
        raise ValueError("Bad mark format")
    return float(L[0]) / float(L[1])


def mean(it):
    return sum(it) / len(it)


def single_ue_mean(ue_marks):
    result_list = [(mark_evaluator(test), str_to_mark(mark))
                   for test, mark in ue_marks.items()]
    # group by key
    result_dict = defaultdict(list)
    for mark_type, mark in result_list:
        result_dict[mark_type].append(mark)

    #{exam : [1, 0]} -> {exam : 0.5}
    mean_dict = {k: mean(v) for k, v in result_dict.items()}

    if "Finale" in mean_dict.keys():
        return mean_dict["Finale"]

    if "CC" in mean_dict.keys() and "Partiel" in mean_dict.keys():
        mean_dict["CC"] = 0.6 * mean_dict["Partiel"] + 0.4 * mean_dict["CC"]
        del mean_dict["Partiel"]
        return mean_dict

    if "Partiel" in mean_dict.keys() and "CC" not in mean_dict.keys():
        mean_dict["CC"] = mean_dict["Partiel"]
        del mean_dict["Partiel"]
        return mean_dict

    return mean_dict


def calculate_mean(user_marks, coef_dict):
    result_dict = dict()
    for code, ue_dico in user_marks.items():
        try:
            coef = coef_dict[code]
        except KeyError:
            # default coef
            coef = {"Ecrit": 0.6, "CC": 0.4, "TP": 0, "Oral": 0}
        ue_mean = single_ue_mean(ue_dico)
        if type(ue_mean) is float:
            result_dict[code] = ue_mean
        else:
            mean = 0
            for exam_type, score in filter(lambda x: x[0] is not None, ue_mean.items()):
                mean += coef[exam_type] * score
            result_dict[code] = mean
    return result_dict


if __name__ == '__main__':
    pass
