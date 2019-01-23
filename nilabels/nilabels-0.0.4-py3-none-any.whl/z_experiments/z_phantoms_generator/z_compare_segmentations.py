"""
Module based on nifty path to file due to the need of performing registration on the data.
--------
Notes on how to get SVFs from NiftyReg.

SVF are obtained from NiftyReg as follows reg_f3d with command -vel, returning the corresponding cpp grid as the
control point grid we are interested in.
The dense vector field that corresponds to the given gpp grid is then provided with -flow and it
is obtained in 'deformation coordinates' (Eulerian coordinate system).
To have it in displacement coordinate system (Lagrangian coordinate system) for our elaboration we need to
subtract them the identity with python (not with - disp in niftyReg, otherwise it will be exponentiated again).
"""
import os
from os.path import join as jph

import nibabel as nib
import numpy as np
import pandas as pd

from nilabels.tools.aux_methods.label_descriptor_manager import LabelsDescriptorManager
from nilabels.tools.aux_methods.utils import set_new_data


def get_errors_data_frame(pfi_segm1, pfi_segm2, pfo_intermediate_files, pfi_label_descriptor,
                          pfi_output_table=None, erase_intermediate=False, tag=''):

    """
    Images in intermediate files are saved as
    im_<image name>_<label_name>_tag_<tag>.nii.gz
    :param pfi_segm1:
    :param pfi_segm2:
    :param pfo_intermediate_files:
    :param pfi_label_descriptor:
    :param pfi_output_table:
    :param erase_intermediate:
    :param tag:
    :return:
    """
    im1 = nib.load(pfi_segm1)
    im2 = nib.load(pfi_segm2)
    assert im1.shape == im2.shape
    list_labels_1 = sorted(list(set(im1.get_data().flat)))
    list_labels_2 = sorted(list(set(im2.get_data().flat)))
    assert list_labels_1 == list_labels_2

    ldm = LabelsDescriptorManager(pfi_label_descriptor)
    multi_label = ldm.get_multi_label_dict()

    # create data-frame to fill:
    regions = multi_label.keys()
    s_dice  = pd.Series(np.zeros(len(regions)), index=regions)
    s_dispe = pd.Series(np.zeros(len(regions)), index=regions)
    s_prec  = pd.Series(np.zeros(len(regions)), index=regions)

    # PHASE 1 - save the splitted images -
    # split images in binarised segmentations components, one for each region.
    for r in regions():
        # get image data:
        data_r1 = np.zeros(im1.shape, dtype=np.bool)
        data_r2 = np.zeros(im2.shape, dtype=np.bool)
        for p in multi_label[r]:
            data_r1 += im1.get_data == p
            data_r2 += im1.get_data == p
        # get images names and filenames:
        str_label = r.split().replace(' ', '_')
        im_name_1 = os.path.basename(pfi_segm1).split('.')[0]
        im_name_2 = os.path.basename(pfi_segm2).split('.')[0]
        filename_im1_region_r = 'im_' + im_name_1 + '_' + str_label + '_tag_' + str(tag) + '.nii.gz'
        filename_im2_region_r = 'im_' + im_name_2 + '_' + str_label + '_tag_' + str(tag) + '.nii.gz'
        pfi_im1_region_r = jph(pfo_intermediate_files, filename_im1_region_r)
        pfi_im2_region_r = jph(pfo_intermediate_files, filename_im2_region_r)
        # get new type as boolean, get new data, same header as the original image.
        nib.save(set_new_data(im1, data_r1, new_dtype=np.bool), pfi_im1_region_r)
        nib.save(set_new_data(im2, data_r2, new_dtype=np.bool), pfi_im2_region_r)

        # s_dice[r] = get_dice_score(pfi_im1_region_r, pfi_im2_region_r)
        # s_dispe[r] = get_dispersion(pfi_im1_region_r, pfi_im2_region_r, pfo_intermediate_files, tag=r)
        # s_prec[r] = get_precision(pfi_im1_region_r, pfi_im2_region_r, pfo_intermediate_files, tag=r)

    df = pd.DataFrame({'Similarity' : s_dice, 'Dispersion' : s_dispe, 'Precision' : s_prec})
    print(df)
    if pfi_output_table is None:
        pfi_output_table = os.path.join(pfo_intermediate_files, 'result.pkl')
    df.to_pickle(pfi_output_table)
    print('Data frame saved in {}'.format(pfi_output_table))
