from os.path import join, isfile
import numpy as np
from collections import defaultdict, OrderedDict
import abc
import warnings

class _MetaInfo(object):
	def __init__(self, **kwargs):
		for name, value in kwargs.items():
			setattr(self, name, value)
		self.structure = []

class BaseAnnotations(abc.ABC):
	@property
	@abc.abstractmethod
	def meta(self):
		pass

	def _path(self, file):
		return join(self.root, file)

	def _open(self, file):
		return open(self._path(file))

	def read_content(self, file, attr):
		content = None
		fpath = self._path(file)
		if isfile(fpath):
			with self._open(file) as f:
				content = [line.strip() for line in f if line.strip()]
		else:
			warnings.warn("File \"{}\" was not found!".format(fpath))

		setattr(self, attr, content)

	def __init__(self, root):
		super(BaseAnnotations, self).__init__()
		self.root = root

		for fname, attr in self.meta.structure:
			self.read_content(fname, attr)

		self.labels = np.array([int(l) for l in self.labels], dtype=np.int32)

		self._load_uuids()
		self._load_parts()
		self._load_split()

	def _load_uuids(self):
		assert self._images is not None, "Images were not loaded!"
		uuid_fnames = [i.split() for i in self._images]
		self.uuids, self.images = map(np.array, zip(*uuid_fnames))
		self.uuid_to_idx = {uuid: i for i, uuid in enumerate(self.uuids)}

	def _load_parts(self):
		assert self._part_locs is not None, "Part locations were not loaded!"
		# this part is quite slow... TODO: some runtime improvements?
		uuid_to_parts = defaultdict(list)
		for content in [i.split() for i in self._part_locs]:
			uuid_to_parts[content[0]].append([float(i) for i in content[1:]])

		self.part_locs = np.stack([uuid_to_parts[uuid] for uuid in self.uuids]).astype(int)

		if hasattr(self, "_part_names") and self._part_names is not None:
			self._load_part_names()

	def _load_part_names(self):
		self.part_names = OrderedDict()
		self.part_name_list = []
		for line in self._part_names:
			part_idx, _, name = line.partition(" ")
			self.part_names[int(part_idx)] = name
			self.part_name_list.append(name)

	def _load_split(self):
		assert self._split is not None, "Train-test split was not loaded!"
		uuid_to_split = {uuid: int(split) for uuid, split in [i.split() for i in self._split]}
		self.train_split = np.array([uuid_to_split[uuid] for uuid in self.uuids], dtype=bool)
		self.test_split = np.logical_not(self.train_split)

	def image_path(self, image):
		return join(self.root, self.meta.images_folder, image)

	def image(self, uuid):
		fname = self.images[self.uuid_to_idx[uuid]]
		return self.image_path(fname)

	def label(self, uuid):
		return self.labels[self.uuid_to_idx[uuid]].copy()

	def parts(self, uuid):
		return self.part_locs[self.uuid_to_idx[uuid]].copy()


	def _uuids(self, split):
		return self.uuids[split]

	@property
	def train_uuids(self):
		return self._uuids(self.train_split)

	@property
	def test_uuids(self):
		return self._uuids(self.test_split)

class NAB_Annotations(BaseAnnotations):
	@property
	def meta(self):
		info = _MetaInfo(
			images_folder="images",
			images_file="images.txt",
			labels_file="labels.txt",
			hierarchy_file="hierarchy.txt",
			split_file="train_test_split.txt",
			parts_file=join("parts", "part_locs.txt"),
			part_names_file=join("parts", "parts.txt"),
		)

		info.structure = [
			[info.images_file, "_images"],
			[info.labels_file, "labels"],
			[info.hierarchy_file, "hierarchy"],
			[info.split_file, "_split"],
			[info.parts_file, "_part_locs"],
			[info.part_names_file, "_part_names"],
		]
		return info

class CUB_Annotations(BaseAnnotations):
	@property
	def meta(self):
		info = _MetaInfo(
			images_folder="images",
			images_file="images.txt",
			labels_file="labels.txt",
			split_file="tr_ID.txt",
			bounding_boxes="bounding_boxes.txt",
			bounding_box_dtype=np.dtype([(v, np.int32) for v in "xywh"]),
			parts_file=join("parts", "part_locs.txt"),
			part_names_file=join("parts", "parts.txt"),

		)

		info.structure = [
			[info.images_file, "_images"],
			[info.labels_file, "labels"],
			[info.split_file, "_split"],
			[info.parts_file, "_part_locs"],
			[info.part_names_file, "_part_names"],
			[info.bounding_boxes, "_bounding_boxes"],
		]
		return info

	def __init__(self, *args, **kwargs):
		super(CUB_Annotations, self).__init__(*args, **kwargs)
		# set labels from [1..200] to [0..199]
		self.labels -= 1

	def _load_split(self):
		assert self._split is not None, "Train-test split was not loaded!"
		uuid_to_split = {uuid: int(split) for uuid, split in zip(self.uuids, self._split)}
		self.train_split = np.array([uuid_to_split[uuid] for uuid in self.uuids], dtype=bool)
		self.test_split = np.logical_not(self.train_split)

	def _load_parts(self):
		super(CUB_Annotations, self)._load_parts()
		# set part idxs from 1-idxs to 0-idxs
		self.part_locs[..., 0] -= 1

		self._load_bounding_boxes()

	def _load_bounding_boxes(self):
		assert self._bounding_boxes is not None, "Bouding boxes were not loaded!"

		uuid_to_bbox = {}
		for content in [i.split() for i in self._bounding_boxes]:
			uuid, bbox = content[0], content[1:]
			uuid_to_bbox[uuid] = [float(i) for i in bbox]

		self.bounding_boxes = np.array(
			[tuple(uuid_to_bbox[uuid]) for uuid in self.uuids],
			dtype=self.meta.bounding_box_dtype)


	def bounding_box(self, uuid):
		return self.bounding_boxes[self.uuid_to_idx[uuid]].copy()
