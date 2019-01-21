import os
from logging import getLogger

import numpy as np

logger = getLogger(__name__)


def save_chunks(loader, target_dir):
    """
    Split dataset to chunks.

    :param loader: instance of DataLoader
    :param target_dir: path of target dir for chunks
    :return:
    """
    os.mkdir(target_dir)

    chunk_name_format = 'chunk_{{:0{}d}}'.format(len(str(len(loader))) + 1)

    for chunk_id, (x, y) in enumerate(loader):
        chunk_dir_name = chunk_name_format.format(chunk_id)
        chunk_path = os.path.join(target_dir, chunk_dir_name)
        os.mkdir(chunk_path)

        np.save(os.path.join(chunk_path, 'x'), np.array(x))
        np.save(os.path.join(chunk_path, 'y'), np.array(y))


def split_ds(train_loader, test_loader, target_dir):
    """
    Split train and test dataset to chunks.

    :param train_loader: instance of DataLoader for train data
    :param test_loader: instance of DataLoader for test data
    :param target_dir: path of target dir to "test" and "train" chunks
    :return: tuple(path to train dir, path to test dir)
    """
    target_train_dir = os.path.join(target_dir, 'train')
    logger.info('Train chunks dir: {}'.format(target_train_dir))

    save_chunks(train_loader, target_train_dir)

    target_test_dir = os.path.join(target_dir, 'test')
    logger.info('Test chunks dir: {}'.format(target_test_dir))

    save_chunks(test_loader, target_test_dir)

    return target_train_dir, target_test_dir
