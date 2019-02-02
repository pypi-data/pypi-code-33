from pydnameth.infrastucture.path import get_data_base_path
import numpy as np
import os.path
import pickle


def get_line_list(line):
    line_list = line.split('\t')
    for val_id in range(0, len(line_list)):
        line_list[val_id] = line_list[val_id].replace('"', '').rstrip()
    return line_list


def load_cpg(config):
    fn_dict = get_data_base_path(config) + '/' + 'cpg_dict.pkl'
    fn_data = get_data_base_path(config) + '/' + config.data.name
    fn_txt = fn_data + '.txt'
    fn_npz = fn_data + '.npz'

    if os.path.isfile(fn_dict) and os.path.isfile(fn_npz):

        f = open(fn_dict, 'rb')
        config.cpg_dict = pickle.load(f)
        f.close()

        data = np.load(fn_npz)
        config.cpg_data = data['cpg_data']

    else:

        config.cpg_dict = {}

        f = open(fn_txt)
        f.readline()
        cpg_id = 0
        for line in f:
            line_list = get_line_list(line)
            cpg = line_list[0]
            config.cpg_dict[cpg] = cpg_id
            cpg_id += 1
        f.close()

        f = open(fn_dict, 'wb')
        pickle.dump(config.cpg_dict, f, pickle.HIGHEST_PROTOCOL)
        f.close()

        num_cpgs = cpg_id

        f = open(fn_txt)
        header_line = f.readline()
        headers = header_line.split('\t')
        headers = [x.rstrip() for x in headers]
        subjects = headers[1:len(headers)]

        config.cpg_data = np.zeros((num_cpgs, len(subjects)), dtype=np.float32)

        cpg_id = 0
        for line in f:
            line_list = get_line_list(line)
            curr_data = list(map(np.float32, line_list[1::]))
            config.cpg_data[cpg_id] = curr_data
            cpg_id += 1
        f.close()

        np.savez_compressed(fn_npz, cpg_data=config.cpg_data)
