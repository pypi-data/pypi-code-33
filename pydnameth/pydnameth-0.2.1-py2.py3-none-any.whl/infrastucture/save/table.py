from pydnameth.infrastucture.path import get_save_path
import pandas as pd
import csv


def save_table_dict(config, table_dict):
    fn = get_save_path(config) + '/' + \
         config.setup.get_file_name() + '.xlsx'
    df = pd.DataFrame(table_dict)
    writer = pd.ExcelWriter(fn, engine='xlsxwriter')
    df.to_excel(writer, index=False)
    writer.save()

    fn = get_save_path(config) + '/' + \
        config.setup.get_file_name() + '.csv'
    with open(fn, 'w') as csvfile:
        writer = csv.DictWriter(csvfile,
                                fieldnames=table_dict.keys(),
                                lineterminator='\n')
        writer.writeheader()
        for id in range(0, len(list(table_dict.values())[0])):
            tmp_dict = {}
            for key, values in table_dict.items():
                tmp_dict[key] = values[id]
            writer.writerow(tmp_dict)
