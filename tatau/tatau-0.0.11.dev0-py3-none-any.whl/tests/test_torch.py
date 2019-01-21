"""
Torch Unit Test

"""

import os
import pytest
import torch


class TestTorch:

    def test_mnist(self, tmpdir):
        from examples.torch.mnist import train, prepare_dataset
        ds_dir = os.path.join(tmpdir.__str__(), "dataset")
        batch_size = 32
        prepare_dataset.prepare_mnist(target_dir=ds_dir, chunk_size=batch_size, allow_exists_dir=False)

        target_weight_path = os.path.join(tmpdir.__str__(), 'weights.pkl')
        val_loss, val_acc = train.train_local(
            train_dir=os.path.join(ds_dir, 'train'),
            test_dir=os.path.join(ds_dir, 'test'),
            model_path='examples/torch/mnist/model.py',
            batch_size=batch_size,
            iterations=1,
            epochs=2,
            target_weight_path=target_weight_path
        )

        assert val_acc > 0.9
        assert os.path.isfile(target_weight_path)

    @pytest.mark.skipif(not torch.cuda.is_available(), reason="Requires CUDA device")
    def test_mnist_fp16(self, tmpdir):
        from examples.torch.mnist import train, prepare_dataset
        ds_dir = os.path.join(tmpdir.__str__(), "dataset")
        batch_size = 32
        prepare_dataset.prepare_mnist(target_dir=ds_dir, chunk_size=batch_size, allow_exists_dir=False)

        target_weight_path = os.path.join(tmpdir.__str__(), 'weights.pkl')
        val_loss, val_acc = train.train_local(
            train_dir=os.path.join(ds_dir, 'train'),
            test_dir=os.path.join(ds_dir, 'test'),
            model_path='examples/torch/mnist/model_fp16.py',
            batch_size=batch_size,
            iterations=1,
            epochs=2,
            target_weight_path=target_weight_path
        )

        assert val_acc > 0.9
        assert os.path.isfile(target_weight_path)
