import numpy as np
import pandas as pd
import pointframes as pf
import decimal
import dask
import dask.dataframe as dd

def compute_z_order_dask(df, scalar=1., bpd=32, index=True):
	""" Compute the z-order of a dask dataframe.

		args:
			df    : dask dataframe
			index : bool
					  Index dataframe to z-order

		returns:
			df : computed dask dataframe
	"""

	xmin, xmax, ymin, ymax, zmin, zmax = dask.compute(df.X.min(), df.X.max(),
													  df.Y.min(), df.Y.max(),
													  df.Z.min(), df.Z.max())
	scene_bbox = [xmin, xmax, ymin, ymax, zmin, zmax]

	npartitions = df.npartitions
	print ('[info] processing file with {:} partitions'.format(npartitions))
	df['z_ord'] = df.map_partitions(lambda x: pf.spatial_index(x, 2, scalar=scalar, bpd=bpd, scene_bbox=scene_bbox, dask=True))
	print ('[info] indexing...')
	df = df.set_index(df.z_ord)
	print ('[info] set up complete... computing csvs...')
	df = df[['z_ord'] + list(df.columns[:-1])]
	return df


def spatial_bounds(pc):
	"""
	Compute the axis aligned bounding box of the point cloud.

	args
		pc : pandas dataframe
	returns
		tuple
			Minimum and maximum of X, Y and Z coordinates following the format
			(minX, minY, minZ, maxX, maxY, maxZ)
	"""

	pc = pc[['X', 'Y', 'Z']].values
	return (min(pc[:,0]), min(pc[:,1]), min(pc[:,2]),
			max(pc[:,0]), max(pc[:,1]), max(pc[:,2]))


def encode_pt_2d(pt, scalar, encoder, scene_bbox, bpd=32):

	x_scale = scalar / (scene_bbox[3] - scene_bbox[0])
	y_scale = scalar / (scene_bbox[4] - scene_bbox[1])
	x_coord = int(round((2**bpd-1) * (pt[0] - scene_bbox[0]) * x_scale))
	y_coord = int(round((2**bpd-1) * (pt[1] - scene_bbox[1]) * y_scale))

	return encoder.encode((x_coord, y_coord))


def encode_pt_3d(pt, scalar, encoder, scene_bbox, bpd=32):

	x_scale = scalar / (scene_bbox[3] - scene_bbox[0])
	y_scale = scalar / (scene_bbox[4] - scene_bbox[1])
	z_scale = scalar / (scene_bbox[5] - scene_bbox[2])
	x_coord = int(round((2**bpd-1) * (pt[0] - scene_bbox[0]) * x_scale))
	y_coord = int(round((2**bpd-1) * (pt[1] - scene_bbox[1]) * y_scale))
	z_coord = int(round((2**bpd-1) * (pt[2] - scene_bbox[2]) * y_scale))

	return encoder.encode((x_coord, y_coord, z_coord))


def spatial_index(pc, ndims, scalar=1., bpd=32, scene_bbox=None, dask=False):
	"""
	Compute a linear key for each point of the point cloud.

	This may use the Morton code as a space filling curve (SFC). The index is
	computed on a shifted point cloud to optimize the domain for more efficient
	encoding.The computed code is packed into a 64bit integer. The function is
	a mapping function (XYZ) -> <k, (XYZ)>

	args
		pc : pandas datafram
		bb : tuple
			 The bounding box of the pc as (minX, minY, minZ, maxX, maxY, maxZ)

	returns
		pandas dataframe
	"""


	if scene_bbox == None:
		scene_bbox = spatial_bounds(pc)

	if ndims == 2:
		encoder = pf.ZEncoder(2, ndims*bpd)
		z_ord = np.apply_along_axis(encode_pt_2d, 1, pc[['X' , 'Y']].values, scalar, encoder, scene_bbox)
	elif ndims == 3:
		encoder = pf.ZEncoder(3, ndims*bpd)
		z_ord = np.apply_along_axis(encode_pt_3d, 1, pc[['X' , 'Y', 'Z']].values, scalar, encoder, scene_bbox)
	else:
		raise ValueError("Dimensions must be either 2 or 3")

	if dask == False:
		pc['z_ord'] = z_ord
		return pc
	else:
		return pd.Series(z_ord).astype('int64')


def filter_xyz(pc, bbox):
	""" Simple filter by bounding box for pandas dataframe.

		Bounding box should be a list with values:
		[xmin, ymin, xmax, ymax] or
		[xmin, ymin, zmin, xmax, ymax, zmax]

		args:
			pc : pandas dataframe
			bb : list
		returns:
			pandas dataframe
	"""

	pf.check_attributes(['X', 'Y', 'Z'])

	if len(bbox) == 4:
		pc = pc[(pc['X'] >= bbox[0]) & (pc['X'] <= bbox[2]) & \
			    (pc['Y'] >= bbox[1]) & (pc['Y'] <= bbox[3])]
	elif len(bbox) == 6:
		pc = pc[(pc['X'] >= bbox[0]) & (pc['X'] <= bbox[2]) & \
				(pc['Y'] >= bbox[1]) & (pc['Y'] <= bbox[3])
				(pc['Z'] >= bbox[2]) & (pc['Z'] <= bbox[5])]
	else:
		raise ValueError("Dimensions must be either 2 or 3")

	return pc

def select_points(pc, bbox, z_order=False, scalar=1., bpd=32):
	""" Select point within a given bounding box.
		Bounding box should be a list with values:
		[xmin, ymin, xmax, ymax] or
		[xmin, ymin, zmin, xmax, ymax, zmax]

		args:
			bounding_box : list
			z_order      : bool
							 Use z-order indexing
		returns:
			pandas dataframe [or] series
	"""

	pf.check_attributes(['X', 'Y', 'Z'])
	columns = pc.columns

	scene_extent = pf.spatial_bounds(pc)
	# Check if z order indexing is present
	if z_order == True:
		print ('[info] Selecting with z-order...')
		# Check dimensions
		if len(bbox) == 4:
			# Get encoder object
			encoder = pf.ZEncoder(2)

			idx1 = pf.encode_pt_2d([bbox[0], bbox[1]], scalar, encoder, scene_extent, bpd)
			idx2 = pf.encode_pt_2d([bbox[2], bbox[3]], scalar, encoder, scene_extent, bpd)

		elif len(bbox) == 6:

			encoder = pf.ZEncoder(3)

			idx1 = pf.encode_pt_3d([bbox[0], bbox[1], bbox[2]], scalar, encoder, scene_extent, bpd)
			idx2 = pf.encode_pt_3d([bbox[3], bbox[4], bbox[5]], scalar, encoder, scene_extent, bpd)

		else:

			raise ValueError("Error: Dimensions must be either 2 or 3")

		if pc.index.name == 'z_ord':
			pc = pc.loc[min(idx1, idx2):max(idx1,idx2)]
		else:
			pc = pc.loc[pc['z_ord']>min(idx1, idx2) & pc['z_ord']>max(idx1, idx2)]

	else:

		pc = pf.filter_xyz(pc, bbox)

	return pc
