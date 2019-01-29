import numpy as np
from scipy.misc import imresize


def pad(images, K, shape=None):
    if shape is None:
        shape = images.shape[1:]
    pad_width = ((0, 0), (K, K), (K, K))
    if len(shape) == 3:
        pad_width += ((0, 0),)

    return np.pad(images, pad_width, mode='constant')


def iscolor(img):
    shape = img.shape
    return len(shape) == 3 and shape[-1] == 3


def resize_imagenet(img):
    # crop imgs to 224 x 224
    H, W = img.shape[:2]
    scale = 1.15
    r = max(224. / H, 224. / W)
    Hp = int(H * r * scale)
    Wp = int(W * r * scale)
    img2 = imresize(img, (Hp, Wp))

    Hcut = Hp - 224
    Wcut = Wp - 224

    Htop = Hcut // 2
    Wleft = Wcut // 2

    img2 = img2[Htop: Htop + 224, Wleft: Wleft + 224, ...]
    return img2


def normalized(img):
    result = img.copy()
    result -= result.min()
    result /= result.max()
    return result


def rescale_img(img, min_from=-1, max_from=1, min_to=0, max_to=255, dtype='float32'):
    len_from = max_from - min_from
    len_to = max_to - min_to
    return ((img.astype(np.float32) - min_from) * len_to / len_from + min_to).astype(dtype)

