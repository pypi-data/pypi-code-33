import pandas as pd
import numpy as np
import pointframes as pf

def min_class_partition(pointcloud, class_ind, return_all=False):
    """ Balance the number of observations per-class of a pointcloud
        By randomly sub-sampling all classes to the minimum observed
        class. If return_all is set to 'True' the subsampled classes
        can be returned as well for test data.

        args:
            pointcloud : pandas dataframe
            class_ind  : Int
            return_all : Bool
        returns:
            pandas dataframe OR 2 x pandas dataframe
    """

    columns = pointcloud.columns
    data = pointcloud.values

    unique, count = np.unique(data[:, class_ind], return_counts=True)

    for i, c in enumerate(unique):
        class_arr = data[np.where(data[:, class_ind]==c)]
        sample = np.random.randint(low=0, high=class_arr.shape[0], size=min(count))
        sampled_data = class_arr[sample] if i == 0 else np.vstack((sampled_data, class_arr[sample]))
        if return_all == True:
            inv_sub_sample = np.delete(class_arr, sample, 0)
            inv_sampled_data = inv_sub_sample if i == 0 else np.vstack((inv_sampled_data, inv_sub_sample))

    sampled_df = pd.DataFrame(data=sampled_data, columns=columns)

    if return_all == True:
        inv_sampled_df = pd.DataFrame(data=inv_sampled_data, columns=columns)
        return sampled_df, inv_sampled_df
    else:
        return sampled_df

def shuffle_pointcloud(pointcloud, array=False):
    """ Randomly shuffle the order of a pandas dataframe (array=False) or
        a numpy array (array = True), by axis 0 (rows).

        args:
            pointcloud : pandas dataframe OR numpy array [n x k]
            array      : Bool
                           Make True if input in numpy array
        returns:
            numpy array [n x k]
    """

    if array == False:
        columns = pointcloud.columns
        pointcloud = pointcloud.values

    idx = np.arange(pointcloud.shape[0])
    np.random.shuffle(idx)
    pointcloud = pointcloud[idx, :]

    if array == False:
        df = pd.DataFrame(data=pointcloud, columns=columns)
        return df
    else:
        return pointcloud

def class_probabilities_index(pointcloud, min_prob=0.25):
    """ Return a probability index for each class in a pointcloud.
        Probabilities are designed for pf.non_uniform_sample() function.

        args:
            pointcloud : pandas dataframe
            min_prob   : Float
                           Minimum probability a class can have
            returns:
                numpy array [n x 1]
    """
    pf.check_attributes(pointcloud, ['class'])

    # Find unique classes and return their count
    cats, counts = np.unique(pointcloud['class'].values, return_counts=True)
    # Normalise the counts [0, 1]
    counts = counts.astype(np.float32)
    counts /= np.max(np.abs(counts), axis=0)
    # Invert to weigh under represented classes higher
    # Shift to minimum probability
    # Better way to do this???
    counts = (1 - counts)

    probabilities = np.zeros((pointcloud.values.shape[0], 1))

    for i, c in enumerate(pointcloud['class'].values):
        probabilities[i] = counts[np.where(cats == c)[0][0]]

    return probabilities


def non_uniform_sample(pointcloud, probabilites, n=100, seed=None, max_repeats=10, shuffle=False):
    """ Non-uniform sampling of point cloud where probability of
        being selected is defined by a corresponding probabilities
        array. Also performs shuffle to order of point cloud by design.

        args:
            pointcloud   : pandas dataframe
            probabilites : numpy array [n x k]
                             Where n, k match pandas dataframe .values() shape
            n            : int
                             number of points
            seed         : int
                             Random state seed (if none, uses clock time)
    """

    rs = np.random.RandomState(seed=None)
    # Store columns for reassembly of dataframe
    columns = pointcloud.columns
    # Shuffle points for fairness if not already done
    if shuffle == True:
        pointcloud = pf.shuffle_pointcloud(pointcloud.values, array=True)
    else:
        pointcloud = pointcloud.values

    i = 0
    repeats = 0
    num_points = 0
    sampled_pts = []
    remaining_pts = []
    # Loop through pointcloud appending points
    while i <= pointcloud.shape[0]:
        if repeats > max_repeats:
            #print("[warning] Max repeats: {:} reached, returning None".format(max_repeats))
            return None
        if pointcloud.shape[0] == 0:
            #print("[warning] Point cloud too small, returning None".format(max_repeats))
            return None

        rnd_num = rs.random_sample()

        if rnd_num < probabilites[i]:
            sampled_pts.append(pointcloud[i])
            # Increment the number of points variable
            num_points += 1
        else:
            # Add remaining points to new array so we
            # don't repeat points. This is much faster
            # and less memory intensive than using np.delete()
            remaining_pts.append(pointcloud[i])

        if num_points == n:
            # We have enough points so exit
            break

        if i == pointcloud.shape[0]-1:
            # We don't have enough points so restart the counter
            i = 0
            repeats += 1
            pointcloud = np.array(remaining_pts)
            remaining_pts = []
        else:
            i += 1

    pointcloud = np.array(sampled_pts)
    #Reconstruct the dataframe
    df = pd.DataFrame(data=pointcloud, columns=columns)
    return df



def sub_sample(pointcloud, n=100):
    ''' Function to randomly subsample pointcloud to n
        number of points. If n is larger than pointcloud
        None is returned.

        args:
            pointcloud : pandas dataframe
            n          : int number of point to return
        returns:
            pandas dataframe
    '''

    n_greater = False

    if pointcloud.values.shape[0] > n:
        pointcloud = pointcloud.sample(n=n)
    elif pointcloud.values.shape[0] < n:
        n_greater = True

    if n_greater == True:
        pointcloud = None

    return pointcloud

def n_partition(pointcloud, n=1, ret_objects=False):
    ''' Function to divide a point cloud into partitions with n points.
        The return is a list of dataframes or PointCloud objects where the
        number of points = n

        args:
            pointcloud : pandas dataframe
            n          : int
        returns:
            list (containing dataframes or PointCloud objects)
    '''

    # Check attributes are present
    pf.check_attributes(pointcloud, ['X', 'Y', 'Z'])

    # Convert to numpy array as this offers 100% speed increase
    # from working directly with Pandas
    columns = pointcloud.columns
    pc_arr = pointcloud.values

    # Save memory
    pointcloud = None

    # Determine remainder points after split and remove
    if (len(pc_arr) % n) != 0:
        pc_arr = pc_arr[0:-(len(pc_arr) % n)]
    # Split the point cloud
    array_list = np.array(np.split(pc_arr, (len(pc_arr)/n)))
    partition_list = []
    # Convert back to dataframes
    [partition_list.append(pd.DataFrame(data=d, columns=columns)) for d in array_list]

    # Loop through and convert all dataframes to PointCloud objects
    if ret_objects == True:
        object_list = []
        for partition in partition_list:
            pc = pf.PointCloud()
            pc.data = partition
            object_list.append(pc)
        partition_list = object_list

    return partition_list

def get_extent(pointcloud, n_dims=2):
    ''' Function to return the horizontal limits for
        a PointCloud object.

        args:
            pointcloud : pandas dataframe
            n_dims     : Int (either 2 or 3)
        returns:
            list (xmin, ymin, xmax, ymax)
    '''

    if n_dims == 2:
        xmin = np.min(pointcloud['X'])
        ymin = np.min(pointcloud['Y'])
        xmax = np.max(pointcloud['X'])
        ymax = np.max(pointcloud['Y'])
        return [xmin, ymin, xmax, ymax]
    elif n_dims == 3:
        xmin = np.min(pointcloud['X'])
        ymin = np.min(pointcloud['Y'])
        xmax = np.max(pointcloud['X'])
        ymax = np.max(pointcloud['Y'])
        zmin = np.min(pointcloud['Z'])
        zmax = np.max(pointcloud['Z'])
        return [xmin, ymin, zmin, xmax, ymax, zmax]
    else:
        raise ValueError("Number of dimensions must be 2 or 3")

def partition_by_xy(pointcloud, box_size, ret_objects=False):
    ''' Function to partition a point cloud by a box size in the
        unit of the point cloud (i.e. meters). Returns a list of
        dataframes or PointCloud objects.

        args:
            pointcloud : Pandas dataframe
            box_size   : float
        returns:
            list (containing dataframes or PointCloud objects)

    '''

    pf.check_attributes(pointcloud, ['X', 'Y', 'Z'])

    # Find the XY extent of the pointcloud
    pc_extent = get_extent(pointcloud)
    xmin, ymin, xmax, ymax = pc_extent

    # Convert to numpy array as this offers 100% speed increase
    # from working directly with Pandas
    columns = pointcloud.columns
    pc_arr = pointcloud.values

    # Save memory
    pointcloud = None

    num_xstrides = int(np.floor((xmax-xmin) / box_size))
    num_ystrides = int(np.floor((ymax-ymin) / box_size))

    # Get a list of the coordinates to sample the point cloud by.
    sample_coords = []
    for x_stride in range(0, num_xstrides):
        for y_stride in range(0, num_ystrides):
            sample_coords.append([xmin+(x_stride*box_size), \
                                  ymin+(y_stride*box_size), \
                                  xmin+((x_stride*box_size)+box_size), \
                                  ymin+((y_stride*box_size)+box_size)])
    sample_coords = np.array(sample_coords)

    # Filter coordinates by sample coordinate parameters.
    sampled_pts = []
    for volume in sample_coords:
        xmin, ymin, xmax, ymax = volume
        batch_pts = pc_arr[(pc_arr[:,0] > xmin) & (pc_arr[:,0] < xmax) & \
                            (pc_arr[:,1] > ymin) & (pc_arr[:,1] < ymax)]
        sampled_pts.append(batch_pts)

    partition_list = []
    # Convert back to dataframes
    [partition_list.append(pd.DataFrame(data=d, columns=columns)) for d in sampled_pts]

    # Loop through and convert all dataframes to PointCloud objects
    if ret_objects == True:
        object_list = []
        for partition in partition_list:
            pc = pf.PointCloud()
            pc.data = partition
            object_list.append(pc)
        partition_list = object_list

    return partition_list
