#!/usr/bin/python


""""------------------------------------------------PACKAGES---------------------------------------------------------"""
from __future__ import print_function
from scipy import stats
from pylab import *
import csv

"""---------------------------------------------------------------------------------------------------------------------
---------------------------------------------------FUNCTIONS---------------------------------------------------------"""


def combine_all(ori_rrna_range, ori_dnaa_range, ori_go_range, dnaa_max_pos,
                ORI_gc, ORI_ta, p_ori_gc, p_ori_ta, p_ori_go, ter_rrna_range,
                ter_dif_range, ter_go_range, dif_max_pos,
                TER_gc, TER_ta, p_ter_gc, p_ter_ta, p_ter_go, alpha, csv_file, sequence_length,
                av_diff_gc, av_diff_ta, linear=False, motifs=False, skews=False, allmeas=False, geneori=False):

    final_ORI = final_TER = -1
    final_p_ori = final_p_ter = -1.0
    use_ori = use_ter = True
    comment_ori = ""
    comment_ter = ""

    if p_ori_gc == p_ori_ta == 1.0:
        '''check if the intervals är ok'''
        if p_ori_go <= alpha:
            ''' use ori_go '''
            if len(ori_dnaa_range)  != 0:
                dist = list()
                for pos in ori_go_range:
                    dist.append(abs(pos-dnaa_max_pos))

                final_ORI = ori_go_range[dist.index(min(dist))]
                final_p_ori = p_ori_go
            else:
                final_ORI = round(mean([ori_go_range[0], ori_go_range[-1]]))
                final_p_ori = p_ori_go
        else:
            if len(ori_dnaa_range) != 0:
                '''use dnaa range'''
                if dnaa_max_pos in ori_dnaa_range:
                    final_ORI = dnaa_max_pos
                    final_p_ori = -1.0
                else:
                    final_ORI = round(mean([ori_dnaa_range[0], ori_dnaa_range[-1]]))
            else:
                if len(ori_rrna_range) != 0:
                    if ORI_gc in ori_rrna_range:
                        if ORI_ta in ori_rrna_range:
                            final_ORI = round(mean([ORI_gc, ORI_ta]))
                            stat, final_p_ori = stats.combine_pvalues([p_ori_gc, p_ori_ta], method='fisher',
                                                                      weights=None)
                        else:
                            final_ORI = ORI_gc
                            final_p_ori = p_ori_gc
                    elif ori_go_range in ori_rrna_range:
                        final_ORI = round(mean([ori_go_range[0], ori_go_range[-1]]))
                        final_p_ori = p_ori_go
                    else:
                        '''use rrna range'''
                        final_ORI = round(mean([ori_rrna_range[0], ori_rrna_range[-1]]))
                        final_p_ori = -1.0
                else:
                    '''cannot predict'''
                    final_ORI = -1
                    final_p_ori = -1.0
                    use_ori = False

    elif p_ori_gc != 1.0 == p_ori_ta:
        if ORI_gc in ori_go_range and p_ori_go <= alpha:
            if len(ori_dnaa_range) != 0:
                dist = list()
                for pos in ori_go_range:
                    dist.append(abs(pos-dnaa_max_pos))

                ORI_go = ori_go_range[dist.index(min(dist))]
                final_ORI = round(mean([ORI_go, ORI_gc]))
                stat, final_p_ori = stats.combine_pvalues([p_ori_gc, p_ori_go], method='fisher', weights=None)
            else:
                final_ORI = ORI_gc
                final_p_ori = p_ori_gc
        elif ORI_gc not in ori_go_range and p_ori_go <= alpha:
            if p_ori_gc <= alpha:
                if len(ori_dnaa_range) != 0:
                    dist = list()
                    for pos in ori_go_range:
                        dist.append(abs(pos - dnaa_max_pos))

                    ORI_go = ori_go_range[dist.index(min(dist))]
                    final_ORI = round(mean([ORI_go, ORI_gc]))
                    stat, final_p_ori = stats.combine_pvalues([p_ori_gc, p_ori_go], method='fisher', weights=None)
                else:
                    final_ORI = round(mean([ORI_gc, ori_go_range[0], ori_go_range[-1]]))
                    stat, final_p_ori = stats.combine_pvalues([p_ori_gc, p_ori_go], method='fisher', weights=None)
            else:
                if len(ori_dnaa_range) != 0:
                    dist = list()
                    for pos in ori_go_range:
                        dist.append(abs(pos - dnaa_max_pos))

                    ORI_go = ori_go_range[dist.index(min(dist))]
                    final_ORI = ORI_go
                    final_p_ori = p_ori_go
                else:
                    final_ORI = round(mean([ori_go_range[0], ori_go_range[-1]]))
                    final_p_ori = p_ori_go
        else:
            final_ORI = ORI_gc
            final_p_ori = p_ori_gc

    elif p_ori_gc == 1.0 != p_ori_ta:
        '''use ta'''
        if ORI_ta in ori_go_range and p_ori_go <= alpha:
            if len(ori_dnaa_range) != 0:
                dist = list()
                for pos in ori_go_range:
                    dist.append(abs(pos-dnaa_max_pos))

                ORI_go = ori_go_range[dist.index(min(dist))]
                final_ORI = round(mean([ORI_go, ORI_ta]))
                stat, final_p_ori = stats.combine_pvalues([p_ori_ta, p_ori_go], method='fisher', weights=None)
            else:
                final_ORI = ORI_ta
                final_p_ori = p_ori_ta
        elif ORI_ta not in ori_go_range and p_ori_go <= alpha:
            if p_ori_ta <= alpha:
                if len(ori_dnaa_range) != 0:
                    dist = list()
                    for pos in ori_go_range:
                        dist.append(abs(pos - dnaa_max_pos))

                    ORI_go = ori_go_range[dist.index(min(dist))]
                    final_ORI = round(mean([ORI_go, ORI_ta]))
                    stat, final_p_ori = stats.combine_pvalues([p_ori_ta, p_ori_go], method='fisher', weights=None)
                else:
                    final_ORI = round(mean([ORI_ta, ori_go_range[0], ori_go_range[-1]]))
                    stat, final_p_ori = stats.combine_pvalues([p_ori_ta, p_ori_go], method='fisher', weights=None)
            else:
                if len(ori_dnaa_range) != 0:
                    dist = list()
                    for pos in ori_go_range:
                        dist.append(abs(pos - dnaa_max_pos))

                    ORI_go = ori_go_range[dist.index(min(dist))]
                    final_ORI = ORI_go
                    final_p_ori = p_ori_go
                else:
                    final_ORI = round(mean([ori_go_range[0], ori_go_range[-1]]))
                    final_p_ori = p_ori_go
        else:
            final_ORI = ORI_ta
            final_p_ori = p_ori_ta
    else:
        '''cannot predict'''
        final_ORI = -1
        final_p_ori = -1.0
        use_ori = False

    '''TER'''
    if p_ter_gc == p_ter_ta == 1.0:
        '''Check if go pred significant '''
        if p_ter_go <= alpha:
            ''' Use'''
            if len(ter_dif_range) != 0:
                dist = list()
                for pos in ter_go_range:
                    dist.append(abs(pos-dif_max_pos))

                final_TER = ter_go_range[dist.index(min(dist))]
                final_p_ter = p_ter_go
            else:
                final_TER = round(mean([ter_go_range[0], ter_go_range[-1]]))
        else:
            '''cIf'''
            if len(ter_dif_range) != 0:
                if dif_max_pos in ter_dif_range:
                    final_TER = dif_max_pos
                    final_p_ter = -1.0
                else:
                    final_TER = round(mean([ter_dif_range[0], ter_dif_range[-1]]))
                    final_p_ter = -1.0
            else:
                if len(ter_rrna_range) != 0:
                    if TER_gc in ter_rrna_range:
                        if TER_ta in ter_rrna_range:
                            final_TER = round(mean([TER_gc, TER_ta]))
                            stat, final_p_ter = stats.combine_pvalues([p_ter_gc, p_ter_ta], method='fisher',
                                                                      weights=None)
                        else:
                            final_TER = TER_gc
                            final_p_ter = p_ter_gc
                    elif ter_go_range in ter_rrna_range:
                        final_TER = round(mean([TER_go[0], TER_go[1]]))
                        final_p_ter = p_ter_go
                    else:
                        '''use rrna range'''
                        final_TER = round(mean([ter_rrna_range[0], ter_rrna_range[-1]]))
                        final_p_ter = -1.0
                else:
                    '''cannot predict'''
                    final_TER = -1
                    final_p_ter = -1.0
                    use_ter = False

    elif p_ter_gc != 1.0 == p_ter_ta:
        if TER_gc in ter_go_range and p_ter_go <= alpha:
            if len(ter_dif_range) != 0:
                dist = list()
                for pos in ter_go_range:
                    dist.append(abs(pos-dif_max_pos))

                TER_go = ter_go_range[dist.index(min(dist))]
                final_TER = round(mean([TER_go, TER_gc]))
                stat, final_p_ter = stats.combine_pvalues([p_ter_gc, p_ter_go], method='fisher', weights=None)
            else:
                final_TER = TER_gc
                final_p_ter = p_ter_gc

        elif TER_gc not in ter_go_range and p_ter_go <= alpha:
            if p_ter_gc <= alpha:
                if len(ter_dif_range) != 0:
                    dist = list()
                    for pos in ter_go_range:
                        dist.append(abs(pos - dif_max_pos))

                    TER_go = ter_go_range[dist.index(min(dist))]
                    final_TER = round(mean([TER_go, TER_gc]))
                    stat, final_p_ter = stats.combine_pvalues([p_ter_gc, p_ter_go], method='fisher', weights=None)
                else:
                    final_TER = round(mean([TER_gc, ter_go_range[0], ter_go_range[-1]]))
                    stat, final_p_ter = stats.combine_pvalues([p_ter_gc, p_ter_go], method='fisher', weights=None)
            else:
                if len(ter_dif_range) != 0:
                    dist = list()
                    for pos in ter_go_range:
                        dist.append(abs(pos - dif_max_pos))

                    TER_go = ter_go_range[dist.index(min(dist))]
                    final_TER = TER_go
                    final_p_ter = p_ter_go
                else:
                    final_TER = round(mean([ter_go_range[0], ter_go_range[-1]]))
                    final_p_ter = p_ter_go
        else:
            final_TER = TER_gc
            final_p_ter = p_ter_gc

    elif p_ter_gc == 1.0 != p_ter_ta:
        '''use ta'''
        if TER_ta in ter_go_range and p_ter_go <= alpha:
            if len(ter_dif_range) != 0:
                dist = list()
                for pos in ter_go_range:
                    dist.append(abs(pos-dif_max_pos))

                TER_go = ter_go_range[dist.index(min(dist))]
                final_TER = round(mean([TER_go, TER_ta]))
                stat, final_p_ter = stats.combine_pvalues([p_ter_ta, p_ter_go], method='fisher', weights=None)
            else:
                final_TER = TER_ta
                final_p_ter = p_ter_ta
        elif TER_ta not in ter_go_range and p_ter_go <= alpha:
            if p_ter_ta <= alpha:
                if len(ter_dif_range) != 0:
                    dist = list()
                    for pos in ter_go_range:
                        dist.append(abs(pos - dif_max_pos))

                    TER_go = ter_go_range[dist.index(min(dist))]
                    final_TER = round(mean([TER_go, TER_ta]))
                    stat, final_p_ter = stats.combine_pvalues([p_ter_ta, p_ter_go], method='fisher', weights=None)
                else:
                    final_TER = round(mean([TER_ta, ter_go_range[0], ter_go_range[-1]]))
                    stat, final_p_ter = stats.combine_pvalues([p_ter_ta, p_ter_go], method='fisher', weights=None)
            else:
                if len(ter_dif_range) != 0:
                    dist = list()
                    for pos in ter_go_range:
                        dist.append(abs(pos - dif_max_pos))

                    TER_go = ter_go_range[dist.index(min(dist))]
                    final_TER = TER_go
                    final_p_ter = p_ter_go
                else:
                    final_TER = round(mean([ter_go_range[0], ter_go_range[-1]]))
                    final_p_ter = p_ter_go
        else:
            final_TER = TER_ta
            final_p_ter = p_ter_ta
    else:
        '''cannot predict'''
        final_TER = -1
        final_p_ter = -1.0
        use_ter = False

    if not use_ori:
        comment_ori = "ORI prediction not possible. "
    if not use_ter:
        comment_ter = "TER prediction not possible."

    comment = ""
    if not use_ori and not use_ter:
        comment = "Predictions not possible."
    else:
        comment = comment_ori + comment_ter

    if use_ori:
        if final_p_ori > alpha:
            comment_ori = "NB! ORI p-value above significance level, \n" \
                          "do not trust result. "
    if use_ter:
        if final_p_ter > alpha:
            comment_ter = "NB! TER p-value above significance level, \n" \
                          "do not trust result. "

    if use_ori and use_ter and final_p_ori > alpha < final_p_ter:
        comment = "NB! Both p-values indicate insignificant result, \n" \
                  "do not trust result!"
    else:
        comment = comment_ori + comment_ter

    if final_p_ori <= alpha or final_p_ter <= alpha:
        if (av_diff_gc <= av_diff_ta and av_diff_gc > 0.05) or \
                (av_diff_ta < av_diff_gc and av_diff_ta > 0.05):
            comment = comment + "Large variation -- do not trust p-values."

    '''No p-values if only running motifs'''
    if motifs == True and not skews and not allmeas and not geneori:
        final_p_ori = final_p_ter = -1.0

    predict(int(final_ORI), int(final_TER), round(final_p_ori, 3), round(final_p_ter, 3), comment,
            csv_file, sequence_length, use_ori, use_ter, "", linear)


def predict(ORI, TER, p_ori, p_ter, comment, csv_file, sequence_length,
            use_ori=True, use_ter=True, pred="", linear=False):
    """
    Adds final prediction to csv file

    :param ORI:             Final prediction of ORI
    :param TER:             Final prediction of TER
    :param p_ori:           Final p-value for ORI prediction
    :param p_ter:           Final p-value for TER prediction
    :param comment:         Comment if needed
    :param csv_file:        Name of csv file
    :param sequence_length: Length of sequence studied
    :param use_ori:         Is the ORI prediction ok or not
    :param use_ter:         Is the TER prediction ok or not
    :param pred:            Both predictions, only ORI or only TER
    :param linear:          If the sequence is from a linear chromosome
    :return:                Saves to file
    """
    if linear:
        if TER != sequence_length - 1:
            TER_1 = TER
            TER_2 = TER + 1
        elif TER == sequence_length - 1:
            TER_1 = TER
            TER_2 = 0

        if use_ori and use_ter:
            if p_ori == p_ter == -1.0:
                with open(csv_file, mode='a') as results:
                    teritori_writer = csv.writer(results, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    teritori_writer.writerow(["", ORI, "", TER_1, TER_2, "", comment])
            elif p_ori == -1.0 and p_ter != -1.0:
                with open(csv_file, mode='a') as results:
                    teritori_writer = csv.writer(results, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    teritori_writer.writerow(["", ORI, "", TER_1, TER_2, p_ter, comment])
            elif p_ori != -1.0 and p_ter == -1.0:
                with open(csv_file, mode='a') as results:
                    teritori_writer = csv.writer(results, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    teritori_writer.writerow(["", ORI, p_ori, TER_1, TER_2, "", comment])
            else:
                with open(csv_file, mode='a') as results:
                    teritori_writer = csv.writer(results, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    teritori_writer.writerow(["", ORI, p_ori, TER_1, TER_2, p_ter, comment])
        elif use_ori and not use_ter:
            if p_ori == -1.0:
                if pred == "":
                    with open(csv_file, mode='a') as results:
                        teritori_writer = csv.writer(results, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                        teritori_writer.writerow(["", ORI, "", "---", "---", "---", comment])
                elif pred == "ori":
                    with open(csv_file, mode='a') as results:
                        teritori_writer = csv.writer(results, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                        teritori_writer.writerow(["", ORI, "", "", "", "", comment])
            else:
                if pred == "":
                    with open(csv_file, mode='a') as results:
                        teritori_writer = csv.writer(results, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                        teritori_writer.writerow(["", ORI, p_ori, "---", "---", "---", comment])
                elif pred == "ori":
                    with open(csv_file, mode='a') as results:
                        teritori_writer = csv.writer(results, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                        teritori_writer.writerow(["", ORI, p_ori, "", "", "", comment])
                else:
                    with open(csv_file, mode='a') as results:
                        teritori_writer = csv.writer(results, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                        teritori_writer.writerow(["", ORI, p_ori, "---", "---", "---", comment])
        elif not use_ori and use_ter:
            if p_ter == -1.0:
                if pred == "":
                    with open(csv_file, mode='a') as results:
                        teritori_writer = csv.writer(results, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                        teritori_writer.writerow(["", "---", "---", TER_1, TER_2, "", comment])
                elif pred == "ter":
                    with open(csv_file, mode='a') as results:
                        teritori_writer = csv.writer(results, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                        teritori_writer.writerow(["", "", "", TER_1, TER_2, "", comment])
            else:
                if pred == "":
                    with open(csv_file, mode='a') as results:
                        teritori_writer = csv.writer(results, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                        teritori_writer.writerow(["", "---", "---", TER_1, TER_2, p_ter, comment])
                elif pred == "ter":
                    with open(csv_file, mode='a') as results:
                        teritori_writer = csv.writer(results, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                        teritori_writer.writerow(["", "", "", TER_1, TER_2, p_ter, comment])
                else:
                    with open(csv_file, mode='a') as results:
                        teritori_writer = csv.writer(results, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                        teritori_writer.writerow(["", "---", "---", TER_1, TER_2, p_ter, comment])
        elif not use_ori and not use_ter:
            with open(csv_file, mode='a') as results:
                teritori_writer = csv.writer(results, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                teritori_writer.writerow(["", "---", "---", "---", "---", "---", "Predictions not possible"])
    elif not linear:
        if use_ori and use_ter:
            if p_ori == p_ter == -1.0:
                with open(csv_file, mode='a') as results:
                    teritori_writer = csv.writer(results, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    teritori_writer.writerow(["", ORI, "", TER, "", comment])
            elif p_ori == -1.0 and p_ter != -1.0:
                with open(csv_file, mode='a') as results:
                    teritori_writer = csv.writer(results, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    teritori_writer.writerow(["", ORI, "", TER, p_ter, comment])
            elif p_ori != -1.0 and p_ter == -1.0:
                with open(csv_file, mode='a') as results:
                    teritori_writer = csv.writer(results, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    teritori_writer.writerow(["", ORI, p_ori, TER, "", comment])
            else:
                with open(csv_file, mode='a') as results:
                    teritori_writer = csv.writer(results, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    teritori_writer.writerow(["", ORI, p_ori, TER, p_ter, comment])
        elif use_ori and not use_ter:
            if p_ori == -1.0:
                if pred == "":
                    with open(csv_file, mode='a') as results:
                        teritori_writer = csv.writer(results, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                        teritori_writer.writerow(["", ORI, "", "---", "---", comment])
                elif pred == "ori":
                    with open(csv_file, mode='a') as results:
                        teritori_writer = csv.writer(results, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                        teritori_writer.writerow(["", ORI, "", "", "", comment])
            else:
                if pred == "":
                    with open(csv_file, mode='a') as results:
                        teritori_writer = csv.writer(results, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                        teritori_writer.writerow(["", ORI, p_ori, "---", "---", comment])
                elif pred == "ori":
                    with open(csv_file, mode='a') as results:
                        teritori_writer = csv.writer(results, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                        teritori_writer.writerow(["", ORI, p_ori, "", "", comment])
                else:
                    with open(csv_file, mode='a') as results:
                        teritori_writer = csv.writer(results, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                        teritori_writer.writerow(["", ORI, p_ori, "---", "---", comment])
        elif not use_ori and use_ter:
            if p_ter == -1.0:
                if pred == "":
                    with open(csv_file, mode='a') as results:
                        teritori_writer = csv.writer(results, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                        teritori_writer.writerow(["", "---", "---", TER, "", comment])
                elif pred == "ter":
                    with open(csv_file, mode='a') as results:
                        teritori_writer = csv.writer(results, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                        teritori_writer.writerow(["", "", "", TER, "", comment])
            else:
                if pred == "":
                    with open(csv_file, mode='a') as results:
                        teritori_writer = csv.writer(results, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                        teritori_writer.writerow(["", "---", "---", TER, p_ter, comment])
                elif pred == "ter":
                    with open(csv_file, mode='a') as results:
                        teritori_writer = csv.writer(results, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                        teritori_writer.writerow(["", "", "", TER, p_ter, comment])
                else:
                    with open(csv_file, mode='a') as results:
                        teritori_writer = csv.writer(results, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                        teritori_writer.writerow(["", "---", "---", TER, p_ter, comment])
        elif not use_ori and not use_ter:
            with open(csv_file, mode='a') as results:
                teritori_writer = csv.writer(results, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                teritori_writer.writerow(["", "---", "---", "---", "---", "Predictions not possible"])