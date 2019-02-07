import pandas as pd
import numpy as np
import json


def xls_to_csv(filename, year, filename_trans_tech="kbob_translation_tech.csv",
               filename_trans_ind="kbob_translation_indicator.csv"):
    """
    Transform the kbob data from the a xlsx file to a csv. It save the units in a separate json file.

    Because we create a csv file, the comma in the french kbob terminology (i.e., the last column of the xlsx
     file with technology names) will be transformed to a hyphen.

    Require python > 3.6 as json.load is not ordered preserving before!

    Usage::
    * Load the kbob data in an Excel file. It is usually in a .zip file at the address :
    https://www.kbob.admin.ch/kbob/fr/home/publikationen/nachhaltiges-bauen/oekobilanzdaten_baubereich.html
    * Check that the downloaded kbob in in kWh and not MJ as both are available
    * use xls_to_csv("my_kbob", 2018)

    :param filename: string - the xlsx file with the kbob
    :param year: can be a int, float, or string - will be added to the name of the created csv files
    :param filename_trans_tech: string - name of the csv file which translate kbob terminology in german,
           french and english
    :param filename_trans_ind: string- name of the csv file which translate kbob terminology in in german,
           french and english
    :return: none
    """

    # name of the files to load and create
    sheetname = "Energie Energie"
    name_base_csv = "kbob_data"
    filename_unit = "kbob_unit{}.json".format(year)
    name_ener_type = {'utile': 'useful', 'finale': 'final'}

    # load raw-excel
    df_kbob = pd.read_excel(filename, sheet_name=sheetname, skiprows=6, usecols=[4, 5, 6, 7, 8, 9, 10, 11])
    if "kWh" not in filename:
        raise Warning("The kbob loaded here should be in kWh. Please check units.")

    # rename columns
    col_unit = pd.read_json(filename_unit, typ='series')
    df_kbob.columns = col_unit.index

    # adapt data
    df_kbob["FRA"] = df_kbob["FRA"].str.replace(',', ' -')
    df_kbob["EP_Percent_Renew"] = 100 * (df_kbob["EP_Renew"] / df_kbob["EP_Global"])
    df_kbob.dropna(inplace=True)
    for kstr in name_ener_type.keys():
        df_kbob.loc[df_kbob['EnerType'].str.contains(kstr), 'EnerType'] = name_ener_type[kstr]

    # load and test validity of translation
    trans_data_tech = pd.read_csv(filename_trans_tech, header=0)
    if trans_data_tech["FRA"].tolist() != df_kbob["FRA"].tolist():
        raise Warning("Translation terms are not coherent between the kbob and the file {}".format(filename_trans_tech))
    trans_data_ind = pd.read_csv(filename_trans_ind, header=0)
    if df_kbob.columns.tolist() in trans_data_ind['ENG'].tolist():
        raise Warning("Translation terms are not coherent between the kbob and the file {}".format(filename_trans_ind))

    # add language
    df_kbob = pd.merge(df_kbob, trans_data_tech, on="FRA")


    # export
    df_kbob.to_csv(name_base_csv +year + ".csv")


def main():

    filename = "Liste Oekobilanzdaten im Baubereich 2009-1-2016-gerundet-kWh.xlsx"
    year = "2016"
    xls_to_csv(filename, year)


if __name__ == '__main__':
    main()
