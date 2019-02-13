import pandas as pd
import csv


def save_table_dict(fn, table_dict):
    fn_xls = fn + '.xlsx'
    df = pd.DataFrame(table_dict)
    writer = pd.ExcelWriter(fn_xls, engine='xlsxwriter')
    df.to_excel(writer, index=False)
    writer.save()

    fn_csv = fn + '.csv'
    with open(fn_csv, 'w') as csvfile:
        writer = csv.DictWriter(csvfile,
                                fieldnames=table_dict.keys(),
                                lineterminator='\n')
        writer.writeheader()
        for id in range(0, len(list(table_dict.values())[0])):
            tmp_dict = {}
            for key, values in table_dict.items():
                tmp_dict[key] = values[id]
            writer.writerow(tmp_dict)
