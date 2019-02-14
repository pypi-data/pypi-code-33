import os
from datasmash.utils import genesess, xgenesess
from datasmash.d3m_dataset_loader import D3MDatasetLoader
from datasmash.quantizer import Quantizer


def d3m_to_zed(d3m_data_dir, quantize=True, featurizer=None):
    """

    """
    train_data = os.path.join(d3m_data_dir, 'TRAIN',
                              'dataset_TRAIN', 'datasetDoc.json')
    test_data = os.path.join(d3m_data_dir, 'TEST', 'dataset_TEST',
                             'datasetDoc.json')
    d3m_reader = D3MDatasetLoader()
    d3m_reader.load_dataset(data=train_data, train_or_test='train')
    tmp_dir, channel_dirs, channel_problems, y =(
        d3m_reader.write_libs(problem_type='supervised'))
    for channel in channel_dirs:
        if featurizer == 'xg2':
            kwargs = {'featurization': genesess,
                      'featurization_params': {'multi_line': True, 'depth':
                                               1000}}
        elif featurizer == 'xg1':
            kwargs = {'featurization': xgenesess,
                      'featurization_params': {'max_delay': 20}}
        else:
            kwargs = {}
        qtz = Quantizer(problem_type='supervised', multi_partition=True,
                        **kwargs)
        X = qtz.fit_transform(channel)

    d3m_reader.load_dataset(data=test_data, train_or_test='test')
    channel_problems = d3m_reader.write_test()

    for channel, problem in channel_problems.items():
        test_file = problem['test']
        X = qtz.transform(test_file)

    return tmp_dir
