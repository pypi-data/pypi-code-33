import os
from logging import getLogger

import numpy as np

logger = getLogger(__name__)


def save_chunks(x_arr: np.ndarray, y_arr: np.ndarray, chunk_size: int, target_dir: str):
    """
    Split x_arr, y_arr to chunks and save to target dir.

    :param x_arr: X data
    :param y_arr: Y data
    :param chunk_size: size of chunk
    :param target_dir: path of target dir for chunks
    :return:
    """
    os.mkdir(target_dir)

    chunks = len(x_arr) // chunk_size
    chunk_dir_name_format = '{{:0{}d}}'.format(len(str(chunks)) + 1)

    for chunk_idx in range(0, chunks):
        start_idx = chunk_idx * chunk_size
        end_idx = start_idx + chunk_size
        x_chunk = x_arr[start_idx: end_idx]
        y_chunk = y_arr[start_idx: end_idx]

        chunk_dir = os.path.join(target_dir, 'chunk_' + chunk_dir_name_format.format(chunk_idx))
        os.mkdir(chunk_dir)

        x_path = os.path.join(chunk_dir, 'x')
        np.save(x_path, x_chunk)

        y_path = os.path.join(chunk_dir, 'y')
        np.save(y_path, y_chunk)


def split_ds(x_train: np.ndarray, y_train: np.ndarray,
             x_test: np.ndarray, y_test: np.ndarray,
             chunk_size: int, target_dir: str):
    """
    Split train and test data to chunks.

    :param x_train: X train
    :param y_train: Y train
    :param x_test: X test
    :param y_test: Y test
    :param chunk_size: size of chunk
    :param target_dir: target dir for "train" and "test" dirs
    :return: tuple(path to train dir, path to test dir)
    """
    target_train_dir = os.path.join(target_dir, 'train')
    logger.info('Train chunks dir: {}'.format(target_train_dir))

    save_chunks(x_train, y_train, chunk_size, target_train_dir)

    target_test_dir = os.path.join(target_dir, 'test')
    logger.info('Test chunks dir: {}'.format(target_test_dir))

    save_chunks(x_test, y_test, chunk_size, target_test_dir)

    return target_train_dir, target_test_dir
