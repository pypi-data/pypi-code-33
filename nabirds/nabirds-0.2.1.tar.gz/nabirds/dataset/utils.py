import numpy as np
from PIL.Image import Image as PIL_Image

DEFAULT_RATIO = np.sqrt(49 / 400)

def __expand_parts(p):
	return p[:, 0], p[:, 1:3], p[:, 3].astype(bool)

def dimensions(im):
	if isinstance(im, np.ndarray):
		assert im.ndim == 3, "Only RGB images are currently supported!"
		return im.shape
	elif isinstance(im, PIL_Image):
		w, h = im.size
		c = len(im.getbands())
		# assert c == 3, "Only RGB images are currently supported!"
		return h, w, c
	else:
		raise ValueError("Unknown image instance ({})!".format(type(im)))

def asarray(im, dtype=np.uint8):
	if isinstance(im, np.ndarray):
		return im.astype(dtype)
	elif isinstance(im, PIL_Image):
		return np.asarray(im, dtype=dtype)
	else:
		raise ValueError("Unknown image instance ({})!".format(type(im)))


def uniform_parts(im, ratio=DEFAULT_RATIO, round_op=np.floor):
	h, w, c = dimensions(im)

	part_w = round_op(w * ratio).astype(np.int32)
	part_h = round_op(h * ratio).astype(np.int32)

	n, m = w // part_w, h // part_h

	parts = np.ones((n*m, 4), dtype=int)
	parts[:, 0] = np.arange(n*m)

	for x in range(n):
		for y in range(m):
			i = y * n + x
			x0, y0 = x * part_w, y * part_h
			parts[i, 1:3] = [x0 + part_w // 2, y0 + part_h // 2]

	return parts

def visible_part_locs(p):
	idxs, locs, vis = __expand_parts(p)
	return idxs[vis], locs[vis].T


def crops(im, xy, ratio=DEFAULT_RATIO, padding_mode="edge"):
	h, w, c = dimensions(im)
	crop_h, crop_w = int(h * ratio), int(w * ratio)
	crops = np.zeros((xy.shape[1], crop_h, crop_w, c), dtype=np.uint8)

	pad_h, pad_w = crop_h // 2, crop_w // 2

	padded_im = np.pad(im, [(pad_h, pad_h), (pad_w, pad_w), [0,0]], mode=padding_mode)

	for i, (x, y) in enumerate(xy.T):
		x0, y0 = x - crop_w // 2 + pad_w, y - crop_h // 2 + pad_h
		crops[i] = padded_im[y0:y0+crop_h, x0:x0+crop_w]

	return crops

def visible_crops(im, p, *args, **kw):
	idxs, locs, vis = __expand_parts(p)
	parts = crops(asarray(im), locs[vis].T, *args, **kw)
	res = np.zeros((len(idxs),) + parts.shape[1:], dtype=parts.dtype)
	res[vis] = parts
	return res

def reveal_parts(im, xy, ratio=DEFAULT_RATIO):
	h, w, c = dimensions(im)
	crop_h, crop_w = int(h * ratio), int(w * ratio)
	im = asarray(im)
	res = np.zeros_like(im)
	for x, y in xy.T:
		x0, y0 = max(x - crop_w // 2, 0), max(y - crop_h // 2, 0)
		res[y0:y0+crop_h, x0:x0+crop_w] = im[y0:y0+crop_h, x0:x0+crop_w]

	return res

def select(crops, mask):
	selected = np.zeros_like(crops)
	selected[mask] = crops[mask]
	return selected

def selection_mask(idxs, n):
	return np.bincount(idxs, minlength=n).astype(bool)

def random_select(idxs, xy, part_crops, *args, **kw):
	rnd_idxs = random_idxs(np.arange(len(idxs)), *args, **kw)
	idxs = idxs[rnd_idxs]
	xy = xy[:, rnd_idxs]

	mask = selection_mask(idxs, len(part_crops))
	selected_crops = select(part_crops, mask)

	return idxs, xy, selected_crops

def random_idxs(idxs, rnd=None, n_parts=None):

	if rnd is None or isinstance(rnd, int):
		rnd = np.random.RandomState(rnd)
	else:
		assert isinstance(rnd, np.random.RandomState), \
			"'rnd' should be either a random seed or a RandomState instance!"

	n_parts = n_parts or rnd.randint(1, len(idxs))
	res = rnd.choice(idxs, n_parts, replace=False)
	res.sort()
	return res
