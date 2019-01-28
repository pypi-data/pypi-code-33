import numpy as np


class sampling(object):


    # The samples generating code will also generate flips (horizontal, vertical) or rotations (0-90-180-270).
    # When a flip or rotation are selected each possible choice will occur with equal probability.
    # These are helpful for augmenting the training data.
    @staticmethod
    def image_random_subsampler(image_size, n_samples, tile_size, percentage_flip=0.0, percentage_rotation=0.0):
        if tile_size > image_size[0] or tile_size > image_size[1]:
            return []

        x = np.random.randint(0, image_size[0]-tile_size, size=n_samples).tolist()
        y = np.random.randint(0, image_size[1]-tile_size, size=n_samples).tolist()
        samples = [dict(x=x[i], dx=tile_size, y=y[i], dy=tile_size,
                        hflip=False, vflip=False, rot=0.0) for i in range(n_samples)]

        if percentage_flip != 0:
            hv = np.random.uniform(size=(n_samples, 2)) <= percentage_flip / 2
            [s.update(dict(hflip=hv[i,0], vflip=hv[i,1])) for i,s in enumerate(samples)]

        if percentage_rotation != 0:
            do = np.random.uniform(size=n_samples) <= percentage_rotation
            rot = np.random.randint(0, 3, size=(n_samples)) * 90.0 * do
            [s.update(dict(rot=rot[i])) for i,s in enumerate(samples)]

        return samples

    # This returns a set of tiles that entirely cover an image, with no overlap except what is required to preserve
    # tile size at right and bottom borders. Use with XXX to stitch tiles back onto an image.
    @staticmethod
    def image_tile_subsampler(image_size, tile_size):
        if tile_size > image_size[0] or tile_size > image_size[1]:
            return []

        upper_left = [[i, j]
                      for i in range(0, image_size[0] - tile_size, tile_size)
                      for j in range(0, image_size[1] - tile_size, tile_size)]
        right_vertical = [[image_size[0] - tile_size, j]
                          for j in range(0, image_size[1] - tile_size, tile_size)]
        bottom_row = [[i, image_size[1] - tile_size]
                      for i in range(0, image_size[0] - tile_size, tile_size)]
        bottom_right = [[image_size[0] - tile_size, image_size[1] - tile_size]]
        tiles = upper_left + right_vertical + bottom_row + bottom_right

        samples = [dict(x=x, dx=tile_size, y=y, dy=tile_size,
                        hflip=False, vflip=False, rot=0.0) for (x,y) in tiles]

        return samples

    @staticmethod
    def _subsample_matrix(image, sample):
        return image[sample["x"]:sample["x"]+sample["dx"], sample["y"]:sample["y"]+sample["dy"], :]

    @staticmethod
    def extract_subsamples(image, samples):
        return [sampling._subsample_matrix(image, sample) for sample in samples]


    # This method takes an image of size [n_d1, n_d2, n_bands] and a stack of n_samples, and their values of size
    # [n_samples, n_d1, n_d2, n_bands] and "inserts" the stack of sample values into the image at their appropriate
    # location. Notice that this will ignore rotation and flipping.
    @staticmethod
    def transfer_into_image(image, samples, sample_matrices, add_border_to_samples=False):
        if add_border_to_samples:
            sample_matrices = sampling._add_border_to_samples(sample_matrices)

        for i in range(0, len(samples)):
            image[samples[i]["x"]:samples[i]["x"]+samples[i]["dx"], samples[i]["y"]:samples[i]["y"]+samples[i]["dy"]] \
                = sample_matrices[i]
        return image

    # Adds NaN to a border of a sample. Useful for visualization.
    @staticmethod
    def _add_border_to_samples(sample_matrices, value=np.NaN, depth=3, inset=0):
        sample_matrices[:,:,inset:-(inset+1),inset:depth] = value
        sample_matrices[:,:,inset:-(inset+1),-(depth+1):-(inset+1)] = value
        sample_matrices[:,:,inset:depth,inset:-(inset+1)] = value
        sample_matrices[:,:,-(depth+1):-(inset+1),inset:-(inset+1)] = value
        return sample_matrices
