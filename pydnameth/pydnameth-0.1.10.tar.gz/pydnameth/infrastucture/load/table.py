from pydnameth.infrastucture.path import get_save_path
import pandas as pd
import os.path


def load_table_dict(config):
    fn = get_save_path(config) + '/' + config.setup.get_file_name() + '.xlsx'
    if os.path.isfile(fn):
        df = pd.read_excel(fn)
        tmp_dict = df.to_dict()
        table_dict = {}
        for key in tmp_dict:
            curr_dict = tmp_dict[key]
            table_dict[key] = list(curr_dict.values())
        return table_dict
    else:
        raise IOError('No such file')
