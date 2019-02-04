import itertools
import numpy as np
import pandas as pd
import pointframes as pf
import sklearn.neighbors
import scipy.spatial
import progressbar
pd.options.mode.chained_assignment = None

known_features = ['sum_eigens', 'planarity','omnivariance', 'linearity', 'anisotropy',
                  'eigentropy', 'sum_eigens', 'scattering', 'curvature', 'point_density']

def calculate_covariance_matrix(data):
    """ Calculate covariance matrix for n x k points.

        args:

            data : numpy nd.array (n x k)

        returns:

            numpy ndarray (k x k)
    """

    C = np.zeros((data.shape[1], data.shape[1]))
    mean_xyz = [data[:,i].mean() for i in range(0, data.shape[1])]

    for i in range(0, C.shape[0]):
        for j in range(0, C.shape[1]):
            C[i][j] = np.sum((data[:, i] - mean_xyz[i])*(data[:, j]-mean_xyz[j]))

    return (1.0/data.shape[0]) * C

def eigenvalue_descriptors(convariance_matrix, features, nn, radius_neighbourhood):
    """ Compute eigenvalue based feature descriptors. By
        design always returns eigenvalues. Additional features
        can be defined in a feature list.

        args:

            convariance_matrix : numpy ndarray (k x k)
            features           : list

        returns:

            numpy ndarray (1 x 3 + num features)
    """

    D, V = np.linalg.eig(convariance_matrix)
    D.sort()
    evalue3, evalue2, evalue1 = D

    feature_desc = np.zeros((3+len(features)), dtype='float')
    feature_desc[0:3] = [evalue1, evalue2, evalue3]

    # Skip this if no additional features are requested
    if len(features) > 0 :

        # Convert to array so we can make use of np.where()
        # Maybe precompute these values once and pass into function to
        # save calculating for every point.
        features = np.array(features)

        D = (1/sum(D)*D)

        # Check which features to compute and add to array
        if 'linearity' in features:
            # Add three to get passed three eigen values
            feature_desc[np.where(features=='linearity')[0][0]+3] = (evalue1 - evalue2) / evalue1
        if 'planarity' in features:
            feature_desc[np.where(features=='planarity')[0][0]+3] = (evalue2 - evalue3) / evalue1
        if 'scattering' in features:
            feature_desc[np.where(features=='scattering')[0][0]+3] = evalue3 / evalue1
        if 'omnivariance' in features:
            misc1 = np.prod(D)
            feature_desc[np.where(features=='omnivariance')[0][0]+3] = pow(misc1,(1.0/3))
        if 'anisotropy' in features:
            feature_desc[np.where(features=='anisotropy')[0][0]+3] = (evalue1 - evalue3) / evalue1
        if 'eigentropy' in features:
            D_ = D+1e-17
            misc2 = (D_*np.log(D_))
            s = sum(misc2)*-1
            feature_desc[np.where(features=='eigentropy')[0][0]+3] = s
        if 'sum_eigens' in features:
            feature_desc[np.where(features=='sum_eigens')[0][0]+3] = sum(D)
        if 'curvature' in features:
            feature_desc[np.where(features=='curvature')[0][0]+3] = evalue3/sum(D)
        if 'point_density' in features:
            feature_desc[np.where(features=='point_density')[0][0]+3] = calculate_point_density(nn, radius_neighbourhood)

    return feature_desc

def calculate_point_density(nn, radius):
    """ Return point density of neighbourhood """
    return (nn+1.0)/((4.0/3)*np.pi*pow(radius, 3))

def compute_eigenvalues(pointcloud, nn, features=[], leaf_size=40):
    """ Compute eigenvalues for local neighbourhood of point defined by nn.
        Optionally, aditional eigenvalue based features can be computed by
        populating a list (in no particular order) containing one or more of
        the following:

        [sum_eigens, planarity,omnivariance, linearity, anisotropy,
         eigentropy, sum_eigens, scattering, curvature, point_density]

         args:

            pointcloud : pandas dataframe
            nn         : Int (number of neighbours)
            features   : list
            leaf size  : Int (leaf size for kd-tree)

        returns:

            pandas dataframe
    """

    pf.check_attributes(['X', 'Y', 'Z'])

    for feature in features:
        assert feature in known_features, "Unknown feature {:}".format(feature)

    xyz = pointcloud[['X', 'Y', 'Z']].values

    # Compute KDTree and produce index list
    print ('[INFO] Constructing and indexing KDTree ...')
    kd_tree = sklearn.neighbors.KDTree(xyz, leaf_size=leaf_size, metric='euclidean')
    idx_list = kd_tree.query(xyz, k=nn, return_distance=False, sort_results=True)

    point_density = []

    # Construct empty array to populate
    feature_arr = np.zeros((xyz.shape[0], 3+len(features)), dtype='float')

    # Computation can take a long time so initalise a progress bar
    print ('[INFO] Calculating eigenvalues + {:} features for {:} points ...'.format(len(features), xyz.shape[0]))
    bar = progressbar.ProgressBar(maxval=xyz.shape[0], \
    widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    bar.start()

    for i, idx in enumerate(idx_list):
        bar.update(i+1)
        neighbourhood = xyz[idx]
        # Only compute if we need to
        radius_neighbourhood = scipy.spatial.distance.euclidean(xyz[idx[0]], xyz[idx[-1]]) if 'point_density' in features else None
        # Compute the covariance matrix
        C = calculate_covariance_matrix(neighbourhood)
        # Compute the feature array
        feature_arr[i] = eigenvalue_descriptors(C, features, nn, radius_neighbourhood)

    bar.finish()

    # Add eigenvalues to features
    features = ['eig1', 'eig2', 'eig3'] + features
    # Add the new columns to data frame
    for idx, feature in enumerate(features):
        pointcloud[feature] = feature_arr[:, idx]

    return pointcloud
