import os
from os.path import join as jph

from nilabels.tools.aux_methods.label_descriptor_manager import LabelsDescriptorManager

pfi_descriptor = '/Users/sebastiano/Desktop/labels_descriptor.txt'
ldm = LabelsDescriptorManager(pfi_descriptor, labels_descriptor_convention='itk-snap')
print ldm.dict_label_descriptor

# mri_convert segm_only/1305_approved_round3_cleaned.nii.gz segm_only/converted.mgh
# freeview -v converted/converted_T1.mgh converted/segm_converted.mgh:colormap=lut:opacity=0.4 -f surf005.stl:edgecolor:blue

# from a segmentation export all the labels in stand-alone .stl files with ITK-snap.
suffix_surf = 'surf'
add_color = False
pfo_where_surfaces = '/Volumes/SmartWare/rabbit/E_for_images/1305'


pfi_t1 = jph(pfo_where_surfaces, 'mod/1305_T1.nii.gz')

cmd = 'source $FREESURFER_HOME/SetUpFreeSurfer.sh; freeview -v {0} -f '.format(pfi_t1)


labels_to_delineate = ldm.dict_label_descriptor.keys()[1:-1]

# labels_to_delineate = [7, 8, 31, 32, 69, 70, 83, 84, 109, 110, 218, 223, 224, 233]


for k in labels_to_delineate:

    pfi_surface = os.path.join(pfo_where_surfaces, '{0}{1:05d}.stl'.format(suffix_surf, k))
    assert os.path.exists(pfi_surface), pfi_surface
    if add_color:
        triplet_rgb = '{0},{1},{2}'.format(ldm.dict_label_descriptor[k][0][0],
                                           ldm.dict_label_descriptor[k][0][1],
                                           ldm.dict_label_descriptor[k][0][2])

        cmd += ' {0}:edgecolor={1}:color={1} '.format(pfi_surface, triplet_rgb)
    else:
        cmd += ' {0} '.format(pfi_surface)
os.system(cmd)

print cmd
# -

# -
