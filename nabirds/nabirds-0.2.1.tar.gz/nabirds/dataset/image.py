from imageio import imread
from PIL import Image
from os.path import isfile

import copy
import numpy as np

from . import utils

def should_have_parts(func):
	def inner(self, *args, **kwargs):
		assert self.has_parts, "parts are not present!"
		return func(self, *args, **kwargs)
	return inner

class ImageWrapper(object):
	@staticmethod
	def read_image(im_path, mode="RGB"):
		# im = imread(im_path, pilmode=mode)
		im = Image.open(im_path, mode="r")
		return im


	def __init__(self, im_path, label, parts=None, mode="RGB"):

		self.mode = mode
		self.im = im_path
		self._im_array = None

		self.label = label
		self.parts = parts

		self.parent = None
		self._feature = None

	def __del__(self):
		if isinstance(self._im, Image.Image):
			if self._im is not None and self._im.fp is not None:
				self._im.close()

	@property
	def im(self):
		return self._im

	@property
	def im_array(self):
		if self._im_array is None:
			if isinstance(self._im, Image.Image):
				_im = self._im.convert(self.mode)
				self._im_array = utils.asarray(_im)
			elif isinstance(self._im, np.ndarray):
				if self.mode == "RGB" and self._im.ndim == 2:
					self._im_array = np.stack((self._im,) * 3, axis=-1)
				elif self._im.ndim == 3:
					self._im_array = self._im
				else:
					raise ValueError()
			else:
				raise ValueError()
		return self._im_array

	@im.setter
	def im(self, value):
		if isinstance(value, str):
			assert isfile(value), "Image \"{}\" does not exist!".format(value)
			self._im = ImageWrapper.read_image(value, mode=self.mode)
		else:
			self._im = value

	def as_tuple(self):
		return self.im_array, self.parts, self.label

	def copy(self):
		new = copy.copy(self)
		new.parent = self
		deepcopies = [
			"_feature",
			"parts",
		]
		for attr_name in deepcopies:
			attr_copy = copy.deepcopy(getattr(self, attr_name))
			setattr(new, attr_name, attr_copy)

		return new
	@property
	def feature(self):
		return self._feature

	@feature.setter
	def feature(self, im_feature):
		self._feature = im_feature

	def crop(self, x, y, w, h):
		result = self.copy()
		# result.im = self.im[y:y+h, x:x+w]
		result.im = self.im.crop(x, y, x+w, y+h)
		if self.has_parts:
			result.parts[:, 1] -= x
			result.parts[:, 2] -= y
		return result

	@should_have_parts
	def hide_parts_outside_bb(self, x, y, w, h):
		idxs, (xs,ys) = self.visible_part_locs()
		f = np.logical_and
		mask = f(f(x <= xs, xs <= x+w), f(y <= ys, ys <= y+h))
		result = self.copy()
		result.parts[:, -1] = mask.astype(self.parts.dtype)

		return result

	def uniform_parts(self, ratio):
		result = self.copy()
		result.parts = utils.uniform_parts(self.im, ratio=ratio)
		return result

	@should_have_parts
	def select_parts(self, idxs):
		result = self.copy()

		result.parts[:, -1] = 0
		result.parts[idxs, -1] = 1

		return result

	@should_have_parts
	def select_random_parts(self, rnd, n_parts):

		idxs, xy = self.visible_part_locs()
		rnd_idxs = utils.random_idxs(idxs, rnd=rnd, n_parts=n_parts)
		return self.select_parts(rnd_idxs)

	@should_have_parts
	def visible_crops(self, ratio):
		return utils.visible_crops(self.im, self.parts, ratio=ratio)

	@should_have_parts
	def visible_part_locs(self):
		return utils.visible_part_locs(self.parts)

	@should_have_parts
	def reveal_visible(self, ratio):
		_, xy = self.visible_part_locs()
		result = self.copy()
		result.im = utils.reveal_parts(self.im, xy, ratio=ratio)
		return result

	@should_have_parts
	def part_crops(self, ratio):
		crops = self.visible_crops(ratio)
		idxs, _ = self.visible_part_locs()
		result = self.copy()
		result.im = crops[idxs]
		return result

	@property
	def has_parts(self):
		return self.parts is not None

