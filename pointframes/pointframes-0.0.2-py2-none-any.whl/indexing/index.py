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

    x_scale = scalar / (scene_bbox[2] - scene_bbox[0])
    y_scale = scalar / (scene_bbox[3] - scene_bbox[1])
    x_coord = int(round((2**bpd-1) * (pt[0] - scene_bbox[0]) * x_scale))
    y_coord = int(round((2**bpd-1) * (pt[1] - scene_bbox[1]) * y_scale))

    return encoder.encode((x_coord, y_coord))


def encode_pt_3d(pt, scalar, encoder, scene_bbox, bpd=32):

    x_scale = scalar / (scene_bbox[2] - scene_bbox[0])
    y_scale = scalar / (scene_bbox[3] - scene_bbox[1])
    z_scale = scalar / (scene_bbox[5] - scene_bbox[2])
    x_coord = int(round((2**bpd-1) * (pt[0] - scene_bbox[0]) * x_scale))
    y_coord = int(round((2**bpd-1) * (pt[1] - scene_bbox[1]) * y_scale))
    z_coord = int(round((2**bpd-1) * (pt[2] - scene_bbox[1]) * y_scale))

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

    if dask == False:

        columns = pc.columns
        xyz_ind = [pc.columns.get_loc(c) for c in ['X','Y','Z']]
        pc_arr = pc.values
        # Create empty array with extra column for z_order
        pc = np.zeros((pc_arr.shape[0], pc_arr.shape[1]+1))
        # Populate with existing data columns
        pc[:, 1:] = pc_arr
        pc_arr = None

        if ndims == 2:
            encoder = pf.ZEncoder(2, 2*bpd)
            pc[:,0] = np.apply_along_axis(encode_pt_2d, 1, pc[:,1:3], scalar, encoder, scene_bbox)
        elif ndims == 3:
            encoder = pf.ZEncoder(3, 2*bpd)
            pc[:,0] = np.apply_along_axis(encode_pt_3d, 1, pc[:,1:4], scalar, encoder, scene_bbox)
        else:
            raise ValueError("Dimensions must be either 2 or 3")

        return pd.DataFrame(data=pc, columns=columns.insert(0, 'z_ord'))

    else:

        if ndims == 2:
            encoder = pf.ZEncoder(2, ndims*bpd)
        elif ndims == 3:
            encoder = pf.ZEncoder(3, ndims*bpd)
        else:
            raise ValueError("Dimensions must be either 2 or 3")
        z_ord = np.apply_along_axis(encode_pt_2d, 1, pc[['X' , 'Y', 'Z']].values, scalar, encoder, scene_bbox)
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

    xyz_ind = [pc.columns.get_loc(c) for c in ['X','Y','Z']]
    columns = pc.columns
    pc = pc.values

    if len(bbox) == 4:
        pc = pc[(pc[:,xyz_ind[0]] >= bbox[0]) & (pc[:,xyz_ind[0]] <= bbox[2]) & \
                (pc[:,xyz_ind[1]] >= bbox[1]) & (pc[:,xyz_ind[1]] <= bbox[3])]
    elif len(bbox) == 6:
        pc = pc[(pc[:,xyz_ind[0]] >= bbox[0]) & (pc[:,xyz_ind[0]] <= bbox[3]) & \
                (pc[:,xyz_ind[1]] >= bbox[1]) & (pc[:,xyz_ind[1]] <= bbox[4]) & \
                (pc[:,xyz_ind[2]] >= bbox[2]) & (pc[:,xyz_ind[1]] <= bbox[5])]
    else:
        raise ValueError("Dimensions must be either 2 or 3")

    return pd.DataFrame(data=pc, columns=columns)


def select_points(pc, bbox, z_order=False, x_scale=None, y_scale=None, bpd=32):
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

    bbox = [int(round(i)) for i in bbox]
    # Check if z order indexing is present
    if z_order == True:
        print ('[info] Selecting with z-order...')
        # Check dimensions
        if len(bbox) == 4:
            # Get encoder object
            encoder = pf.ZEncoder(2)

            x_coord = int(round((2**bpd-1) * (pt[0] - scene_bbox[0]) * x_scale))
            y_coord = int(round((2**bpd-1) * (pt[1] - scene_bbox[1]) * y_scale))

            pc = pc.loc[encoder.encode(bbox[2:]):encoder.encode(bbox[:2])]

        elif len(bbox) == 6:
            encoder = pf.ZEncoder(3)
            pc = pc.loc[encoder.encode(bbox[3:]):encoder.encode(bbox[:3])]
        else:
            raise ValueError("Error: Dimensions must be either 2 or 3")
    else:

        pc = pf.filter_xyz(pc, bbox)

    return pc
