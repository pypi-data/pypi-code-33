import os
from os.path import join as jph

from nilabels.agents.agents_controller import AgentsController as LT
from nilabels.tools.aux_methods.label_descriptor_manager import LabelsDescriptorManager as LDM
from nilabels.tools.aux_methods.utils import print_and_run

# ---- PATH MANAGER ----

# Input
root = '/Users/sebastiano/Dropbox/RabbitEOP-MRI/study/A_MultiAtlas_W8/12503/segm'
pfi_input_segmentation = jph(root, 'automatic', '12503_segm_notyetfinal_HALF.nii.gz')
pfi_labels_descriptor  = '/Users/sebastiano/Dropbox/RabbitEOP-MRI/study/A_MultiAtlas_W8/labels_descriptor.txt'

assert os.path.exists(pfi_input_segmentation), pfi_input_segmentation
assert os.path.exists(pfi_labels_descriptor), pfi_labels_descriptor

# intermediate
pfi_input_segmentation_pre_processed = jph(root, 'automatic', '12503_pre_sym2.nii.gz')

# Output
log_file_before_cleaning          = jph(root, 'automatic', 'log_before_cleaning.txt')
pfi_output_cleaned_segmentation   = jph(root, 'automatic', '12503_segm_notyetfinal_HALF_cleaned.nii.gz')
log_file_after_cleaning           = jph(root, 'automatic', 'log_after_cleaning.txt')
pfi_differece_cleaned_non_cleaned = jph(root, 'automatic', 'difference_half_cleaned_uncleaned.nii.gz')


# ---- PRE-PROCESS ----

if True:
    cmd_ero  = 'seg_maths {} -ero 1 {}'.format(pfi_input_segmentation, pfi_input_segmentation_pre_processed)
    cmd_dil  = 'seg_maths {} -dil 1 {}'.format(pfi_input_segmentation_pre_processed, pfi_input_segmentation_pre_processed)
    cmd_smol = 'seg_maths {} -smol 1 {}'.format(pfi_input_segmentation_pre_processed, pfi_input_segmentation_pre_processed)

    print_and_run(cmd_ero)
    print_and_run(cmd_dil)
    print_and_run(cmd_smol)

else:
    cmd_cp  = 'cp {}  {}'.format(pfi_input_segmentation, pfi_input_segmentation_pre_processed)
    print_and_run(cmd_cp)

# ---- PROCESS ----

lt = LT()
ldm = LDM(pfi_labels_descriptor)

print '---------------------------'
print '---------------------------'
print 'Cleaning segmentation {}'.format(pfi_input_segmentation_pre_processed)
print '---------------------------\n\n'

# get the report before
lt.check.number_connected_components_per_label(pfi_input_segmentation_pre_processed,
                                               where_to_save_the_log_file=log_file_before_cleaning)

# get the labels_correspondences - do not clean the 0, get 2 components for the 201
labels = ldm.get_dict_itk_snap().keys()
correspondences_lab_comps  = []
for lab in labels:
    if lab == 201:
        correspondences_lab_comps.append([lab, 5])
    elif lab == 229:
        correspondences_lab_comps.append([lab, 2])
    elif lab == 230:
        correspondences_lab_comps.append([lab, 2])
    elif lab == 127:
        correspondences_lab_comps.append([lab, 2])
    elif lab == 203:
        correspondences_lab_comps.append([lab, 5])
    elif lab == 204:
        correspondences_lab_comps.append([lab, 5])
    elif lab == 0:
        pass
    else:
        correspondences_lab_comps.append([lab, 1])

print('Wanted final number of components per label:')
print(correspondences_lab_comps)

# get the cleaned segmentation
lt.manipulate_labels.clean_segmentation(pfi_input_segmentation_pre_processed, pfi_output_cleaned_segmentation,
                                        labels_to_clean=correspondences_lab_comps, force_overwriting=True)

# get the report of the connected components afterwards
lt.check.number_connected_components_per_label(pfi_output_cleaned_segmentation,
                                               where_to_save_the_log_file=log_file_after_cleaning)

# get the differences between the non-liceaned and the cleaned:

cmd = 'seg_maths {0} -sub {1} {2}'.format(pfi_input_segmentation, pfi_output_cleaned_segmentation,
                                          pfi_differece_cleaned_non_cleaned)
os.system(cmd)
cmd = 'seg_maths {0} -bin {0}'.format(pfi_differece_cleaned_non_cleaned)
os.system(cmd)
