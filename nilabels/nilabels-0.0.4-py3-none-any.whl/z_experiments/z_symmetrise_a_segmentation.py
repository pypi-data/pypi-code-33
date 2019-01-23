
import os

from nilabels.agents.agents_controller import AgentsController as LT

# ---- PATH MANAGER ----

# input
pfi_input_anatomy      = '/Users/sebastiano/Dropbox/RabbitEOP-MRI/study/A_MultiAtlas_W8/12503/mod/12503_T1.nii.gz'
pfi_input_segmentation = '/Users/sebastiano/Dropbox/RabbitEOP-MRI/study/A_MultiAtlas_W8/12503/segm/automatic/12503_segm_notyetfinal_HALF.nii.gz'
pfo_output_folder      = '/Users/sebastiano/Dropbox/RabbitEOP-MRI/study/A_MultiAtlas_W8/12503/segm/automatic/z_tmp'

assert os.path.exists(pfi_input_anatomy), pfi_input_anatomy
assert os.path.exists(pfi_input_segmentation), pfi_input_segmentation
assert os.path.exists(pfo_output_folder), pfo_output_folder

# output
pfi_output_segmentation = '/Users/sebastiano/Dropbox/RabbitEOP-MRI/study/A_MultiAtlas_W8/12503/segm/automatic/12503_SYM2_from_HALF_CLEANED.nii.gz'

# ---- LABELS LIST ----


labels_central = [0, 77, 78,  121, 127, 151, 153, 161, 201, 215, 218, 233, 237, 253]

labels_left       = [5, 7, 9, 11,  13, 15, 17, 19, 25, 27, 31, 43, 45, 53, 55, 69, 71, 75, 83, 109, 129, 133, 135,
                     139, 141, 179, 203, 211, 219, 223, 225, 227, 229, 239, 241, 243, 247, 251]

labels_right = [a + 1 for a in labels_left]

labels_sym_left = labels_left + labels_central
labels_sym_right = labels_right + labels_central


# --- EXECUTE ----


lt = LT()
lt.symmetrize.symmetrise_with_registration(pfi_input_anatomy,
                                           pfi_input_segmentation,
                                           labels_sym_left,
                                           pfi_output_segmentation,
                                           results_folder_path=pfo_output_folder,
                                           list_labels_transformed=labels_sym_right,
                                           coord='z',
                                           reuse_registration=True)






















''' --- LABELS
]

5   128  128    3        1  1  1    "Medial Prefrontal Left"
7   171   25   35        1  1  1    "Frontal Left"
9   128  128    0        1  1  1    "Occipital Left"
11    64  128    0        1  1  1    "Parietal Left"
13     0  128  128        1  1  1    "Temporal Left"
15    79  255   79        1  1  1    "Cingulate Left"
17   156  222  255        1  1  1    "Retrosplenium Left"
19   102  102  255        1  1  1    "Insular Left"
25     0  128  128        1  1  1    "Olfactory lobe Left"
27   255  255  102        1  1  1    "Piriform Left"
31   244   80  244        1  1  1    "Hippocampus Left" 
43   128    0  255        1  1  1    "Subiculum Left"
45   205  133   63        1  1  1    "Entorhinal Left"
53   221   64   64        1  1  1    "Claustrum Left"
55     0  251  255        1  1  1    "Amygdala Left"
69    94   61  255        1  1  1    "Caudate nucleus Left"
71   220  174  255        1  1  1    "Putamen Left" 
75   148    0  211        1  1  1    "Globus pallidus Left"
83   255   29   74        1  1  1    "Thalamus Left"
109   186  253   78        1  1  1    "Hypothalamus Left"
129    25    0  255        1  1  1    "Pretectal Left"
133     0  206  209        1  1  1    "Superior colliculus Left"
135   239  138   44        1  1  1    "Inferior colliculus Left"
139    42   42  176        1  1  1    "Substantia nigra Left"
141   115  255  183        1  1  1    "Periaqueductal gray Left"
179    34  139   34        1  1  1    "Cerebellar hemisphere Left"
203   0    255  127        1  1  1    "Lateral Ventricle area Left"
211   222  184  135        1  1  1    "Periventricular area Left"
219   128  128    0        1  1  1    "External capsule Left"
223   139   69   19        1  1  1    "Internal capsule Left"
225   204  102  255        1  1  1    "Corona radiata Left"
227   255  102   51        1  1  1    "Cerebral peduncle Left"
229   102  102  255        1  1  1    "Subcortical white matter Left"
239     0  100    0        1  1  1    "Fimbria of hippocampus Left"
241   255  128    0        1  1  1    "Columns of the fornix Left"
243   135  206  235        1  1  1    "Stria terminalis Left"
247   204  153    0        1  1  1    "Mammilothalamic tract Left"
251   102  102   51        1  1  1    "Fasciculus retroflexus Left"


6   181  181    1        1  1  1    "Medial Prefrontal Right"
8   128    0    0        1  1  1    "Frontal Right"
10   128  128    0        1  1  1    "Occipital Right"
12    64  128    0        1  1  1    "Parietal Right"
14     0  128  128        1  1  1    "Temporal Right"
16     5  194    5        1  1  1    "Cingulate Right"
18    70  165  212        1  1  1    "Retrosplenium Right"
20   102  102  255        1  1  1    "Insular Right"
26     0  128  128        1  1  1    "Olfactory lobe Right"
28   255  255  102        1  1  1    "Piriform Right"
32   226   38  226        1  1  1    "Hippocampus Right"
44   128    0  255        1  1  1    "Subiculum Right"
46   210  180  140        1  1  1    "Entorhinal Right"
54   221   64   64        1  1  1    "Claustrum Right"
56     0  251  255        1  1  1    "Amygdala Right"
70    94   61  167        1  1  1    "Caudate nucleus Right"
72   220  174  255        1  1  1    "Putamen Right"
76   148    0  211        1  1  1    "Globus pallidus Right"
84   212   31   67        1  1  1    "Thalamus Right"
110   129  199   15        1  1  1    "Hypothalamus Right"
130    25    0  255        1  1  1    "Pretectal Right"
134   138  206  209        1  1  1    "Superior colliculus Right"
136   255  128    0        1  1  1    "Inferior colliculus Right"
140    56   56  153        1  1  1    "Substantia nigra Right"
142    22  226   97        1  1  1    "Periaqueductal gray Right"
180    34  139   34        1  1  1    "Cerebellar hemisphere Right"
204   0    255  127        1  1  1    "Lateral Ventricle area Right"
212   222  184  135        1  1  1    "Periventricular area Right"
220   128  128    0        1  1  1    "External capsule Right"
224   139   69    0        1  1  1    "Internal capsule Right"
226   204  102  255        1  1  1    "Corona radiata Right"
228   255  102   51        1  1  1    "Cerebral peduncle Right"
230   102  102  255        1  1  1    "Subcortical white matter Right"
240     0  100    0        1  1  1    "Fimbria of hippocampus Right"
242   255  128    0        1  1  1    "Columns of the fornix Right"
244   135  206  235        1  1  1    "Stria terminalis Right"
248   204  153    0        1  1  1    "Mammilothalamic tract Right"
252   102  102   51        1  1  1    "Fasciculus retroflexus Right"


0     0    0    0        0  0  0    "Clear Label"
77    65  105  225        1  1  1    "Basal forebrain"
78   244  164   96        1  1  1    "Septum"
121   255   99   71        1  1  1    "Mammillary body"
127   250  240  230        1  1  1    "Midbrain"
151   128    0    0        1  1  1    "Pons"
153    50  205   50        1  1  1    "Medulla oblongata"
161   173  255   47        1  1  1    "Cerebellar vermis"
201   168  230  197        1  1  1    "Ventricular system"
215   255  153    0        1  1  1    "Optic tract and optic chiasm"
218   128    0  128        1  1  1    "Corpus callosum"
233   255  255    0        1  1  1    "Anterior commissure"
237   255  250  205        1  1  1    "Hippocampal commissure"
253   255  243    7        1  1  1    "Posterior commissure"


'''