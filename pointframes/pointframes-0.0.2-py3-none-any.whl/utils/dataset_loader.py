import os
import numpy as np
import pandas as pd
import pointframes as pf
import dask
import dask.dataframe as dd

class DaskDataSet(object):

	""" Class for a out-of-memory dataset using Dask. The class assumes than the dataset
		has already been pre-processed using pf.compute_z_order_dask().

		The aim of this class is to be able to read both a single and list of pointclouds
		for feeding into a ML/DL algorithm. This should be a general as possible to allow
		for re-use regardless of the dataset type or application. All assumptions should
		be clearly displayed. Where possible the functions called here should be existing
		pointframes functions.

		Current datasets that should be catered for are:
			- Standard .csv (i.e. X, Y, Z, R, G, B, class)
			- Semantic3D
			- ScanNet
			- Robin Mobile Mapping System

		attributes:
		------------

			filelist           : list
								   list of filepaths
			num_classes        : int
								   number of classes in dataset
			num_workers        : int
								   number of threads for dask to use
			blocksize          : int
								   blocksize in bytes (i.e. byte per threads)
			box_size           : float
							       size of boxes for sampling (square/cubed)
			num_points         : int
								   number of points to return in batch
			features           : list
								   features to attach to batch points i.e. ['X', 'Y', 'Z']
			columns            : list
								   name of columns for data frames
			header             : None or int
								   pandas header argument, None for no header, 0 for first row
			df_dtype           : dict
			                       data type dictionary to tell dask column data types
			labels_weights_dir : str
								   directory of labels_weigths file if present
								   otherwise, directory where file is created
			z_scalar           : float
			                       scalar value used for z-order indexing
								   z-order sampling won't work if this value is incorrect

		functions:
		------------

	"""

	def __init__(self, train=True, filelist=None, num_workers=4, blocksize=25e7, load_scene=True,
					   num_points=1000, columns=None, header=None, dtype=None, labels_weights_dir=None,
					   load_labels_weights=True, z_scalar=1., box_size=10):

		self._train = train
		self._filelist = filelist
		self._num_workers = num_workers
		self._blocksize = blocksize
		self._box_size = box_size
		self._encoder = None
		self._num_points = num_points
		self._features = ['X', 'Y', 'Z']
		self._columns = columns
		self._labels_weights = None
		self._header = header
		self._df_dtype = dtype
		self._labels_weights_dir = labels_weights_dir
		self._z_scalar = z_scalar
		self._bpd = None

		self._scene_iterator = -1
		self._curr_scene = None
		self._curr_nparitions = None

		self._batch_iterator = -1
		self._curr_batch_list = None
		self._curr_batch = None

		self._full_scene_pass = False
		self._scene_complete = False

		if load_labels_weights == True:
			assert self._labels_weights_dir is not None, '[error] labels weights directory must be set.'
			assert os.path.isdir(self._labels_weights_dir), '[error] labels weights directory is not valid.'
			if os.path.isfile(os.path.join(self._labels_weights_dir, 'labels_weights.csv')):
				self._load_labels_weights_file(self._labels_weights_dir)
			else:
				print ('[info] generating labels and weights file...')
				self.generate_labels_weights_file(self._labels_weights_dir)
				self._load_labels_weights_file(self._labels_weights_dir)

		if load_scene == True:
			# Load in initial scene
			self._load_model(self._filelist[self._scene_iterator], header=self._header)


	def _load_model(self, filepath, sorted=True, sep=',', header=None, compute=False):
		""" Method to load a model from disk. Assumes models are .csv files with ',' seperator """

		# Incease scene iterator if more scenes available
		self._scene_iterator = self._scene_iterator + 1 if self._has_more_scenes() else 0

		# Get scene filename
		self._filename = self._filelist[self._scene_iterator].split('/')[-1].split('.')[0]
		print (self._filename)

		# Read dataset into dask computation graph
		df = dd.read_csv(filepath, blocksize=self._blocksize, sep=sep, header=header, dtype=self._df_dtype)
		n_partitions = df.npartitions

		if self._columns is not None:
			df.columns = self._columns

		# Set the index of the scene. This is much faster if already sorted.
		df = df.set_index(df.z_ord, sorted=True) if sorted == True else df.set_index(df.z_ord, sorted=False)
		# Only compute if dataset fits into memory
		df = df if compute == False else df.compute()

		# Store current scene graph and number of paritions in memory
		self._curr_scene = df
		self._curr_nparitions = n_partitions

		self._scene_extent()
		self._generate_batch_list()

		print (len(self._curr_batch_list))

		# Re-compute the z-order scales used for indexing
		self._x_scale = self._z_scalar / (self._curr_scene_extent[2] - self._curr_scene_extent[0])
		self._y_scale = self._z_scalar / (self._curr_scene_extent[3] - self._curr_scene_extent[1])

		return None

	def _unique_label_count(self, df):
		""" Method to get unique labels for pandas series """
		return np.unique(df.label.values, return_counts=True)

	def generate_labels_weights_file(self, save_dir):
		""" Method to generate a labels .txt file. Pre-computation of this speeds up
			runtime performance.
		"""

		global_labels = []
		global_counts = []

		for scene_file in self._filelist:
			self._load_model(scene_file)
			unique = self._curr_scene.map_partitions(lambda x : self._unique_label_count(x))
			unique = unique.compute().values
			labels = []
			counts = []
			[labels.append(label[0]) for label in unique]
			[counts.append(label[1]) for label in unique]
			u_labels = []
			u_counts = []
			for i, l in enumerate(labels):
				for j, v in enumerate(l):
					u_labels.append(v)
					u_counts.append(counts[i][j])
			global_labels.append(u_labels)
			global_counts.append(u_counts)

		u_labels = np.array([])
		u_counts = np.array([])

		# TODO: This doesn't append the final value for some reason?

		for i, l in enumerate(global_labels[0]):
			if l in u_labels:
				u_counts[np.where(l==u_labels)] += global_counts[0][i]
			else:
				u_labels = np.append(u_labels, l)
				u_counts = np.append(u_counts, global_counts[0][i])

		np.savetxt(os.path.join(save_dir, 'labels_weights.csv'),
				   np.hstack((u_labels.reshape(-1, 1).astype(int), u_counts.reshape(-1, 1))),
				   delimiter=',', fmt="%s")


	def _load_labels_weights_file(self, dir, min_shift=None):
		""" Method to read in label and weight file as pandas dataframe """

		path = os.path.join(dir, 'labels_weights.csv')
		df = pd.read_csv(path, delimiter=',', header=None)
		df.columns = ['label', 'count']
		if min_shift == None:
			df['weights'] = 1 - (df['count'] / df['count'].max())
		else:
			df['weights'] = (1 - (df['count'] / df['count'].max())) + min_shift
			df['weigths'].values[df['weights'].values > 1] = 1
		self._labels_weights = df


	def _scene_extent(self):
		""" Method to set the extent of the current scene """

		xmin, xmax, ymin, ymax, zmin, zmax = dask.compute(self._curr_scene.X.min(), self._curr_scene.X.max(),
		self._curr_scene.Y.min(), self._curr_scene.Y.max(),
		self._curr_scene.Z.min(), self._curr_scene.Z.max())

		self._curr_scene_extent = [xmin, xmax, ymin, ymax, zmin, zmax]


	def _generate_batch_list(self, dims=2, bpd=32):

		batch_list = []
		self._bpd = bpd

		if dims == 2:
			self._encoder = pf.ZEncoder(2, 2*bpd)
			num_xstrides = int(np.floor((self._curr_scene_extent[1]-self._curr_scene_extent[0]) / self._box_size))
			num_ystrides = int(np.floor((self._curr_scene_extent[3]-self._curr_scene_extent[2]) / self._box_size))
			for x_stride in range(0, num_xstrides):
				for y_stride in range(0, num_ystrides):
					batch_list.append([self._curr_scene_extent[0]+(x_stride*self._box_size),
									   self._curr_scene_extent[2]+(y_stride*self._box_size),
									   self._curr_scene_extent[0]+((x_stride*self._box_size)+self._box_size),
									   self._curr_scene_extent[2]+((y_stride*self._box_size)+self._box_size)])

		# Shuffle batch list to avoid training bias
		batch_list = np.array(batch_list)
		np.random.shuffle(batch_list)
		self._curr_batch_list = batch_list


	def _has_more_scenes(self):
		""" Method to check if more scenes are available """
		# Full scene pass is True when scenes left is False
		self._full_scene_pass = self._scene_iterator == len(self._filelist)-1
		if self._full_scene_pass == True:
			print('[info] scene complete.')
		return not self._scene_iterator == len(self._filelist)-1


	def _has_more_batches(self):
		""" Method to check if more batches are available in the scene """
		self._scene_complete = self._batch_iterator == len(self._curr_batch_list)-1
		return not self._batch_iterator == len(self._curr_batch_list)-1


	def _get_batch_weights(self, labels):
		""" Method to get weights for a batch of labels """
		return np.array([[self._labels_weights['weights'].values[np.where(x==self._labels_weights['label'].values)] for x in labels]])


	def get_next_batch(self, sample_method='uniform'):
		""" Method to get the next batch for model training """

		valid_batch = False

		# Repeat until we get a batch with enough points or run out of points
		while valid_batch == False:

			# Get the bounding box for the next batch
			self._batch_iterator = self._batch_iterator + 1 if self._has_more_batches() else 0
			batch_bbox = self._curr_batch_list[self._batch_iterator]

			# If scene is complete, load the next one
			if self._scene_complete == True:
				# No need to reload if only single scene in filelist
				if len(self._filelist)>1:
					self._load_model(self._filelist[self._scene_iterator], header=self._header)
				self._scene_complete = False

			batch_bbox = np.array(batch_bbox).astype(int)

			idx1 = self._encoder.encode((int(round((2**self._bpd-1) * (batch_bbox[0] - self._curr_scene_extent[0]) * self._x_scale)),
								         int(round((2**self._bpd-1) * (batch_bbox[1] - self._curr_scene_extent[1]) * self._y_scale))))

			idx2 = self._encoder.encode((int(round((2**self._bpd-1) * (batch_bbox[2] - self._curr_scene_extent[0]) * self._x_scale)),
								         int(round((2**self._bpd-1) * (batch_bbox[3] - self._curr_scene_extent[1]) * self._y_scale))))
			# Filter points using z-order index
			tmp_batch = self._curr_scene.loc[min(idx1, idx2):max(idx1, idx2)]

			# Convert batch to pandas dataframe
			tmp_batch = tmp_batch.compute()

			# Check if current batch has enough points
			if tmp_batch.values.shape[0] < self._num_points:
				pass
			elif tmp_batch.values.shape[0] >= self._num_points:
				# Need to sub-sample
				if sample_method == 'uniform':
					tmp_batch = pf.sub_sample(tmp_batch, n=self._num_points)
					valid_batch = True
					break
				elif sample_method == 'non-uniform':
					prob = pf.class_probabilities_index(set, min_prob=0.25)
					tmp_batch = pf.non_uniform_sample(tmp_batch, prob, self._num_points, max_repeats=10)
					valid_batch = True
					break
				print (tmp_batch.values.shape)


		# Check if we found a batch
		if valid_batch == True:
			pts = tmp_batch[self._features].values
			labels = tmp_batch['label'].values
			weights = self._get_batch_weights(labels)
		else:
			pts, labels, weights = None, None, None

		return pts, labels, weights


	""" Getters and Setters """

	@property
	def filelist(self):
		return self._filelist
	@filelist.setter
	def filelist(self, filelist):
		self._filelist = filelist

	@property
	def blocksize(self):
		return self._blocksize
	@blocksize.setter
	def blocksize(self, blocksize):
		self._blocksize = blocksize

	@property
	def num_workers(self):
		return self._num_workers
	@num_workers.setter
	def num_workers(self, num_workers):
		self._num_workers = num_workers

	@property
	def box_size(self):
		return self._box_size
	@box_size.setter
	def box_size(self, box_size):
		self._box_size = box_size

	@property
	def batch_iterator(self):
		return self._batch_iterator
	@batch_iterator.setter
	def batch_iterator(self, box_size):
		self._batch_iterator = batch_iterator
