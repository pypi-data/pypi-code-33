from __future__ import print_function
from os.path import join, dirname, abspath
import xlrd
import requests
import json
from mech import mechanizer
# from counter import totalCount

def topgen(path_in, numof, list_of_files, input_type, category, pval_method, output_name):

    current = 0
    for i in range(0, numof):
        # print("TEST: "+ str(path_in) + str(list_of_files[i]))
        tempFileName = str(list_of_files[i])
        fname = join(dirname(dirname(abspath(__file__))), 'test_data', str(path_in) + str(list_of_files[i]))

        # Open the workbook
        print("FNAME: "+str(fname))
        xl_workbook = xlrd.open_workbook(fname)

        # List sheet names, and pull a sheet by name
        sheet_names = xl_workbook.sheet_names()
        print('Sheet Names', sheet_names)

        xl_sheet = xl_workbook.sheet_by_name(sheet_names[0])

        # Or grab the first sheet by index
        #  (sheets are zero-indexed)
        xl_sheet = xl_workbook.sheet_by_index(0)
        print ('Sheet name: %s' % xl_sheet.name)

        num_rows = xl_sheet.nrows  # Number of rows
        num_cols = xl_sheet.ncols   # Number of columns


        entrez_id = ""
        tempName = ""
        print ("NUMBER OF Rows: " , num_rows)
        print ("NUMBER OF Cols: " ,num_cols)
        # In this case, 1 is where the patient names start
        for c in range(0, num_cols):
            current = current + 1
            # count = 0
            for r in range(0, num_rows):
                if(r == 0):
                    # Add name of patient to index zero of list
                    tempName = (str((xl_sheet.cell(r, c).value)))
                else:
                    entrez_id = entrez_id + (str(int(xl_sheet.cell(r, 0).value))) + ", "
            print("Name: ",tempName)
            # print("IDs" , entrez_id)
            # Call topgene parser
            mechanizer(tempName, entrez_id, current, input_type, category, pval_method, output_name, tempFileName)
            entrez_id = ""

    # totalCount(output_name, num_of_files, category)
