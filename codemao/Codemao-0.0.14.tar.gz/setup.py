
import hashlib
import http
import os
import urllib.request

from setuptools import setup, find_packages


# Add WITH_DATASHEET=1 environment to embed data sheet.
include_datasheet = (os.environ.get("WITH_DATASHEET", "0") == "1")

def get_keras_datasheets():
    def md5_file(fname):
        hash_md5 = hashlib.md5()
        with open(fname, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    url = "https://github.com/fchollet/deep-learning-models/releases/download/v0.2/resnet50_weights_tf_dim_ordering_tf_kernels_notop.h5"
    filename = "resnet50_weights_tf_dim_ordering_tf_kernels_notop.h5"
    filepath = os.path.join(os.path.split(__file__)[0], "codemao", "data", filename)
    md5sum_str = "a268eb855778b3df3c7506639542a6af"
    if os.path.exists(filepath) and md5_file(filepath) == md5sum_str:
        return
    response: http.client.HTTPResponse = urllib.request.urlopen(url)
    buffer_size = 2 ** 16
    hash_md5 = hashlib.md5()
    with open(filepath, "wb") as fh:
        while True:
            buffer = response.read(buffer_size)
            if not buffer:
                break
            fh.write(buffer)
            print("buffer:", len(buffer))
            hash_md5.update(buffer)
    if hash_md5.hexdigest() != md5sum_str:
        raise RuntimeError(F"{url}, Md5sum mismatch, expected {md5sum_str}")


if include_datasheet:
    get_keras_datasheets()

setup(
    name="Codemao",
    version="0.0.14",
    packages=find_packages(),
    install_requires=[
        'easygui',
        'opencv-python',
        'matplotlib',
        'dlib',
        'mxnet',
        'keras-mxnet',
        'scikit-image',
        'pillow',
    ],
    package_data = {
        "codemao": ["data/*.hdf5", "data/*.h5","data/age/*.*","data/mtcnn-model/*.*"],
    },
    description="Codemao是由深圳点猫科技有限公司创建的一个面向Python初学者的、帮助初学者学习Python的库。 欢迎大家提出各种建议意见，共同讨论学习！",
    author="haiguibianjiqi",
    author_email="wood@codemao.cn",
    url="https://python.codemao.cn/"
)
