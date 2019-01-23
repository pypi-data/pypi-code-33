



import os
from os.path import join as jph

from nilabels.agents.agents_controller import AgentsController as LT
from nilabels.tools.aux_methods.label_descriptor_manager import LabelsDescriptorManager as LDM

lt = LT()

root_multi_atlas = '/Users/sebastiano/Dropbox/RabbitEOP-MRI/study/A_MultiAtlas'
multi_atlas_subjects = ['1201', '1203', '1305', '1404', '1507', '1510', '1702', '1805', '2002', '2502', '3301', '3404']



pfi_label_descriptor = jph(root_multi_atlas, 'labels_descriptor.txt')
assert os.path.exists(pfi_label_descriptor)
ldm = LDM(pfi_label_descriptor)

for sj in multi_atlas_subjects:

    print '---------------------------'
    print '---------------------------'
    print 'Cleaning subject {}'.format(sj)
    print '---------------------------\n\n'

    pfi_segm = jph(root_multi_atlas, sj, 'segm', '{}_approved_round3.nii.gz'.format(sj))
    assert os.path.exists(pfi_segm)

    # get the report before
    pfi_log_file_before = jph(root_multi_atlas, sj, 'segm', '{}_approved_round3_connected_components.txt'.format(sj))
    lt.check.number_connected_components_per_label(pfi_segm, where_to_save_the_log_file=pfi_log_file_before)

    # get the labels_correspondences - do not clean the 0, get 2 components for the 201
    labels = ldm.get_dict_itk_snap().keys()
    correspondences_lab_comps  = []
    for l in labels:
        if l == 201:
            correspondences_lab_comps.append([l, 3])
        elif l == 229:
            correspondences_lab_comps.append([l, 2])
        elif l == 230:
            correspondences_lab_comps.append([l, 2])
        elif l == 127:
            correspondences_lab_comps.append([l, 2])
        elif l == 0:
            pass
        else:
            correspondences_lab_comps.append([l, 1])

    print correspondences_lab_comps

    # get the cleaned segmentation
    pfi_ouput_cleaned_segmentation = jph(root_multi_atlas, sj, 'segm', '{}_approved_round3_cleaned2.nii.gz'.format(sj))
    lt.manipulate_labels.clean_segmentation(pfi_segm, pfi_ouput_cleaned_segmentation,
                                            labels_to_clean=correspondences_lab_comps)

    # get the report of the connected components afterwards
    pfi_log_file_before = jph(root_multi_atlas, sj, 'segm', '{}_approved_round3_cleaned_connected_components.txt'.format(sj))
    lt.check.number_connected_components_per_label(pfi_ouput_cleaned_segmentation, where_to_save_the_log_file=pfi_log_file_before)

    # get the differences between the non-liceaned and the cleaned:
    pfi_diff_cleaned_non_cleaned = jph(root_multi_atlas, sj, 'segm', 'z_{}_cleaned_voxels_positions.nii.gz'.format(sj))
    cmd = 'seg_maths {0} -sub {1} {2}'.format(pfi_segm, pfi_ouput_cleaned_segmentation, pfi_diff_cleaned_non_cleaned)
    os.system(cmd)
    cmd = 'seg_maths {0} -bin {0}'.format(pfi_diff_cleaned_non_cleaned)
    os.system(cmd)



#
#
# from nilabel.tools.aux_methods.utils_nib import set_new_data
# import nibabel as nib
#
# im = nib.load('/Users/sebastiano/Desktop/1201_segm.nii.gz')
# new_im = set_new_data(im, segm_with_holes)
# nib.save(new_im, '/Users/sebastiano/Desktop/1201_segm_with_holes.nii.gz')



# if __name__ == '__main__':
#
#
#     pfi_lab_26 = '/Users/sebastiano/Desktop/1201_only_26.nii.gz'
#
#     im = nib.load(pfi_lab_26)
#
#     arr = island_for_label(im.get_data(), 26, emphasis_max=True, special_label=255)
#
#     im_new = set_new_data(im, arr)
#
#     nib.save(im_new, '/Users/sebastiano/Desktop/1201_only_26_scored.nii.gz')
