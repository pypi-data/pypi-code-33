"""Image dataset"""

import os
from logging import getLogger

from torch.utils.data import Dataset as TorchDataset, ConcatDataset
from torchvision.datasets.folder import default_loader

from tatau.fs.dirs import list_files

logger = getLogger(__name__)


class ImageChunkDataset(TorchDataset):
    """
    Image Dataset class for one chunk of image dataset
    """

    def __init__(self, chunk, class_to_idx, loader=None, transform=None, target_transform=None):
        self._transform = transform
        self._target_transform = target_transform
        self._samples = self._make_samples(list_files(chunk), class_to_idx)
        self._class_to_idx = class_to_idx
        self._loader = loader if loader is not None else default_loader

    def __getitem__(self, index: int) -> tuple:
        """
        Get item by index

        :param index: item index
        :return: tuple x, y
        """

        path, y = self._samples[index]
        x = self._loader(path)

        if self._transform is not None:
            x = self._transform(x)

        if self._target_transform is not None:
            y = self._target_transform(y)

        return x, y

    def __len__(self):
        return len(self._samples)

    @staticmethod
    def _make_samples(image_list, class_to_idx):
        samples = []

        for image_name in image_list:
            dir_name = os.path.split(os.path.split(image_name)[0])[1]
            assert dir_name in class_to_idx
            samples.append((image_name, class_to_idx[dir_name]))

        return samples


class ImageChunkedDataset(ConcatDataset):
    """
    Image Dataset class for chunked image dataset
    """

    def __init__(self, chunks, class_to_idx, loader=None, transform=None, target_transform=None):
        super(ImageChunkedDataset, self).__init__(
            datasets=[
                ImageChunkDataset(
                    chunk=chunk,
                    class_to_idx=class_to_idx,
                    loader=loader,
                    transform=transform,
                    target_transform=target_transform
                )
                for chunk in chunks
            ]
        )
