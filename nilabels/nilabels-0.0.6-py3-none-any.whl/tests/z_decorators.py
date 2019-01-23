import os
from os.path import join as jph
import numpy as np
import nibabel as nib


# PATH manager


test_dir = os.path.dirname(os.path.abspath(__file__))
pfo_tmp_test = jph(test_dir, 'z_tmp_test')
pfi_dummy_c  = jph(test_dir, 'z_tmp_test', 'dummy_c.nii.gz')


# AUXILIARIES


def c_shape(omega=(250, 250, 250), internal_radius=40, external_radius=60, opening_height=50,
            background_intensity=0, foreground_intensity=20):
    def get_a_2d_c(omega2, internal_radius2d, external_radius2d, opening_height2d):
        m = background_intensity * np.ones(omega2[:2], dtype=np.uint8)
        c = [omega2[j] / 2 for j in range(len(omega2))]
        # create the crown
        for x in range(omega2[0]):
            for y in range(omega2[1]):
                if internal_radius2d ** 2 < (x - c[0]) ** 2 + (y - c[1]) ** 2 < external_radius2d ** 2:
                    m[x, y] = foreground_intensity
        # open the c
        low_lim = int(omega2[0] / 2) - int(opening_height2d / 2)
        high_lim = int(omega2[0] / 2) + int(opening_height2d / 2)
        for x in range(omega2[0]):
            for y in range(int(omega2[1] / 2), omega2[1]):
                if low_lim < x < high_lim and m[x, y] == foreground_intensity:
                    m[x, y] = background_intensity
        return m

    c_2d = get_a_2d_c(omega2=omega[:2], internal_radius2d=internal_radius, external_radius2d=external_radius,
                      opening_height2d=opening_height)
    return np.repeat(c_2d, omega[2]).reshape(omega)


# DECORATORS


def create_and_erase_temporary_folder_with_dummy_c(test_func):
    def wrap(*args, **kwargs):
        # 1) Before: create folder
        os.system('mkdir {}'.format(pfo_tmp_test))
        im = nib.Nifti1Image(c_shape(), affine=np.eye(4))
        nib.save(im, pfi_dummy_c)
        # 2) Run test
        test_func(*args, **kwargs)
        # 3) After: delete folder and its content
        os.system('rm -r {}'.format(pfo_tmp_test))
    return wrap