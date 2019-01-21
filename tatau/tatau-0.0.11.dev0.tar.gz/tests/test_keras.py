"""
Keras Unit Test

"""

import os


class TestKeras:

    def test_mnist(self, tmpdir):
        from examples.keras.mnist import train, prepare_dataset
        ds_dir = os.path.join(tmpdir.__str__(), 'dataset')
        prepare_dataset.prepare_mnist(target_dir=ds_dir, chunk_size=100, allow_exists_dir=False)

        target_weight_path = os.path.join(tmpdir.__str__(), 'weights.pkl')
        val_loss, val_acc = train.train_local(
            train_dir=os.path.join(ds_dir, 'train'),
            test_dir=os.path.join(ds_dir, 'test'),
            model_path='examples/keras/mnist/model.py',
            batch_size=32,
            iterations=1,
            epochs=2,
            target_weight_path=target_weight_path
        )

        assert val_acc > 0.9
        assert os.path.isfile(target_weight_path)
