setup_bor = """
[LOCAL]
python_local_interpreter:
path_local_phaser:
path_local_shelxe:
path_local_phstat:
path_local_arcimboldo:
path_local_borges:

# OPTIONAL PARAMETERS
[CONDOR]
# Parameters for each executable under Condor (memory constraints, CPU speed ...)
requirements_shelxe:
requirements_phaser:
requirements_borges:

[SGE]
qname:
fraction: 1.00

[TORQUE]
qname:
cores_per_node:
number_of_parallel_jobs: 100

[MOAB]
partition:

[SLURM]
partition:

# Supercomputing environment parameters
[GRID]
# BORGES parameters for "borges" database generation
number_of_pdbs_per_tar: 5
#types are: SGE, Condor, MOAB, Torque, SLURM
type_remote:
type_local:

#EXAMPLE REMOTE
path_remote_phaser:
path_remote_shelxe:
path_remote_borgesclient:
python_remote_interpreter:
remote_frontend_username:
remote_frontend_host:
home_frontend_directory:
remote_frontend_port:
remote_fylesystem_isnfs:
remote_frontend_prompt:
remote_submitter_username:
remote_submitter_host:
remote_submitter_port:
remote_submitter_prompt:
"""

defaults_bor = """
[CONNECTION]:
distribute_computing: multiprocessing
remote_frontend_passkey: ~/.ssh/id_rsa
setup_bor_path:

[GENERAL]
mtz_p1_path:
ent_path:
pdb_path:

[ANOMALOUS]
hkl_fa_path: none
ins_fa_path: none
expphasing= none
nsites_expected= 0
ha_present_in_native = False
recycle_ha: True
sfac= none
dsul: 0
specialPos: False
rootAnom = none
dano_label = none
sigdano_label = none
nat_path: none
peak_path: none
infl_path: none
hrem_path: none
lrem_path: none
sir_path: none
sira_path: none
before_path: none
after_path: none
minusz: False
minusz_zero: True
minuso: False
evaluateAnom: True
patterson: True

# To provide a reference ha file on which to compare solutions from cross Fourier ha search
referenceHA: none

# deprecated, will be removed
hardFilter: False

# To have n cycles of ha refining (without autotracing) prior to expansion cycles
n_HA_refine_cycles: 0

# To start filtering solutions from Lite from fragment number n, based on anomalous signal
filterLiteFromFragNumber: 1

# To provide a heavy atom file already found before, for instance by shelxd (then origin shift and inversion will be tested by shelxe)
# If provided, the cross Fourier mode will not be activated for the first cycles and the provided ha will be used instead
ha_substructure= none

#Truncate anomalous data to this resolution
hres_cutoff: 0

[ARCIMBOLDO-BORGES]
# formfactors: FORMFACTORS ELECTRON
formfactors: FORMFACTORS XRAY
aniso: True
clusters: all
n_clusters: 4
prioritize_phasers: True
f_p1_label:
sigf_p1_label:
number_of_component: -1
number_of_component_p1:
rmsd: 0.2
rotation_clustering_algorithm: rot_matrices
threshold_algorithm: 15
resolution_rotation: 1.0
sampling_rotation: -1
resolution_translation: 1.0
sampling_translation: -1
resolution_refinement: 1.0
sampling_refinement: -1
resolution_gyre: 1.0
exclude_llg: 0
exclude_zscore: 0
spacegroup:
use_packing: True
number_cycles_model_refinement: 1
TNCS: True
pack_clashes: 0
nice: 0
randomize_trans_per_rot: 0
NMA: False
make_positive_llg: False
ROTATION_MODEL_REFINEMENT: NO_GYRE
step_rmsd_decrease_gyre: 0.2
SIGR: 0.0
SIGT: 0.0
PACK_TRA: False
BASE_SUM_FROM_WD: True
GYRE_PRESERVE_CHAINS: False
NMA_P1: False
OCC: False
VRMS: False
VRMS_GYRE: False
BFAC: False
BULK_FSOL: -1
BULK_BSOL: -1
GIMBLE: False
alixe_mode: one_step
prioritize_occ: True
solution_sorting_scheme: LLG
sampling_gyre: -1
applyTopNameFilter: True
noDMinitcc: True
phs_fom_statistics: False
savePHS: False
archivingAsBigFile: False
alixe: False
filter_clusters_after_rot: True
extend_with_random_atoms: False
extend_with_secondary_structure: False
parameters_elongation: 4.8 60 150
#parameters_elongation: 5 150 1
topFRF: 200
topFTF: 70
topPACK: -1
topRNP: 200
topExp: 60
force_core: -1
force_nsol: -1
force_exp : False
ellg_target: 30
fixed_model:
coiled_coil: False
stop_if_solved: True
unitCellContentAnalysis=False
solventContent: 0
# Force the number of autotracing cycles
nAutoTracCyc: -1
# number of autotracing cycles per bunch (default 1)
nBunchAutoTracCyc: 1

[ARCIMBOLDO-SHREDDER]
# formfactors: FORMFACTORS ELECTRON
formfactors: FORMFACTORS XRAY
aniso: True
clusters: all
n_clusters: 4
f_p1_label:
sigf_p1_label:
number_of_component_p1:
rotation_clustering_algorithm: rot_matrices
threshold_algorithm: 15
rmsd_shredder: 1.2
rmsd_arcimboldo: 0.8
resolution_rotation_shredder: 1.0
resolution_rotation_arcimboldo: 1.0
sampling_rotation_shredder: -1
sampling_rotation_arcimboldo: -1
resolution_translation: 1.0
sampling_translation: -1
resolution_refinement: 1.0
resolution_gyre: 1.0
sampling_refinement: -1
exclude_llg: 0
exclude_zscore: 0
spacegroup:
use_packing: True
solution_sorting_scheme: LLG
number_cycles_model_refinement: 2
fragment_to_search: 1
randomize_trans_per_rot: 0
TNCS: True
pack_clashes: 10
prioritize_phasers: True
NMA: False
ROTATION_MODEL_REFINEMENT: BOTH
step_rmsd_decrease_gyre: 0.2
NMA_P1: False
VRMS: True
VRMS_GYRE: False
BFAC: False
SIGR: 0.0
SIGT: 0.0
PACK_TRA: False
BASE_SUM_FROM_WD: True
GIMBLE: True
GYRE_PRESERVE_CHAINS: False
BULK_FSOL: -1
BULK_BSOL: -1
nice: 0
test_method: BRF
#test_method: GYRE
#test_method: RNP
test_sol:
test_txt:
init_location: EULER 0 0 0 FRAC 0 0 0
SHRED_LLG: False

SHRED_METHOD: spherical
# NOTE:  sphere definition parameters are: 
#csize/'default' step 'maintain_coil'/'remove_coil'/'partial_coil_n', where n is number of res 
# min_size_alpha min_size_beta min_diff_alpha min_diff_beta
sphere_definition: default 1 remove_coil 7 4 0.45 0.3
# NOTE: Depending on whether you do two steps or one, this line will be different
# Community clustering parameterization: algorithm bool_pack_beta bool_homogenity
community_clustering: fastgreedy True True

BFACNORM: True
alixe: True
alixe_mode: one_step
#alixe_mode: two_steps
#SHRED_METHOD: secondary_structure
cut_alpha_comb: 0
cut_beta_comb: 0
cut_ss_comb: 3
#SHRED_METHOD: sequential
SHRED_RANGE: 4 20 1 omit all
#SHRED_RANGE: 4 20 1 fragment all
mend_after_translation: False
parameters_borges_matrix: 50,40,2.5,1
reference_to_fix_location:
skip_OMIT: False
OCC: False
prioritize_occ: True
trim_to_polyala: True
maintainCys: False
sampling_gyre: -1
applyTopNameFilter: True
noDMinitcc: True
phs_fom_statistics: False
savePHS: False
archivingAsBigFile: False
filter_clusters_after_rot: True
extend_with_random_atoms: False
extend_with_secondary_structure: False
parameters_elongation: 4.8 60 150
#parameters_elongation: 5 150 1
search_inverted_helix: False
search_inverted_helix_from_fragment: -1
top_inverted_solution_per_cluster: 1000
topFRF: 200
topFTF: 70
topPACK: -1
topRNP: 200
topExp: 40
force_core: -1
force_nsol: -1
force_exp : False
ellg_target: 30
coiled_coil: False
swap_model_after_translation:
stop_if_solved: True
unitCellContentAnalysis=False
solventContent: 0
# Force the number of autotracing cycles
nAutoTracCyc: -1
# number of autotracing cycles per bunch (default 1)
nBunchAutoTracCyc: 1

[ARCIMBOLDO]
# formfactors: FORMFACTORS ELECTRON
formfactors: FORMFACTORS XRAY
aniso: True
rmsd: 0.2
spacegroup:
rotation_clustering_algorithm: rot_matrices
threshold_algorithm: 15
resolution_rotation: 1.0
sampling_rotation: -1
number_of_component: -1
resolution_translation: 1.0
sampling_translation: -1
resolution_refinement: 1.0
sampling_refinement: -1
exclude_llg: 0
exclude_zscore: 0.0
exclude_zscoreRNP: 0.0
#NS you can set up the cycle number from which exclude_zscoreRNP will be active:
cycleNExcludeZscoreRNP : 0
use_packing: True
pack_clashes: 0
fragment_to_search: 1
randomize_trans_per_rot: 0
solution_sorting_scheme: AUTO
TNCS: True
tNCSvector: 0_0_0
OCC: False
VRMS: False
VRMS_GYRE: False
UPDATE_RMSD: False
UPDATE_RMSD_FIXED: False
BFAC: False
SIGR: 0.0
SIGT: 0.0
PACK_TRA: False
BASE_SUM_FROM_WD: True
GYRE_PRESERVE_CHAINS: False
GIMBLE: False
BULK_FSOL: -1
BULK_BSOL: -1
usePDO: False
prioritize_occ: True
nice: 0
noDMinitcc: True
phs_fom_statistics: False
savePHS: False
archivingAsBigFile: False
post_mortem: False
fixed_models_directory:
range_rmsd_tra: 0.0
search_inverted_helix: False
search_inverted_helix_from_fragment: -1
top_inverted_solution_per_cluster: 1000
solution_verification: False
topFRF_1: 1000
topFTF_1: 200
topPACK_1: 10000
topRNP_1: 1000
topExp_1: 60
topFRF_n: 200
topFTF_n: 200
topPACK_n: 10000
topRNP_n: 150
topExp_n: 60
RNCS_MATL = []
force_exp = False
force_core = -1
ellg_target: 30
coiled_coil: False
stop_if_solved: True
phased_TF: 0
use_protocols: 0          
#NS if not zero, from fragment n, the TF will use (9 cycles density modified) phases generated from the fixed fragments n-1 
transformPDB: none  
#NS transform the input PDB files before any search, can be "polyA" (poly-alanine), "polyS" (poly-serine), "pseudoS" (polyA in which all C-betas are oxygen atoms) or "arom" (keeps only the side chains of PHE, TYR, HIS, TRP, and also LEU, ILE, VAL
#NS: now he solvent content will be derived from the number of molecules per asu if it is set to zero
solventContent: 0
ArcimboldoLOW: False
unitCellContentAnalysis=False
# Force the number of autotracing cycles
nAutoTracCyc: -1
# number of autotracing cycles per bunch (default 1)
nBunchAutoTracCyc: 1

[LOCAL]
path_local_phaser: phenix.phaser
path_local_shelxe: shelxe
path_local_arcimboldo: ARCIMBOLDO_BORGES
path_local_phstat: phstat
"""

script_r_galign = """
# Function that does all the work

galign2 <- function(x)
{

  library(Biostrings)
  data("BLOSUM62")

  a = pairwiseAlignment(pattern = c(x[,1]), subject = x[,3], type="global", gapOpening = -10, gapExtension = -0.5, substitutionMatrix = BLOSUM62, scoreOnly=TRUE)
  b = pairwiseAlignment(pattern = c(x[,2]), subject = x[,3], type="global", gapOpening = -10, gapExtension = -0.5, substitutionMatrix = BLOSUM62, scoreOnly=TRUE)
  uno = max(a)
  due = max(b)
  max(uno,due)
  }

galign2Factory <- function()

{

  list(name=galign2, #function that does the processing

       udxtype=c("scalar"), #type of the function

       intype=c("varchar","varchar"), #input types

       outtype=c("float") #output types

  )

}

"""
Fe2S2 = """
HETATM    1  S1  FES A   1       1.488   0.071   0.000  1.00 20.00           S
HETATM    2 FE2  FES A   1      -0.044  -0.289   1.531  1.00 20.00          FE
HETATM    3  S2  FES A   1      -1.401   0.508   0.000  1.00 20.00           S
HETATM    4 FE1  FES A   1      -0.044  -0.289  -1.531  1.00 20.00          FE
END
"""

Fe2S4 = """
HETATM    2  S4  SF4 A   1      51.686  27.350  -4.506  1.00 20.00           S
HETATM    3 FE1  SF4 A   1      51.050  29.410  -4.116  1.00 20.00          FE
HETATM    4 FE3  SF4 A   1      49.927  27.048  -5.778  1.00 20.00          FE
HETATM    5 FE2  SF4 A   1      50.543  26.668  -2.765  1.00 20.00          FE
HETATM    6  S3  SF4 A   1      49.908  28.727  -2.375  1.00 20.00           S
HETATM    8 FE4  SF4 A   1      48.150  28.425  -3.648  1.00 20.00          FE
HETATM    9  S2  SF4 A   1      49.293  29.108  -5.387  1.00 20.00           S
HETATM   11  S1  SF4 A   1      48.786  26.366  -4.037  1.00 20.00           S
END
"""

heme = """
HETATM    1  O2D HEB A   1      29.688  41.928  32.056  1.00 20.00           O
HETATM    2  CGD HEB A   1      29.759  41.890  30.808  1.00 20.00           C
HETATM    3  O1D HEB A   1      30.064  42.849  30.065  1.00 20.00           O
HETATM    4  CBD HEB A   1      29.330  40.592  30.139  1.00 20.00           C
HETATM    5 HBD1 HEB A   1      28.261  40.463  30.316  1.00 20.00           H
HETATM    6 HBD2 HEB A   1      29.878  39.775  30.614  1.00 20.00           H
HETATM    7  CAD HEB A   1      29.603  40.582  28.637  1.00 20.00           C
HETATM    8 HAD1 HEB A   1      30.680  40.470  28.496  1.00 20.00           H
HETATM    9 HAD2 HEB A   1      29.284  41.547  28.236  1.00 20.00           H
HETATM   10  C3D HEB A   1      28.878  39.468  27.913  1.00 20.00           C
HETATM   11  C2D HEB A   1      27.596  39.509  27.415  1.00 20.00           C
HETATM   12  CMD HEB A   1      26.654  40.676  27.534  1.00 20.00           C
HETATM   13 HMD3 HEB A   1      25.655  40.328  27.487  1.00 20.00           H
HETATM   14 HMD2 HEB A   1      26.814  41.165  28.460  1.00 20.00           H
HETATM   15 HMD1 HEB A   1      26.831  41.354  26.741  1.00 20.00           H
HETATM   16  C1D HEB A   1      27.346  38.251  26.745  1.00 20.00           C
HETATM   17  CHD HEB A   1      26.170  37.928  26.057  1.00 20.00           C
HETATM   18  HHD HEB A   1      25.390  38.668  25.980  1.00 20.00           H
HETATM   19  C4D HEB A   1      29.423  38.180  27.582  1.00 20.00           C
HETATM   20  CHA HEB A   1      30.719  37.800  27.894  1.00 20.00           C
HETATM   21  HHA HEB A   1      31.357  38.530  28.364  1.00 20.00           H
HETATM   22  ND  HEB A   1      28.472  37.481  26.911  1.00 20.00           N
HETATM   23 FE   HEB A   1      28.753  35.505  26.248  1.00 20.00          FE
HETATM   24  NB  HEB A   1      28.995  33.615  25.615  1.00 20.00           N
HETATM   25  C4B HEB A   1      30.203  33.069  25.372  1.00 20.00           C
HETATM   26  C3B HEB A   1      30.002  31.735  24.892  1.00 20.00           C
HETATM   27  CAB HEB A   1      31.121  30.760  24.636  1.00 20.00           C
HETATM   28  HAB HEB A   1      30.836  29.815  25.103  1.00 20.00           H
HETATM   29 HAB2 HEB A   1      32.012  31.155  25.129  1.00 20.00           H
HETATM   30  CBB HEB A   1      31.415  30.533  23.167  1.00 20.00           C
HETATM   31 HBB3 HEB A   1      30.537  30.197  22.680  1.00 20.00           H
HETATM   32 HBB2 HEB A   1      31.739  31.440  22.727  1.00 20.00           H
HETATM   33 HBB1 HEB A   1      32.175  29.802  23.068  1.00 20.00           H
HETATM   34  C2B HEB A   1      28.642  31.548  24.770  1.00 20.00           C
HETATM   35  CMB HEB A   1      27.926  30.355  24.194  1.00 20.00           C
HETATM   36 HMB3 HEB A   1      27.455  29.816  24.974  1.00 20.00           H
HETATM   37 HMB2 HEB A   1      27.196  30.683  23.500  1.00 20.00           H
HETATM   38 HMB1 HEB A   1      28.624  29.728  23.703  1.00 20.00           H
HETATM   39  C1B HEB A   1      28.004  32.749  25.249  1.00 20.00           C
HETATM   40  CHB HEB A   1      26.622  32.950  25.288  1.00 20.00           C
HETATM   41  HHB HEB A   1      25.561  32.879  25.117  1.00 20.00           H
HETATM   42  NC  HEB A   1      26.837  35.608  25.473  1.00 20.00           N
HETATM   43  C4C HEB A   1      25.978  36.679  25.470  1.00 20.00           C
HETATM   44  C3C HEB A   1      24.814  36.265  24.719  1.00 20.00           C
HETATM   45  CAC HEB A   1      23.634  37.140  24.361  1.00 20.00           C
HETATM   46  HAC HEB A   1      23.751  37.935  23.644  1.00 20.00           H
HETATM   47  CBC HEB A   1      22.435  36.926  24.940  1.00 20.00           C
HETATM   48 HBC2 HEB A   1      21.739  37.744  25.083  1.00 20.00           H
HETATM   49 HBC1 HEB A   1      22.152  35.934  25.270  1.00 20.00           H
HETATM   50  C2C HEB A   1      24.987  34.965  24.315  1.00 20.00           C
HETATM   51  CMC HEB A   1      24.071  34.056  23.541  1.00 20.00           C
HETATM   52 HMC3 HEB A   1      23.114  34.504  23.463  1.00 20.00           H
HETATM   53 HMC2 HEB A   1      24.467  33.899  22.572  1.00 20.00           H
HETATM   54 HMC1 HEB A   1      23.987  33.128  24.043  1.00 20.00           H
HETATM   55  C1C HEB A   1      26.275  34.577  24.804  1.00 20.00           C
HETATM   56  CHC HEB A   1      26.782  33.331  24.579  1.00 20.00           C
HETATM   57  HHC HEB A   1      26.197  32.511  24.197  1.00 20.00           H
HETATM   58  NA  HEB A   1      30.655  35.480  27.058  1.00 20.00           N
HETATM   59  C4A HEB A   1      31.485  34.398  27.083  1.00 20.00           C
HETATM   60  C3A HEB A   1      32.709  34.809  27.731  1.00 20.00           C
HETATM   61  CMA HEB A   1      33.867  33.904  28.080  1.00 20.00           C
HETATM   62 HMA3 HEB A   1      33.497  32.990  28.464  1.00 20.00           H
HETATM   63 HMA2 HEB A   1      34.442  33.714  27.211  1.00 20.00           H
HETATM   64 HMA1 HEB A   1      34.475  34.373  28.810  1.00 20.00           H
HETATM   65  C2A HEB A   1      32.579  36.151  28.027  1.00 20.00           C
HETATM   66  C1A HEB A   1      31.250  36.545  27.641  1.00 20.00           C
HETATM   67  CAA HEB A   1      33.619  37.094  28.585  1.00 20.00           C
HETATM   68 HAA1 HEB A   1      33.813  37.829  27.801  1.00 20.00           H
HETATM   69 HAA2 HEB A   1      34.517  36.495  28.749  1.00 20.00           H
HETATM   70  CBA HEB A   1      33.238  37.819  29.889  1.00 20.00           C
HETATM   71 HBA1 HEB A   1      33.894  37.468  30.687  1.00 20.00           H
HETATM   72 HBA2 HEB A   1      32.203  37.572  30.134  1.00 20.00           H
HETATM   73  CGA HEB A   1      33.380  39.329  29.739  1.00 20.00           C
HETATM   74  O1A HEB A   1      34.374  39.756  29.112  1.00 20.00           O
HETATM   75  O2A HEB A   1      32.457  40.026  30.217  1.00 20.00           O
END
"""

th70pdb = """
ATOM      3  N   ALA A   1  1   -0.335   2.307   0.000  1.00  1.00   7
ATOM      4  CA  ALA A   1  1   -0.048   3.749   0.000  1.00  1.00   6
ATOM      5  C   ALA A   1  1    0.806   4.112   1.217  1.00  1.00   6
ATOM      6  O   ALA A   1  1    1.811   4.829   1.100  1.00  1.00   8
ATOM      7  CB  ALA A   1  1   -1.329   4.527   0.054  1.00  1.00   6
ATOM     10  N   ALA A   2  1    0.370   3.598   2.351  1.00  1.00   7
ATOM     11  CA  ALA A   2  1    1.039   3.821   3.641  1.00  1.00   6
ATOM     12  C   ALA A   2  1    2.491   3.342   3.566  1.00  1.00   6
ATOM     13  O   ALA A   2  1    3.418   4.049   3.988  1.00  1.00   8
ATOM     14  CB  ALA A   2  1    0.331   3.062   4.724  1.00  1.00   6
ATOM     17  N   ALA A   3  1    2.634   2.146   3.027  1.00  1.00   7
ATOM     18  CA  ALA A   3  1    3.942   1.496   2.858  1.00  1.00   6
ATOM     19  C   ALA A   3  1    4.862   2.382   2.015  1.00  1.00   6
ATOM     20  O   ALA A   3  1    6.030   2.606   2.366  1.00  1.00   8
ATOM     21  CB  ALA A   3  1    3.773   0.175   2.168  1.00  1.00   6
ATOM     24  N   ALA A   4  1    4.295   2.858   0.922  1.00  1.00   7
ATOM     25  CA  ALA A   4  1    4.999   3.730  -0.029  1.00  1.00   6
ATOM     26  C   ALA A   4  1    5.506   4.984   0.686  1.00  1.00   6
ATOM     27  O   ALA A   4  1    6.667   5.386   0.524  1.00  1.00   8
ATOM     28  CB  ALA A   4  1    4.069   4.141  -1.132  1.00  1.00   6
ATOM     31  N   ALA A   5  1    4.606   5.561   1.460  1.00  1.00   7
ATOM     32  CA  ALA A   5  1    4.881   6.777   2.238  1.00  1.00   6
ATOM     33  C   ALA A   5  1    6.063   6.539   3.181  1.00  1.00   6
ATOM     34  O   ALA A   5  1    6.987   7.362   3.267  1.00  1.00   8
ATOM     35  CB  ALA A   5  1    3.677   7.149   3.052  1.00  1.00   6
ATOM     38  N   ALA A   6  1    5.989   5.409   3.859  1.00  1.00   7
ATOM     39  CA  ALA A   6  1    7.017   4.983   4.820  1.00  1.00   6
ATOM     40  C   ALA A   6  1    8.378   4.895   4.125  1.00  1.00   6
ATOM     41  O   ALA A   6  1    9.391   5.393   4.639  1.00  1.00   8
ATOM     42  CB  ALA A   6  1    6.669   3.637   5.381  1.00  1.00   6
ATOM     45  N   ALA A   7  1    8.350   4.257   2.970  1.00  1.00   7
ATOM     46  CA  ALA A   7  1    9.545   4.058   2.137  1.00  1.00   6
ATOM     47  C   ALA A   7  1   10.169   5.410   1.784  1.00  1.00   6
ATOM     48  O   ALA A   7  1   11.389   5.600   1.900  1.00  1.00   8
ATOM     49  CB  ALA A   7  1    9.174   3.347   0.869  1.00  1.00   6
ATOM     52  N   ALA A   8  1    9.299   6.308   1.361  1.00  1.00   7
ATOM     53  CA  ALA A   8  1    9.683   7.672   0.969  1.00  1.00   6
ATOM     54  C   ALA A   8  1   10.384   8.373   2.135  1.00  1.00   6
ATOM     55  O   ALA A   8  1   11.443   8.995   1.962  1.00  1.00   8
ATOM     56  CB  ALA A   8  1    8.464   8.459   0.589  1.00  1.00   6
ATOM     59  N   ALA A   9  1    9.761   8.246   3.291  1.00  1.00   7
ATOM     60  CA  ALA A   9  1   10.260   8.840   4.539  1.00  1.00   6
ATOM     61  C   ALA A   9  1   11.671   8.328   4.836  1.00  1.00   6
ATOM     62  O   ALA A   9  1   12.578   9.107   5.161  1.00  1.00   8
ATOM     63  CB  ALA A   9  1    9.358   8.471   5.680  1.00  1.00   6
ATOM     66  N   ALA A  10  1   11.804   7.020   4.711  1.00  1.00   7
ATOM     67  CA  ALA A  10  1   13.074   6.319   4.948  1.00  1.00   6
ATOM     68  C   ALA A  10  1   14.161   6.878   4.028  1.00  1.00   6
ATOM     69  O   ALA A  10  1   15.282   7.172   4.469  1.00  1.00   8
ATOM     70  CB  ALA A  10  1   12.910   4.854   4.673  1.00  1.00   6
ATOM     73  N   ALA A  11  1   13.785   7.007   2.770  1.00  1.00   7
ATOM     74  CA  ALA A  11  1   14.672   7.525   1.718  1.00  1.00   6
ATOM     75  C   ALA A  11  1   15.161   8.926   2.090  1.00  1.00   6
ATOM     76  O   ALA A  11  1   16.359   9.230   1.993  1.00  1.00   8
ATOM     77  CB  ALA A  11  1   13.934   7.597   0.414  1.00  1.00   6
ATOM     80  N   ALA A  12  1   14.206   9.736   2.506  1.00  1.00   7
ATOM     81  CA  ALA A  12  1   14.455  11.126   2.913  1.00  1.00   6
ATOM     82  C   ALA A  12  1   15.476  11.162   4.052  1.00  1.00   6
ATOM     83  O   ALA A  12  1   16.434  11.949   4.026  1.00  1.00   8
ATOM     84  CB  ALA A  12  1   13.179  11.760   3.382  1.00  1.00   6
ATOM     87  N   ALA A  13  1   15.231  10.300   5.021  1.00  1.00   7
ATOM     88  CA  ALA A  13  1   16.085  10.168   6.210  1.00  1.00   6
ATOM     89  C   ALA A  13  1   17.518   9.837   5.791  1.00  1.00   6
ATOM     90  O   ALA A  13  1   18.483  10.445   6.278  1.00  1.00   8
ATOM     91  CB  ALA A  13  1   15.569   9.069   7.092  1.00  1.00   6
ATOM     94  N   ALA A  14  1   17.606   8.873   4.892  1.00  1.00   7
ATOM     95  CA  ALA A  14  1   18.888   8.398   4.351  1.00  1.00   6
ATOM     96  C   ALA A  14  1   19.646   9.559   3.706  1.00  1.00   6
ATOM     97  O   ALA A  14  1   20.849   9.747   3.944  1.00  1.00   8
ATOM     98  CB  ALA A  14  1   18.646   7.339   3.317  1.00  1.00   6
ATOM    101  N   ALA A  15  1   18.908  10.303   2.904  1.00  1.00   7
ATOM    102  CA  ALA A  15  1   19.437  11.469   2.182  1.00  1.00   6
ATOM    103  C   ALA A  15  1   20.017  12.480   3.173  1.00  1.00   6
ATOM    104  O   ALA A  15  1   21.130  12.992   2.984  1.00  1.00   8
ATOM    105  CB  ALA A  15  1   18.340  12.129   1.400  1.00  1.00   6
ATOM    108  N   ALA A  16  1   19.233  12.731   4.204  1.00  1.00   7
ATOM    109  CA  ALA A  16  1   19.595  13.671   5.276  1.00  1.00   6
ATOM    110  C   ALA A  16  1   20.912  13.241   5.925  1.00  1.00   6
ATOM    111  O   ALA A  16  1   21.819  14.061   6.133  1.00  1.00   8
ATOM    112  CB  ALA A  16  1   18.521  13.694   6.323  1.00  1.00   6
ATOM    115  N   ALA A  17  1   20.970  11.957   6.223  1.00  1.00   7
ATOM    116  CA  ALA A  17  1   22.143  11.333   6.852  1.00  1.00   6
ATOM    117  C   ALA A  17  1   23.383  11.554   5.983  1.00  1.00   6
ATOM    118  O   ALA A  17  1   24.450  11.943   6.481  1.00  1.00   8
ATOM    119  CB  ALA A  17  1   21.917   9.859   7.011  1.00  1.00   6
ATOM    122  N   ALA A  18  1   23.194  11.296   4.703  1.00  1.00   7
ATOM    123  CA  ALA A  18  1   24.252  11.442   3.692  1.00  1.00   6
ATOM    124  C   ALA A  18  1   24.782  12.878   3.693  1.00  1.00   6
ATOM    125  O   ALA A  18  1   26.000  13.109   3.693  1.00  1.00   8
ATOM    126  CB  ALA A  18  1   23.708  11.125   2.331  1.00  1.00   6
ATOM    129  N   ALA A  19  1   23.836  13.799   3.694  1.00  1.00   7
ATOM    130  CA  ALA A  19  1   24.124  15.241   3.695  1.00  1.00   6
ATOM    131  C   ALA A  19  1   24.978  15.603   4.912  1.00  1.00   6
ATOM    132  O   ALA A  19  1   25.982  16.320   4.796  1.00  1.00   8
ATOM    133  CB  ALA A  19  1   22.842  16.019   3.750  1.00  1.00   6
ATOM    136  N   ALA A  20  1   24.542  15.089   6.046  1.00  1.00   7
ATOM    137  CA  ALA A  20  1   25.212  15.310   7.336  1.00  1.00   6
ATOM    138  C   ALA A  20  1   26.663  14.832   7.260  1.00  1.00   6
ATOM    139  O   ALA A  20  1   27.591  15.538   7.682  1.00  1.00   8
ATOM    140  CB  ALA A  20  1   24.505  14.551   8.419  1.00  1.00   6
ATOM    143  N   ALA A  21  1   26.807  13.636   6.720  1.00  1.00   7
ATOM    144  CA  ALA A  21  1   28.114  12.986   6.550  1.00  1.00   6
ATOM    145  C   ALA A  21  1   29.034  13.873   5.708  1.00  1.00   6
ATOM    146  O   ALA A  21  1   30.202  14.096   6.058  1.00  1.00   8
ATOM    147  CB  ALA A  21  1   27.945  11.666   5.859  1.00  1.00   6
ATOM    150  N   ALA A  22  1   28.467  14.350   4.615  1.00  1.00   7
ATOM    151  CA  ALA A  22  1   29.170  15.222   3.664  1.00  1.00   6
ATOM    152  C   ALA A  22  1   29.677  16.476   4.380  1.00  1.00   6
ATOM    153  O   ALA A  22  1   30.839  16.878   4.218  1.00  1.00   8
ATOM    154  CB  ALA A  22  1   28.240  15.634   2.562  1.00  1.00   6
ATOM    157  N   ALA A  23  1   28.777  17.053   5.155  1.00  1.00   7
ATOM    158  CA  ALA A  23  1   29.053  18.268   5.934  1.00  1.00   6
ATOM    159  C   ALA A  23  1   30.235  18.029   6.876  1.00  1.00   6
ATOM    160  O   ALA A  23  1   31.159  18.852   6.963  1.00  1.00   8
ATOM    161  CB  ALA A  23  1   27.849  18.639   6.748  1.00  1.00   6
ATOM    164  N   ALA A  24  1   30.162  16.899   7.553  1.00  1.00   7
ATOM    165  CA  ALA A  24  1   31.190  16.472   8.513  1.00  1.00   6
ATOM    166  C   ALA A  24  1   32.550  16.385   7.818  1.00  1.00   6
ATOM    167  O   ALA A  24  1   33.563  16.883   8.332  1.00  1.00   8
ATOM    168  CB  ALA A  24  1   30.842  15.125   9.073  1.00  1.00   6
ATOM    171  N   ALA A  25  1   32.523  15.748   6.662  1.00  1.00   7
ATOM    172  CA  ALA A  25  1   33.717  15.549   5.829  1.00  1.00   6
ATOM    173  C   ALA A  25  1   34.341  16.901   5.477  1.00  1.00   6
ATOM    174  O   ALA A  25  1   35.560  17.092   5.593  1.00  1.00   8
ATOM    175  CB  ALA A  25  1   33.346  14.839   4.561  1.00  1.00   6
ATOM    178  N   ALA A  26  1   33.471  17.800   5.055  1.00  1.00   7
ATOM    179  CA  ALA A  26  1   33.854  19.164   4.664  1.00  1.00   6
ATOM    180  C   ALA A  26  1   34.556  19.865   5.829  1.00  1.00   6
ATOM    181  O   ALA A  26  1   35.614  20.487   5.657  1.00  1.00   8
ATOM    182  CB  ALA A  26  1   32.635  19.951   4.285  1.00  1.00   6
ATOM    185  N   ALA A  27  1   33.933  19.737   6.986  1.00  1.00   7
ATOM    186  CA  ALA A  27  1   34.432  20.330   8.235  1.00  1.00   6
ATOM    187  C   ALA A  27  1   35.843  19.817   8.530  1.00  1.00   6
ATOM    188  O   ALA A  27  1   36.751  20.597   8.855  1.00  1.00   8
ATOM    189  CB  ALA A  27  1   33.531  19.960   9.375  1.00  1.00   6
ATOM    192  N   ALA A  28  1   35.977  18.510   8.404  1.00  1.00   7
ATOM    193  CA  ALA A  28  1   37.247  17.809   8.641  1.00  1.00   6
ATOM    194  C   ALA A  28  1   38.333  18.369   7.721  1.00  1.00   6
ATOM    195  O   ALA A  28  1   39.454  18.662   8.162  1.00  1.00   8
ATOM    196  CB  ALA A  28  1   37.082  16.343   8.364  1.00  1.00   6
ATOM    199  N   ALA A  29  1   37.957  18.498   6.462  1.00  1.00   7
ATOM    200  CA  ALA A  29  1   38.843  19.017   5.411  1.00  1.00   6
ATOM    201  C   ALA A  29  1   39.333  20.418   5.783  1.00  1.00   6
ATOM    202  O   ALA A  29  1   40.531  20.723   5.686  1.00  1.00   8
ATOM    203  CB  ALA A  29  1   38.105  19.090   4.107  1.00  1.00   6
ATOM    206  N   ALA A  30  1   38.377  21.227   6.200  1.00  1.00   7
ATOM    207  CA  ALA A  30  1   38.627  22.617   6.608  1.00  1.00   6
ATOM    208  C   ALA A  30  1   39.648  22.653   7.747  1.00  1.00   6
ATOM    209  O   ALA A  30  1   40.606  23.440   7.721  1.00  1.00   8
ATOM    210  CB  ALA A  30  1   37.351  23.251   7.079  1.00  1.00   6
ATOM    213  N   ALA A  31  1   39.403  21.790   8.715  1.00  1.00   7
ATOM    214  CA  ALA A  31  1   40.257  21.657   9.904  1.00  1.00   6
ATOM    215  C   ALA A  31  1   41.691  21.326   9.484  1.00  1.00   6
ATOM    216  O   ALA A  31  1   42.655  21.934   9.972  1.00  1.00   8
ATOM    217  CB  ALA A  31  1   39.742  20.557  10.785  1.00  1.00   6
ATOM    220  N   ALA A  32  1   41.779  20.364   8.585  1.00  1.00   7
ATOM    221  CA  ALA A  32  1   43.060  19.889   8.043  1.00  1.00   6
ATOM    222  C   ALA A  32  1   43.818  21.050   7.398  1.00  1.00   6
ATOM    223  O   ALA A  32  1   45.021  21.238   7.636  1.00  1.00   8
ATOM    224  CB  ALA A  32  1   42.818  18.831   7.008  1.00  1.00   6
ATOM    227  N   ALA A  33  1   43.080  21.795   6.597  1.00  1.00   7
ATOM    228  CA  ALA A  33  1   43.608  22.962   5.876  1.00  1.00   6
ATOM    229  C   ALA A  33  1   44.189  23.972   6.868  1.00  1.00   6
ATOM    230  O   ALA A  33  1   45.302  24.484   6.679  1.00  1.00   8
ATOM    231  CB  ALA A  33  1   42.510  23.622   5.095  1.00  1.00   6
ATOM    234  N   ALA A  34  1   43.405  24.222   7.899  1.00  1.00   7
ATOM    235  CA  ALA A  34  1   43.767  25.161   8.971  1.00  1.00   6
ATOM    236  C   ALA A  34  1   45.085  24.731   9.619  1.00  1.00   6
ATOM    237  O   ALA A  34  1   45.991  25.551   9.828  1.00  1.00   8
ATOM    238  CB  ALA A  34  1   42.694  25.183  10.019  1.00  1.00   6
ATOM    241  N   ALA A  35  1   45.143  23.446   9.917  1.00  1.00   7
ATOM    242  CA  ALA A  35  1   46.316  22.822  10.545  1.00  1.00   6
ATOM    243  C   ALA A  35  1   47.556  23.045   9.676  1.00  1.00   6
ATOM    244  O   ALA A  35  1   48.623  23.433  10.173  1.00  1.00   8
ATOM    245  CB  ALA A  35  1   46.090  21.348  10.703  1.00  1.00   6
ATOM    248  N   ALA A  36  1   47.366  22.787   8.395  1.00  1.00   7
ATOM    249  CA  ALA A  36  1   48.424  22.934   7.384  1.00  1.00   6
ATOM    250  C   ALA A  36  1   48.953  24.370   7.386  1.00  1.00   6
ATOM    251  O   ALA A  36  1   50.172  24.601   7.386  1.00  1.00   8
ATOM    252  CB  ALA A  36  1   47.879  22.618   6.023  1.00  1.00   6
ATOM    255  N   ALA A  37  1   48.008  25.291   7.388  1.00  1.00   7
ATOM    256  CA  ALA A  37  1   48.295  26.732   7.390  1.00  1.00   6
ATOM    257  C   ALA A  37  1   49.149  27.094   8.607  1.00  1.00   6
ATOM    258  O   ALA A  37  1   50.154  27.812   8.491  1.00  1.00   8
ATOM    259  CB  ALA A  37  1   47.014  27.510   7.446  1.00  1.00   6
ATOM    262  N   ALA A  38  1   48.714  26.579   9.741  1.00  1.00   7
ATOM    263  CA  ALA A  38  1   49.384  26.800  11.031  1.00  1.00   6
ATOM    264  C   ALA A  38  1   50.836  26.321  10.954  1.00  1.00   6
ATOM    265  O   ALA A  38  1   51.764  27.027  11.376  1.00  1.00   8
ATOM    266  CB  ALA A  38  1   48.678  26.039  12.113  1.00  1.00   6
ATOM    269  N   ALA A  39  1   50.979  25.126  10.412  1.00  1.00   7
ATOM    270  CA  ALA A  39  1   52.287  24.476  10.242  1.00  1.00   6
ATOM    271  C   ALA A  39  1   53.206  25.364   9.400  1.00  1.00   6
ATOM    272  O   ALA A  39  1   54.374  25.587   9.750  1.00  1.00   8
ATOM    273  CB  ALA A  39  1   52.117  23.156   9.550  1.00  1.00   6
ATOM    276  N   ALA A  40  1   52.639  25.841   8.308  1.00  1.00   7
ATOM    277  CA  ALA A  40  1   53.341  26.715   7.357  1.00  1.00   6
ATOM    278  C   ALA A  40  1   53.849  27.968   8.074  1.00  1.00   6
ATOM    279  O   ALA A  40  1   55.010  28.370   7.912  1.00  1.00   8
ATOM    280  CB  ALA A  40  1   52.411  27.127   6.256  1.00  1.00   6
ATOM    283  N   ALA A  41  1   52.949  28.544   8.850  1.00  1.00   7
ATOM    284  CA  ALA A  41  1   53.225  29.759   9.630  1.00  1.00   6
ATOM    285  C   ALA A  41  1   54.407  29.519  10.571  1.00  1.00   6
ATOM    286  O   ALA A  41  1   55.331  30.342  10.658  1.00  1.00   8
ATOM    287  CB  ALA A  41  1   52.021  30.129  10.445  1.00  1.00   6
ATOM    290  N   ALA A  42  1   54.334  28.388  11.248  1.00  1.00   7
ATOM    291  CA  ALA A  42  1   55.363  27.962  12.207  1.00  1.00   6
ATOM    292  C   ALA A  42  1   56.723  27.875  11.511  1.00  1.00   6
ATOM    293  O   ALA A  42  1   57.736  28.372  12.024  1.00  1.00   8
ATOM    294  CB  ALA A  42  1   55.016  26.614  12.766  1.00  1.00   6
ATOM    297  N   ALA A  43  1   56.695  27.238  10.355  1.00  1.00   7
ATOM    298  CA  ALA A  43  1   57.889  27.040   9.521  1.00  1.00   6
ATOM    299  C   ALA A  43  1   58.512  28.393   9.169  1.00  1.00   6
ATOM    300  O   ALA A  43  1   59.732  28.584   9.285  1.00  1.00   8
ATOM    301  CB  ALA A  43  1   57.517  26.332   8.252  1.00  1.00   6
ATOM    304  N   ALA A  44  1   57.642  29.292   8.749  1.00  1.00   7
ATOM    305  CA  ALA A  44  1   58.026  30.656   8.358  1.00  1.00   6
ATOM    306  C   ALA A  44  1   58.727  31.356   9.524  1.00  1.00   6
ATOM    307  O   ALA A  44  1   59.786  31.978   9.352  1.00  1.00   8
ATOM    308  CB  ALA A  44  1   56.806  31.444   7.981  1.00  1.00   6
ATOM    311  N   ALA A  45  1   58.105  31.227  10.681  1.00  1.00   7
ATOM    312  CA  ALA A  45  1   58.605  31.820  11.930  1.00  1.00   6
ATOM    313  C   ALA A  45  1   60.016  31.307  12.224  1.00  1.00   6
ATOM    314  O   ALA A  45  1   60.923  32.086  12.550  1.00  1.00   8
ATOM    315  CB  ALA A  45  1   57.704  31.449  13.070  1.00  1.00   6
ATOM    318  N   ALA A  46  1   60.149  30.000  12.098  1.00  1.00   7
ATOM    319  CA  ALA A  46  1   61.419  29.298  12.333  1.00  1.00   6
ATOM    320  C   ALA A  46  1   62.505  29.859  11.413  1.00  1.00   6
ATOM    321  O   ALA A  46  1   63.627  30.153  11.854  1.00  1.00   8
ATOM    322  CB  ALA A  46  1   61.255  27.833  12.056  1.00  1.00   6
ATOM    325  N   ALA A  47  1   62.129  29.989  10.155  1.00  1.00   7
ATOM    326  CA  ALA A  47  1   63.015  30.509   9.103  1.00  1.00   6
ATOM    327  C   ALA A  47  1   63.504  31.910   9.477  1.00  1.00   6
ATOM    328  O   ALA A  47  1   64.702  32.215   9.379  1.00  1.00   8
ATOM    329  CB  ALA A  47  1   62.276  30.583   7.800  1.00  1.00   6
ATOM    332  N   ALA A  48  1   62.549  32.719   9.895  1.00  1.00   7
ATOM    333  CA  ALA A  48  1   62.798  34.109  10.304  1.00  1.00   6
ATOM    334  C   ALA A  48  1   63.820  34.144  11.442  1.00  1.00   6
ATOM    335  O   ALA A  48  1   64.778  34.931  11.417  1.00  1.00   8
ATOM    336  CB  ALA A  48  1   61.522  34.742  10.775  1.00  1.00   6
ATOM    339  N   ALA A  49  1   63.576  33.280  12.410  1.00  1.00   7
ATOM    340  CA  ALA A  49  1   64.430  33.146  13.598  1.00  1.00   6
ATOM    341  C   ALA A  49  1   65.864  32.816  13.177  1.00  1.00   6
ATOM    342  O   ALA A  49  1   66.828  33.424  13.665  1.00  1.00   8
ATOM    343  CB  ALA A  49  1   63.916  32.046  14.479  1.00  1.00   6
ATOM    346  N   ALA A  50  1   65.951  31.854  12.278  1.00  1.00   7
ATOM    347  CA  ALA A  50  1   67.232  31.379  11.735  1.00  1.00   6
ATOM    348  C   ALA A  50  1   67.990  32.542  11.091  1.00  1.00   6
ATOM    349  O   ALA A  50  1   69.193  32.730  11.328  1.00  1.00   8
ATOM    350  CB  ALA A  50  1   66.990  30.322  10.699  1.00  1.00   6
ATOM    353  N   ALA A  51  1   67.251  33.287  10.290  1.00  1.00   7
ATOM    354  CA  ALA A  51  1   67.779  34.454   9.569  1.00  1.00   6
ATOM    355  C   ALA A  51  1   68.360  35.463  10.562  1.00  1.00   6
ATOM    356  O   ALA A  51  1   69.473  35.977  10.373  1.00  1.00   8
ATOM    357  CB  ALA A  51  1   66.681  35.115   8.790  1.00  1.00   6
ATOM    360  N   ALA A  52  1   67.576  35.713  11.594  1.00  1.00   7
ATOM    361  CA  ALA A  52  1   67.939  36.651  12.667  1.00  1.00   6
ATOM    362  C   ALA A  52  1   69.257  36.221  13.314  1.00  1.00   6
ATOM    363  O   ALA A  52  1   70.163  37.041  13.523  1.00  1.00   8
ATOM    364  CB  ALA A  52  1   66.866  36.672  13.715  1.00  1.00   6
ATOM    367  N   ALA A  53  1   69.316  34.936  13.610  1.00  1.00   7
ATOM    368  CA  ALA A  53  1   70.489  34.312  14.238  1.00  1.00   6
ATOM    369  C   ALA A  53  1   71.728  34.535  13.369  1.00  1.00   6
ATOM    370  O   ALA A  53  1   72.796  34.923  13.866  1.00  1.00   8
ATOM    371  CB  ALA A  53  1   70.263  32.837  14.394  1.00  1.00   6
ATOM    374  N   ALA A  54  1   71.539  34.278  12.088  1.00  1.00   7
ATOM    375  CA  ALA A  54  1   72.595  34.426  11.077  1.00  1.00   6
ATOM    376  C   ALA A  54  1   73.125  35.862  11.079  1.00  1.00   6
ATOM    377  O   ALA A  54  1   74.343  36.093  11.078  1.00  1.00   8
ATOM    378  CB  ALA A  54  1   72.051  34.111   9.715  1.00  1.00   6
ATOM    381  N   ALA A  55  1   72.179  36.783  11.082  1.00  1.00   7
ATOM    382  CA  ALA A  55  1   72.466  38.224  11.085  1.00  1.00   6
ATOM    383  C   ALA A  55  1   73.321  38.585  12.302  1.00  1.00   6
ATOM    384  O   ALA A  55  1   74.326  39.303  12.186  1.00  1.00   8
ATOM    385  CB  ALA A  55  1   71.185  39.002  11.142  1.00  1.00   6
ATOM    388  N   ALA A  56  1   72.886  38.069  13.436  1.00  1.00   7
ATOM    389  CA  ALA A  56  1   73.557  38.289  14.725  1.00  1.00   6
ATOM    390  C   ALA A  56  1   75.008  37.811  14.648  1.00  1.00   6
ATOM    391  O   ALA A  56  1   75.936  38.517  15.070  1.00  1.00   8
ATOM    392  CB  ALA A  56  1   72.851  37.528  15.808  1.00  1.00   6
ATOM    395  N   ALA A  57  1   75.152  36.616  14.105  1.00  1.00   7
ATOM    396  CA  ALA A  57  1   76.460  35.967  13.934  1.00  1.00   6
ATOM    397  C   ALA A  57  1   77.378  36.855  13.092  1.00  1.00   6
ATOM    398  O   ALA A  57  1   78.547  37.078  13.442  1.00  1.00   8
ATOM    399  CB  ALA A  57  1   76.290  34.647  13.241  1.00  1.00   6
ATOM    402  N   ALA A  58  1   76.811  37.333  12.001  1.00  1.00   7
ATOM    403  CA  ALA A  58  1   77.513  38.207  11.050  1.00  1.00   6
ATOM    404  C   ALA A  58  1   78.020  39.460  11.768  1.00  1.00   6
ATOM    405  O   ALA A  58  1   79.181  39.863  11.605  1.00  1.00   8
ATOM    406  CB  ALA A  58  1   76.582  38.621   9.949  1.00  1.00   6
ATOM    409  N   ALA A  59  1   77.121  40.035  12.544  1.00  1.00   7
ATOM    410  CA  ALA A  59  1   77.397  41.250  13.325  1.00  1.00   6
ATOM    411  C   ALA A  59  1   78.579  41.010  14.266  1.00  1.00   6
ATOM    412  O   ALA A  59  1   79.503  41.832  14.353  1.00  1.00   8
ATOM    413  CB  ALA A  59  1   76.193  41.620  14.141  1.00  1.00   6
ATOM    416  N   ALA A  60  1   78.507  39.878  14.942  1.00  1.00   7
ATOM    417  CA  ALA A  60  1   79.536  39.451  15.900  1.00  1.00   6
ATOM    418  C   ALA A  60  1   80.896  39.365  15.204  1.00  1.00   6
ATOM    419  O   ALA A  60  1   81.909  39.862  15.717  1.00  1.00   8
ATOM    420  CB  ALA A  60  1   79.189  38.103  16.459  1.00  1.00   6
ATOM    423  N   ALA A  61  1   80.867  38.729  14.047  1.00  1.00   7
ATOM    424  CA  ALA A  61  1   82.061  38.532  13.213  1.00  1.00   6
ATOM    425  C   ALA A  61  1   82.684  39.885  12.862  1.00  1.00   6
ATOM    426  O   ALA A  61  1   83.904  40.076  12.977  1.00  1.00   8
ATOM    427  CB  ALA A  61  1   81.689  37.824  11.944  1.00  1.00   6
ATOM    430  N   ALA A  62  1   81.814  40.784  12.442  1.00  1.00   7
ATOM    431  CA  ALA A  62  1   82.197  42.149  12.053  1.00  1.00   6
ATOM    432  C   ALA A  62  1   82.899  42.848  13.219  1.00  1.00   6
ATOM    433  O   ALA A  62  1   83.957  43.470  13.047  1.00  1.00   8
ATOM    434  CB  ALA A  62  1   80.977  42.936  11.676  1.00  1.00   6
ATOM    437  N   ALA A  63  1   82.276  42.718  14.376  1.00  1.00   7
ATOM    438  CA  ALA A  63  1   82.777  43.310  15.625  1.00  1.00   6
ATOM    439  C   ALA A  63  1   84.188  42.797  15.918  1.00  1.00   6
ATOM    440  O   ALA A  63  1   85.096  43.576  16.244  1.00  1.00   8
ATOM    441  CB  ALA A  63  1   81.877  42.938  16.766  1.00  1.00   6
ATOM    444  N   ALA A  64  1   84.322  41.490  15.791  1.00  1.00   7
ATOM    445  CA  ALA A  64  1   85.592  40.788  16.025  1.00  1.00   6
ATOM    446  C   ALA A  64  1   86.678  41.350  15.105  1.00  1.00   6
ATOM    447  O   ALA A  64  1   87.799  41.643  15.546  1.00  1.00   8
ATOM    448  CB  ALA A  64  1   85.428  39.323  15.747  1.00  1.00   6
ATOM    451  N   ALA A  65  1   86.301  41.481  13.847  1.00  1.00   7
ATOM    452  CA  ALA A  65  1   87.186  42.002  12.796  1.00  1.00   6
ATOM    453  C   ALA A  65  1   87.676  43.402  13.170  1.00  1.00   6
ATOM    454  O   ALA A  65  1   88.874  43.707  13.073  1.00  1.00   8
ATOM    455  CB  ALA A  65  1   86.447  42.076  11.493  1.00  1.00   6
ATOM    458  N   ALA A  66  1   86.720  44.211  13.589  1.00  1.00   7
ATOM    459  CA  ALA A  66  1   86.970  45.600  13.999  1.00  1.00   6
ATOM    460  C   ALA A  66  1   87.992  45.635  15.137  1.00  1.00   6
ATOM    461  O   ALA A  66  1   88.949  46.422  15.112  1.00  1.00   8
ATOM    462  CB  ALA A  66  1   85.694  46.233  14.471  1.00  1.00   6
ATOM    465  N   ALA A  67  1   87.748  44.770  16.104  1.00  1.00   7
ATOM    466  CA  ALA A  67  1   88.603  44.635  17.292  1.00  1.00   6
ATOM    467  C   ALA A  67  1   90.036  44.305  16.871  1.00  1.00   6
ATOM    468  O   ALA A  67  1   91.001  44.913  17.358  1.00  1.00   8
ATOM    469  CB  ALA A  67  1   88.089  43.534  18.172  1.00  1.00   6
ATOM    472  N   ALA A  68  1   90.124  43.344  15.970  1.00  1.00   7
ATOM    473  CA  ALA A  68  1   91.405  42.870  15.427  1.00  1.00   6
ATOM    474  C   ALA A  68  1   92.162  44.033  14.783  1.00  1.00   6
ATOM    475  O   ALA A  68  1   93.365  44.221  15.020  1.00  1.00   8
ATOM    476  CB  ALA A  68  1   91.162  41.814  14.390  1.00  1.00   6
ATOM    479  N   ALA A  69  1   91.423  44.779  13.983  1.00  1.00   7
ATOM    480  CA  ALA A  69  1   91.950  45.947  13.263  1.00  1.00   6
ATOM    481  C   ALA A  69  1   92.531  46.955  14.256  1.00  1.00   6
ATOM    482  O   ALA A  69  1   93.644  47.469  14.068  1.00  1.00   8
ATOM    483  CB  ALA A  69  1   90.852  46.608  12.484  1.00  1.00   6
ATOM    486  N   ALA A  70  1   91.748  47.204  15.289  1.00  1.00   7
ATOM    487  CA  ALA A  70  1   92.111  48.141  16.362  1.00  1.00   6
ATOM    488  C   ALA A  70  1   93.429  47.711  17.009  1.00  1.00   6
ATOM    489  O   ALA A  70  1   94.336  48.531  17.218  1.00  1.00   8
ATOM    490  CB  ALA A  70  1   91.039  48.162  17.410  1.00  1.00   6
"""

th70pdb_inverted = """
ATOM      1  N   ALA A   1      94.731  47.285  16.595  1.00  1.00           N  
ATOM      2  CA  ALA A   1      93.448  47.993  16.465  1.00  1.00           C  
ATOM      3  C   ALA A   1      92.663  47.438  15.274  1.00  1.00           C  
ATOM      4  O   ALA A   1      91.462  47.149  15.380  1.00  1.00           O  
ATOM      5  CB  ALA A   1      93.690  49.457  16.249  1.00  1.00           C  
ATOM      6  N   ALA A   2      93.380  47.308  14.173  1.00  1.00           N  
ATOM      7  CA  ALA A   2      92.824  46.795  12.913  1.00  1.00           C  
ATOM      8  C   ALA A   2      92.243  45.395  13.129  1.00  1.00           C  
ATOM      9  O   ALA A   2      91.120  45.098  12.696  1.00  1.00           O  
ATOM     10  CB  ALA A   2      93.901  46.720  11.871  1.00  1.00           C  
ATOM     11  N   ALA A   3      93.039  44.582  13.796  1.00  1.00           N  
ATOM     12  CA  ALA A   3      92.678  43.192  14.114  1.00  1.00           C  
ATOM     13  C   ALA A   3      91.376  43.160  14.918  1.00  1.00           C  
ATOM     14  O   ALA A   3      90.461  42.378  14.621  1.00  1.00           O  
ATOM     15  CB  ALA A   3      93.766  42.552  14.924  1.00  1.00           C  
ATOM     16  N   ALA A   4      91.342  44.022  15.918  1.00  1.00           N  
ATOM     17  CA  ALA A   4      90.187  44.157  16.817  1.00  1.00           C  
ATOM     18  C   ALA A   4      88.931  44.494  16.010  1.00  1.00           C  
ATOM     19  O   ALA A   4      87.866  43.892  16.203  1.00  1.00           O  
ATOM     20  CB  ALA A   4      90.436  45.253  17.811  1.00  1.00           C  
ATOM     21  N   ALA A   5      89.106  45.458  15.126  1.00  1.00           N  
ATOM     22  CA  ALA A   5      88.032  45.941  14.245  1.00  1.00           C  
ATOM     23  C   ALA A   5      87.481  44.783  13.409  1.00  1.00           C  
ATOM     24  O   ALA A   5      86.260  44.601  13.298  1.00  1.00           O  
ATOM     25  CB  ALA A   5      88.561  46.999  13.322  1.00  1.00           C  
ATOM     26  N   ALA A   6      88.413  44.036  12.848  1.00  1.00           N  
ATOM     27  CA  ALA A   6      88.106  42.872  12.003  1.00  1.00           C  
ATOM     28  C   ALA A   6      87.263  41.864  12.789  1.00  1.00           C  
ATOM     29  O   ALA A   6      86.247  41.357  12.292  1.00  1.00           O  
ATOM     30  CB  ALA A   6      89.375  42.208  11.562  1.00  1.00           C  
ATOM     31  N   ALA A   7      87.723  41.610  13.999  1.00  1.00           N  
ATOM     32  CA  ALA A   7      87.068  40.671  14.922  1.00  1.00           C  
ATOM     33  C   ALA A   7      85.623  41.106  15.173  1.00  1.00           C  
ATOM     34  O   ALA A   7      84.691  40.290  15.116  1.00  1.00           O  
ATOM     35  CB  ALA A   7      87.802  40.643  16.231  1.00  1.00           C  
ATOM     36  N   ALA A   8      85.489  42.391  15.445  1.00  1.00           N  
ATOM     37  CA  ALA A   8      84.188  43.020  15.718  1.00  1.00           C  
ATOM     38  C   ALA A   8      83.245  42.804  14.533  1.00  1.00           C  
ATOM     39  O   ALA A   8      82.078  42.421  14.708  1.00  1.00           O  
ATOM     40  CB  ALA A   8      84.367  44.494  15.937  1.00  1.00           C  
ATOM     41  N   ALA A   9      83.789  43.062  13.359  1.00  1.00           N  
ATOM     42  CA  ALA A   9      83.060  42.921  12.091  1.00  1.00           C  
ATOM     43  C   ALA A   9      82.544  41.488  11.938  1.00  1.00           C  
ATOM     44  O   ALA A   9      81.376  41.263  11.594  1.00  1.00           O  
ATOM     45  CB  ALA A   9      83.968  43.237  10.938  1.00  1.00           C  
ATOM     46  N   ALA A  10      83.448  40.563  12.205  1.00  1.00           N  
ATOM     47  CA  ALA A  10      83.165  39.122  12.124  1.00  1.00           C  
ATOM     48  C   ALA A  10      82.000  38.763  13.049  1.00  1.00           C  
ATOM     49  O   ALA A  10      81.066  38.051  12.652  1.00  1.00           O  
ATOM     50  CB  ALA A  10      84.375  38.338  12.537  1.00  1.00           C  
ATOM     51  N   ALA A  11      82.099  39.276  14.260  1.00  1.00           N  
ATOM     52  CA  ALA A  11      81.091  39.057  15.307  1.00  1.00           C  
ATOM     53  C   ALA A  11      79.723  39.543  14.824  1.00  1.00           C  
ATOM     54  O   ALA A  11      78.711  38.840  14.966  1.00  1.00           O  
ATOM     55  CB  ALA A  11      81.466  39.813  16.547  1.00  1.00           C  
ATOM     56  N   ALA A  12      79.743  40.739  14.268  1.00  1.00           N  
ATOM     57  CA  ALA A  12      78.540  41.395  13.736  1.00  1.00           C  
ATOM     58  C   ALA A  12      77.892  40.512  12.667  1.00  1.00           C  
ATOM     59  O   ALA A  12      76.672  40.294  12.673  1.00  1.00           O  
ATOM     60  CB  ALA A  12      78.903  42.715  13.124  1.00  1.00           C  
ATOM     61  N   ALA A  13      78.742  40.034  11.778  1.00  1.00           N  
ATOM     62  CA  ALA A  13      78.333  39.164  10.665  1.00  1.00           C  
ATOM     63  C   ALA A  13      77.639  37.914  11.207  1.00  1.00           C  
ATOM     64  O   ALA A  13      76.569  37.516  10.722  1.00  1.00           O  
ATOM     65  CB  ALA A  13      79.536  38.749   9.871  1.00  1.00           C  
ATOM     66  N   ALA A  14      78.281  37.332  12.204  1.00  1.00           N  
ATOM     67  CA  ALA A  14      77.790  36.117  12.872  1.00  1.00           C  
ATOM     68  C   ALA A  14      76.392  36.362  13.441  1.00  1.00           C  
ATOM     69  O   ALA A  14      75.477  35.543  13.262  1.00  1.00           O  
ATOM     70  CB  ALA A  14      78.713  35.741  13.992  1.00  1.00           C  
ATOM     71  N   ALA A  15      76.276  37.492  14.113  1.00  1.00           N  
ATOM     72  CA  ALA A  15      75.019  37.921  14.743  1.00  1.00           C  
ATOM     73  C   ALA A  15      73.911  38.017  13.692  1.00  1.00           C  
ATOM     74  O   ALA A  15      72.793  37.523  13.899  1.00  1.00           O  
ATOM     75  CB  ALA A  15      75.200  39.267  15.382  1.00  1.00           C  
ATOM     76  N   ALA A  16      74.268  38.653  12.594  1.00  1.00           N  
ATOM     77  CA  ALA A  16      73.358  38.858  11.456  1.00  1.00           C  
ATOM     78  C   ALA A  16      72.855  37.509  10.940  1.00  1.00           C  
ATOM     79  O   ALA A  16      71.651  37.324  10.706  1.00  1.00           O  
ATOM     80  CB  ALA A  16      74.077  39.567  10.346  1.00  1.00           C  
ATOM     81  N   ALA A  17      73.804  36.607  10.779  1.00  1.00           N  
ATOM     82  CA  ALA A  17      73.540  35.245  10.294  1.00  1.00           C  
ATOM     83  C   ALA A  17      72.535  34.546  11.213  1.00  1.00           C  
ATOM     84  O   ALA A  17      71.566  33.929  10.746  1.00  1.00           O  
ATOM     85  CB  ALA A  17      74.813  34.452  10.274  1.00  1.00           C  
ATOM     86  N   ALA A  18      72.807  34.671  12.498  1.00  1.00           N  
ATOM     87  CA  ALA A  18      71.971  34.080  13.553  1.00  1.00           C  
ATOM     88  C   ALA A  18      70.536  34.599  13.438  1.00  1.00           C  
ATOM     89  O   ALA A  18      69.570  33.824  13.492  1.00  1.00           O  
ATOM     90  CB  ALA A  18      72.515  34.445  14.903  1.00  1.00           C  
ATOM     91  N   ALA A  19      70.450  35.907  13.283  1.00  1.00           N  
ATOM     92  CA  ALA A  19      69.167  36.614  13.151  1.00  1.00           C  
ATOM     93  C   ALA A  19      68.384  36.058  11.960  1.00  1.00           C  
ATOM     94  O   ALA A  19      67.183  35.771  12.065  1.00  1.00           O  
ATOM     95  CB  ALA A  19      69.411  38.079  12.935  1.00  1.00           C  
ATOM     96  N   ALA A  20      69.099  35.928  10.860  1.00  1.00           N  
ATOM     97  CA  ALA A  20      68.545  35.414   9.599  1.00  1.00           C  
ATOM     98  C   ALA A  20      67.963  34.016   9.816  1.00  1.00           C  
ATOM     99  O   ALA A  20      66.840  33.717   9.384  1.00  1.00           O  
ATOM    100  CB  ALA A  20      69.621  35.339   8.558  1.00  1.00           C  
ATOM    101  N   ALA A  21      68.759  33.202  10.485  1.00  1.00           N  
ATOM    102  CA  ALA A  21      68.399  31.813  10.803  1.00  1.00           C  
ATOM    103  C   ALA A  21      67.096  31.781  11.606  1.00  1.00           C  
ATOM    104  O   ALA A  21      66.181  30.999  11.310  1.00  1.00           O  
ATOM    105  CB  ALA A  21      69.486  31.174  11.614  1.00  1.00           C  
ATOM    106  N   ALA A  22      67.061  32.643  12.606  1.00  1.00           N  
ATOM    107  CA  ALA A  22      65.907  32.779  13.505  1.00  1.00           C  
ATOM    108  C   ALA A  22      64.651  33.117  12.697  1.00  1.00           C  
ATOM    109  O   ALA A  22      63.586  32.512  12.891  1.00  1.00           O  
ATOM    110  CB  ALA A  22      66.156  33.877  14.497  1.00  1.00           C  
ATOM    111  N   ALA A  23      64.826  34.081  11.812  1.00  1.00           N  
ATOM    112  CA  ALA A  23      63.751  34.562  10.931  1.00  1.00           C  
ATOM    113  C   ALA A  23      63.202  33.404  10.095  1.00  1.00           C  
ATOM    114  O   ALA A  23      61.980  33.221   9.983  1.00  1.00           O  
ATOM    115  CB  ALA A  23      64.282  35.619  10.007  1.00  1.00           C  
ATOM    116  N   ALA A  24      64.134  32.656   9.535  1.00  1.00           N  
ATOM    117  CA  ALA A  24      63.827  31.492   8.692  1.00  1.00           C  
ATOM    118  C   ALA A  24      62.984  30.484   9.477  1.00  1.00           C  
ATOM    119  O   ALA A  24      61.968  29.977   8.980  1.00  1.00           O  
ATOM    120  CB  ALA A  24      65.096  30.827   8.252  1.00  1.00           C  
ATOM    121  N   ALA A  25      63.443  30.229  10.688  1.00  1.00           N  
ATOM    122  CA  ALA A  25      62.788  29.293  11.612  1.00  1.00           C  
ATOM    123  C   ALA A  25      61.343  29.727  11.861  1.00  1.00           C  
ATOM    124  O   ALA A  25      60.411  28.912  11.804  1.00  1.00           O  
ATOM    125  CB  ALA A  25      63.521  29.264  12.920  1.00  1.00           C  
ATOM    126  N   ALA A  26      61.209  31.013  12.133  1.00  1.00           N  
ATOM    127  CA  ALA A  26      59.908  31.643  12.405  1.00  1.00           C  
ATOM    128  C   ALA A  26      58.964  31.426  11.220  1.00  1.00           C  
ATOM    129  O   ALA A  26      57.798  31.042  11.395  1.00  1.00           O  
ATOM    130  CB  ALA A  26      60.087  33.116  12.622  1.00  1.00           C  
ATOM    131  N   ALA A  27      59.509  31.683  10.045  1.00  1.00           N  
ATOM    132  CA  ALA A  27      58.781  31.541   8.776  1.00  1.00           C  
ATOM    133  C   ALA A  27      58.265  30.108   8.626  1.00  1.00           C  
ATOM    134  O   ALA A  27      57.096  29.883   8.281  1.00  1.00           O  
ATOM    135  CB  ALA A  27      59.689  31.855   7.626  1.00  1.00           C  
ATOM    136  N   ALA A  28      59.168  29.183   8.895  1.00  1.00           N  
ATOM    137  CA  ALA A  28      58.884  27.742   8.812  1.00  1.00           C  
ATOM    138  C   ALA A  28      57.720  27.385   9.737  1.00  1.00           C  
ATOM    139  O   ALA A  28      56.787  26.671   9.340  1.00  1.00           O  
ATOM    140  CB  ALA A  28      60.096  26.959   9.228  1.00  1.00           C  
ATOM    141  N   ALA A  29      57.819  27.897  10.950  1.00  1.00           N  
ATOM    142  CA  ALA A  29      56.811  27.679  11.995  1.00  1.00           C  
ATOM    143  C   ALA A  29      55.442  28.164  11.513  1.00  1.00           C  
ATOM    144  O   ALA A  29      54.430  27.463  11.654  1.00  1.00           O  
ATOM    145  CB  ALA A  29      57.186  28.437  13.236  1.00  1.00           C  
ATOM    146  N   ALA A  30      55.463  29.360  10.955  1.00  1.00           N  
ATOM    147  CA  ALA A  30      54.260  30.016  10.422  1.00  1.00           C  
ATOM    148  C   ALA A  30      53.612  29.134   9.353  1.00  1.00           C  
ATOM    149  O   ALA A  30      52.391  28.915   9.359  1.00  1.00           O  
ATOM    150  CB  ALA A  30      54.623  31.336   9.808  1.00  1.00           C  
ATOM    151  N   ALA A  31      54.463  28.654   8.466  1.00  1.00           N  
ATOM    152  CA  ALA A  31      54.054  27.784   7.354  1.00  1.00           C  
ATOM    153  C   ALA A  31      53.359  26.533   7.895  1.00  1.00           C  
ATOM    154  O   ALA A  31      52.290  26.136   7.410  1.00  1.00           O  
ATOM    155  CB  ALA A  31      55.258  27.367   6.560  1.00  1.00           C  
ATOM    156  N   ALA A  32      54.000  25.952   8.893  1.00  1.00           N  
ATOM    157  CA  ALA A  32      53.510  24.738   9.561  1.00  1.00           C  
ATOM    158  C   ALA A  32      52.111  24.983  10.130  1.00  1.00           C  
ATOM    159  O   ALA A  32      51.197  24.165   9.951  1.00  1.00           O  
ATOM    160  CB  ALA A  32      54.432  24.362  10.683  1.00  1.00           C  
ATOM    161  N   ALA A  33      51.995  26.114  10.801  1.00  1.00           N  
ATOM    162  CA  ALA A  33      50.738  26.545  11.430  1.00  1.00           C  
ATOM    163  C   ALA A  33      49.630  26.638  10.378  1.00  1.00           C  
ATOM    164  O   ALA A  33      48.512  26.144  10.585  1.00  1.00           O  
ATOM    165  CB  ALA A  33      50.920  27.890  12.068  1.00  1.00           C  
ATOM    166  N   ALA A  34      49.988  27.274   9.280  1.00  1.00           N  
ATOM    167  CA  ALA A  34      49.079  27.479   8.142  1.00  1.00           C  
ATOM    168  C   ALA A  34      48.575  26.129   7.627  1.00  1.00           C  
ATOM    169  O   ALA A  34      47.371  25.944   7.393  1.00  1.00           O  
ATOM    170  CB  ALA A  34      49.798  28.186   7.031  1.00  1.00           C  
ATOM    171  N   ALA A  35      49.525  25.226   7.467  1.00  1.00           N  
ATOM    172  CA  ALA A  35      49.261  23.864   6.982  1.00  1.00           C  
ATOM    173  C   ALA A  35      48.254  23.167   7.901  1.00  1.00           C  
ATOM    174  O   ALA A  35      47.286  22.550   7.436  1.00  1.00           O  
ATOM    175  CB  ALA A  35      50.534  23.071   6.963  1.00  1.00           C  
ATOM    176  N   ALA A  36      48.527  23.293   9.188  1.00  1.00           N  
ATOM    177  CA  ALA A  36      47.690  22.701  10.243  1.00  1.00           C  
ATOM    178  C   ALA A  36      46.257  23.222  10.127  1.00  1.00           C  
ATOM    179  O   ALA A  36      45.289  22.446  10.180  1.00  1.00           O  
ATOM    180  CB  ALA A  36      48.233  23.068  11.592  1.00  1.00           C  
ATOM    181  N   ALA A  37      46.169  24.529   9.970  1.00  1.00           N  
ATOM    182  CA  ALA A  37      44.888  25.236   9.838  1.00  1.00           C  
ATOM    183  C   ALA A  37      44.105  24.681   8.647  1.00  1.00           C  
ATOM    184  O   ALA A  37      42.902  24.393   8.752  1.00  1.00           O  
ATOM    185  CB  ALA A  37      45.130  26.700   9.621  1.00  1.00           C  
ATOM    186  N   ALA A  38      44.820  24.549   7.547  1.00  1.00           N  
ATOM    187  CA  ALA A  38      44.266  24.034   6.285  1.00  1.00           C  
ATOM    188  C   ALA A  38      43.684  22.635   6.503  1.00  1.00           C  
ATOM    189  O   ALA A  38      42.561  22.336   6.072  1.00  1.00           O  
ATOM    190  CB  ALA A  38      45.342  23.957   5.245  1.00  1.00           C  
ATOM    191  N   ALA A  39      44.479  21.822   7.174  1.00  1.00           N  
ATOM    192  CA  ALA A  39      44.118  20.433   7.493  1.00  1.00           C  
ATOM    193  C   ALA A  39      42.816  20.403   8.296  1.00  1.00           C  
ATOM    194  O   ALA A  39      41.902  19.620   8.000  1.00  1.00           O  
ATOM    195  CB  ALA A  39      45.206  19.794   8.305  1.00  1.00           C  
ATOM    196  N   ALA A  40      42.781  21.265   9.294  1.00  1.00           N  
ATOM    197  CA  ALA A  40      41.626  21.403  10.194  1.00  1.00           C  
ATOM    198  C   ALA A  40      40.370  21.739   9.385  1.00  1.00           C  
ATOM    199  O   ALA A  40      39.305  21.135   9.578  1.00  1.00           O  
ATOM    200  CB  ALA A  40      41.875  22.499  11.184  1.00  1.00           C  
ATOM    201  N   ALA A  41      40.545  22.702   8.498  1.00  1.00           N  
ATOM    202  CA  ALA A  41      39.473  23.182   7.616  1.00  1.00           C  
ATOM    203  C   ALA A  41      38.923  22.024   6.782  1.00  1.00           C  
ATOM    204  O   ALA A  41      37.701  21.841   6.669  1.00  1.00           O  
ATOM    205  CB  ALA A  41      40.003  24.239   6.693  1.00  1.00           C  
ATOM    206  N   ALA A  42      39.855  21.275   6.222  1.00  1.00           N  
ATOM    207  CA  ALA A  42      39.546  20.111   5.379  1.00  1.00           C  
ATOM    208  C   ALA A  42      38.704  19.105   6.165  1.00  1.00           C  
ATOM    209  O   ALA A  42      37.688  18.596   5.669  1.00  1.00           O  
ATOM    210  CB  ALA A  42      40.817  19.446   4.941  1.00  1.00           C  
ATOM    211  N   ALA A  43      39.164  18.850   7.376  1.00  1.00           N  
ATOM    212  CA  ALA A  43      38.508  17.914   8.301  1.00  1.00           C  
ATOM    213  C   ALA A  43      37.063  18.350   8.551  1.00  1.00           C  
ATOM    214  O   ALA A  43      36.130  17.534   8.494  1.00  1.00           O  
ATOM    215  CB  ALA A  43      39.240  17.888   9.610  1.00  1.00           C  
ATOM    216  N   ALA A  44      36.928  19.635   8.819  1.00  1.00           N  
ATOM    217  CA  ALA A  44      35.628  20.265   9.092  1.00  1.00           C  
ATOM    218  C   ALA A  44      34.684  20.048   7.907  1.00  1.00           C  
ATOM    219  O   ALA A  44      33.518  19.664   8.081  1.00  1.00           O  
ATOM    220  CB  ALA A  44      35.807  21.738   9.307  1.00  1.00           C  
ATOM    221  N   ALA A  45      35.229  20.303   6.733  1.00  1.00           N  
ATOM    222  CA  ALA A  45      34.501  20.161   5.463  1.00  1.00           C  
ATOM    223  C   ALA A  45      33.986  18.728   5.314  1.00  1.00           C  
ATOM    224  O   ALA A  45      32.817  18.503   4.967  1.00  1.00           O  
ATOM    225  CB  ALA A  45      35.410  20.475   4.312  1.00  1.00           C  
ATOM    226  N   ALA A  46      34.888  17.803   5.582  1.00  1.00           N  
ATOM    227  CA  ALA A  46      34.606  16.363   5.501  1.00  1.00           C  
ATOM    228  C   ALA A  46      33.440  16.005   6.426  1.00  1.00           C  
ATOM    229  O   ALA A  46      32.506  15.292   6.029  1.00  1.00           O  
ATOM    230  CB  ALA A  46      35.816  15.578   5.917  1.00  1.00           C  
ATOM    231  N   ALA A  47      33.539  16.518   7.638  1.00  1.00           N  
ATOM    232  CA  ALA A  47      32.530  16.302   8.684  1.00  1.00           C  
ATOM    233  C   ALA A  47      31.162  16.787   8.200  1.00  1.00           C  
ATOM    234  O   ALA A  47      30.149  16.085   8.343  1.00  1.00           O  
ATOM    235  CB  ALA A  47      32.905  17.060   9.923  1.00  1.00           C  
ATOM    236  N   ALA A  48      31.182  17.982   7.641  1.00  1.00           N  
ATOM    237  CA  ALA A  48      29.979  18.638   7.108  1.00  1.00           C  
ATOM    238  C   ALA A  48      29.332  17.754   6.040  1.00  1.00           C  
ATOM    239  O   ALA A  48      28.112  17.536   6.044  1.00  1.00           O  
ATOM    240  CB  ALA A  48      30.344  19.957   6.494  1.00  1.00           C  
ATOM    241  N   ALA A  49      30.183  17.273   5.152  1.00  1.00           N  
ATOM    242  CA  ALA A  49      29.775  16.403   4.041  1.00  1.00           C  
ATOM    243  C   ALA A  49      29.080  15.153   4.585  1.00  1.00           C  
ATOM    244  O   ALA A  49      28.010  14.756   4.099  1.00  1.00           O  
ATOM    245  CB  ALA A  49      30.978  15.985   3.248  1.00  1.00           C  
ATOM    246  N   ALA A  50      29.721  14.572   5.581  1.00  1.00           N  
ATOM    247  CA  ALA A  50      29.231  13.359   6.251  1.00  1.00           C  
ATOM    248  C   ALA A  50      27.830  13.605   6.818  1.00  1.00           C  
ATOM    249  O   ALA A  50      26.916  12.786   6.641  1.00  1.00           O  
ATOM    250  CB  ALA A  50      30.152  12.983   7.373  1.00  1.00           C  
ATOM    251  N   ALA A  51      27.714  14.736   7.490  1.00  1.00           N  
ATOM    252  CA  ALA A  51      26.458  15.167   8.119  1.00  1.00           C  
ATOM    253  C   ALA A  51      25.351  15.260   7.066  1.00  1.00           C  
ATOM    254  O   ALA A  51      24.231  14.768   7.272  1.00  1.00           O  
ATOM    255  CB  ALA A  51      26.639  16.514   8.754  1.00  1.00           C  
ATOM    256  N   ALA A  52      25.708  15.896   5.966  1.00  1.00           N  
ATOM    257  CA  ALA A  52      24.800  16.099   4.827  1.00  1.00           C  
ATOM    258  C   ALA A  52      24.295  14.749   4.313  1.00  1.00           C  
ATOM    259  O   ALA A  52      23.093  14.564   4.079  1.00  1.00           O  
ATOM    260  CB  ALA A  52      25.519  16.806   3.717  1.00  1.00           C  
ATOM    261  N   ALA A  53      25.245  13.846   4.156  1.00  1.00           N  
ATOM    262  CA  ALA A  53      24.981  12.483   3.671  1.00  1.00           C  
ATOM    263  C   ALA A  53      23.975  11.787   4.589  1.00  1.00           C  
ATOM    264  O   ALA A  53      23.006  11.170   4.124  1.00  1.00           O  
ATOM    265  CB  ALA A  53      26.254  11.691   3.654  1.00  1.00           C  
ATOM    266  N   ALA A  54      24.246  11.913   5.876  1.00  1.00           N  
ATOM    267  CA  ALA A  54      23.410  11.324   6.931  1.00  1.00           C  
ATOM    268  C   ALA A  54      21.976  11.844   6.815  1.00  1.00           C  
ATOM    269  O   ALA A  54      21.010  11.068   6.870  1.00  1.00           O  
ATOM    270  CB  ALA A  54      23.952  11.691   8.281  1.00  1.00           C  
ATOM    271  N   ALA A  55      21.889  13.152   6.657  1.00  1.00           N  
ATOM    272  CA  ALA A  55      20.607  13.858   6.524  1.00  1.00           C  
ATOM    273  C   ALA A  55      19.824  13.301   5.333  1.00  1.00           C  
ATOM    274  O   ALA A  55      18.622  13.014   5.438  1.00  1.00           O  
ATOM    275  CB  ALA A  55      20.850  15.322   6.306  1.00  1.00           C  
ATOM    276  N   ALA A  56      20.541  13.169   4.233  1.00  1.00           N  
ATOM    277  CA  ALA A  56      19.986  12.654   2.974  1.00  1.00           C  
ATOM    278  C   ALA A  56      19.405  11.256   3.192  1.00  1.00           C  
ATOM    279  O   ALA A  56      18.282  10.957   2.759  1.00  1.00           O  
ATOM    280  CB  ALA A  56      21.063  12.576   1.932  1.00  1.00           C  
ATOM    281  N   ALA A  57      20.200  10.441   3.863  1.00  1.00           N  
ATOM    282  CA  ALA A  57      19.838   9.054   4.183  1.00  1.00           C  
ATOM    283  C   ALA A  57      18.536   9.024   4.985  1.00  1.00           C  
ATOM    284  O   ALA A  57      17.621   8.240   4.689  1.00  1.00           O  
ATOM    285  CB  ALA A  57      20.925   8.415   4.996  1.00  1.00           C  
ATOM    286  N   ALA A  58      18.500   9.886   5.983  1.00  1.00           N  
ATOM    287  CA  ALA A  58      17.345  10.025   6.882  1.00  1.00           C  
ATOM    288  C   ALA A  58      16.090  10.362   6.072  1.00  1.00           C  
ATOM    289  O   ALA A  58      15.024   9.758   6.266  1.00  1.00           O  
ATOM    290  CB  ALA A  58      17.594  11.123   7.872  1.00  1.00           C  
ATOM    291  N   ALA A  59      16.265  11.323   5.185  1.00  1.00           N  
ATOM    292  CA  ALA A  59      15.192  11.803   4.302  1.00  1.00           C  
ATOM    293  C   ALA A  59      14.643  10.645   3.469  1.00  1.00           C  
ATOM    294  O   ALA A  59      13.422  10.462   3.356  1.00  1.00           O  
ATOM    295  CB  ALA A  59      15.722  12.860   3.378  1.00  1.00           C  
ATOM    296  N   ALA A  60      15.575   9.895   2.910  1.00  1.00           N  
ATOM    297  CA  ALA A  60      15.267   8.731   2.068  1.00  1.00           C  
ATOM    298  C   ALA A  60      14.424   7.725   2.854  1.00  1.00           C  
ATOM    299  O   ALA A  60      13.408   7.216   2.359  1.00  1.00           O  
ATOM    300  CB  ALA A  60      16.538   8.064   1.630  1.00  1.00           C  
ATOM    301  N   ALA A  61      14.883   7.471   4.066  1.00  1.00           N  
ATOM    302  CA  ALA A  61      14.227   6.536   4.990  1.00  1.00           C  
ATOM    303  C   ALA A  61      12.782   6.972   5.239  1.00  1.00           C  
ATOM    304  O   ALA A  61      11.849   6.156   5.183  1.00  1.00           O  
ATOM    305  CB  ALA A  61      14.959   6.509   6.299  1.00  1.00           C  
ATOM    306  N   ALA A  62      12.647   8.257   5.509  1.00  1.00           N  
ATOM    307  CA  ALA A  62      11.346   8.888   5.778  1.00  1.00           C  
ATOM    308  C   ALA A  62      10.403   8.669   4.593  1.00  1.00           C  
ATOM    309  O   ALA A  62       9.238   8.286   4.767  1.00  1.00           O  
ATOM    310  CB  ALA A  62      11.527  10.361   5.993  1.00  1.00           C  
ATOM    311  N   ALA A  63      10.950   8.925   3.419  1.00  1.00           N  
ATOM    312  CA  ALA A  63      10.221   8.781   2.149  1.00  1.00           C  
ATOM    313  C   ALA A  63       9.706   7.349   2.001  1.00  1.00           C  
ATOM    314  O   ALA A  63       8.537   7.122   1.655  1.00  1.00           O  
ATOM    315  CB  ALA A  63      11.131   9.093   0.998  1.00  1.00           C  
ATOM    316  N   ALA A  64      10.608   6.423   2.271  1.00  1.00           N  
ATOM    317  CA  ALA A  64      10.326   4.982   2.192  1.00  1.00           C  
ATOM    318  C   ALA A  64       9.161   4.626   3.116  1.00  1.00           C  
ATOM    319  O   ALA A  64       8.227   3.913   2.719  1.00  1.00           O  
ATOM    320  CB  ALA A  64      11.536   4.199   2.608  1.00  1.00           C  
ATOM    321  N   ALA A  65       9.259   5.140   4.327  1.00  1.00           N  
ATOM    322  CA  ALA A  65       8.249   4.925   5.373  1.00  1.00           C  
ATOM    323  C   ALA A  65       6.881   5.408   4.889  1.00  1.00           C  
ATOM    324  O   ALA A  65       5.868   4.707   5.030  1.00  1.00           O  
ATOM    325  CB  ALA A  65       8.624   5.683   6.611  1.00  1.00           C  
ATOM    326  N   ALA A  66       6.902   6.605   4.329  1.00  1.00           N  
ATOM    327  CA  ALA A  66       5.699   7.259   3.795  1.00  1.00           C  
ATOM    328  C   ALA A  66       5.052   6.376   2.726  1.00  1.00           C  
ATOM    329  O   ALA A  66       3.832   6.158   2.731  1.00  1.00           O  
ATOM    330  CB  ALA A  66       6.065   8.578   3.179  1.00  1.00           C  
ATOM    331  N   ALA A  67       5.904   5.894   1.840  1.00  1.00           N  
ATOM    332  CA  ALA A  67       5.496   5.022   0.729  1.00  1.00           C  
ATOM    333  C   ALA A  67       4.801   3.772   1.272  1.00  1.00           C  
ATOM    334  O   ALA A  67       3.732   3.375   0.787  1.00  1.00           O  
ATOM    335  CB  ALA A  67       6.699   4.604  -0.064  1.00  1.00           C  
ATOM    336  N   ALA A  68       5.441   3.193   2.271  1.00  1.00           N  
ATOM    337  CA  ALA A  68       4.950   1.980   2.940  1.00  1.00           C  
ATOM    338  C   ALA A  68       3.551   2.227   3.508  1.00  1.00           C  
ATOM    339  O   ALA A  68       2.636   1.407   3.330  1.00  1.00           O  
ATOM    340  CB  ALA A  68       5.871   1.606   4.063  1.00  1.00           C  
ATOM    341  N   ALA A  69       3.433   3.358   4.178  1.00  1.00           N  
ATOM    342  CA  ALA A  69       2.177   3.791   4.806  1.00  1.00           C  
ATOM    343  C   ALA A  69       1.071   3.882   3.753  1.00  1.00           C  
ATOM    344  O   ALA A  69      -0.049   3.391   3.958  1.00  1.00           O  
ATOM    345  CB  ALA A  69       2.358   5.137   5.441  1.00  1.00           C  
ATOM    346  N   ALA A  70       1.428   4.517   2.652  1.00  1.00           N  
ATOM    347  CA  ALA A  70       0.520   4.719   1.515  1.00  1.00           C  
ATOM    348  C   ALA A  70       0.016   3.370   1.000  1.00  1.00           C  
ATOM    349  O   ALA A  70      -1.188   3.184   0.766  1.00  1.00           O  
ATOM    350  CB  ALA A  70       1.239   5.425   0.403  1.00  1.00           C  
"""
th70pdb_inverted2 = """
ATOM      1  N   ALA B   1       1.522   2.029   2.874  1.00  1.00           N
ATOM      2  CA  ALA B   1       0.255   2.425   3.505  1.00  1.00           C
ATOM      3  C   ALA B   1      -0.844   2.538   2.446  1.00  1.00           C
ATOM      4  O   ALA B   1      -1.959   2.024   2.625  1.00  1.00           O
ATOM      5  CB  ALA B   1       0.412   3.751   4.186  1.00  1.00           C
ATOM      6  N   ALA B   2       3.548   1.953   0.981  1.00  1.00           N
ATOM      7  CA  ALA B   2       3.066   0.713   1.606  1.00  1.00           C
ATOM      8  C   ALA B   2       1.659   0.922   2.168  1.00  1.00           C
ATOM      9  O   ALA B   2       0.757   0.099   1.955  1.00  1.00           O
ATOM     10  CB  ALA B   2       3.983   0.312   2.723  1.00  1.00           C
ATOM     11  N   ALA B   3       3.980   4.672   0.643  1.00  1.00           N
ATOM     12  CA  ALA B   3       3.592   3.833  -0.500  1.00  1.00           C
ATOM     13  C   ALA B   3       2.909   2.557  -0.004  1.00  1.00           C
ATOM     14  O   ALA B   3       1.848   2.162  -0.512  1.00  1.00           O
ATOM     15  CB  ALA B   3       4.807   3.457  -1.294  1.00  1.00           C
ATOM     16  N   ALA B   4       4.947   5.312   3.164  1.00  1.00           N
ATOM     17  CA  ALA B   4       3.741   5.969   2.640  1.00  1.00           C
ATOM     18  C   ALA B   4       3.115   5.114   1.538  1.00  1.00           C
ATOM     19  O   ALA B   4       1.897   4.880   1.525  1.00  1.00           O
ATOM     20  CB  ALA B   4       4.094   7.312   2.072  1.00  1.00           C
ATOM     21  N   ALA B   5       7.322   3.879   3.135  1.00  1.00           N
ATOM     22  CA  ALA B   5       6.306   3.615   4.164  1.00  1.00           C
ATOM     23  C   ALA B   5       4.936   4.098   3.684  1.00  1.00           C
ATOM     24  O   ALA B   5       3.932   3.381   3.793  1.00  1.00           O
ATOM     25  CB  ALA B   5       6.660   4.337   5.431  1.00  1.00           C
ATOM     26  N   ALA B   6       8.673   5.245   1.134  1.00  1.00           N
ATOM     27  CA  ALA B   6       8.410   3.805   1.005  1.00  1.00           C
ATOM     28  C   ALA B   6       7.241   3.403   1.905  1.00  1.00           C
ATOM     29  O   ALA B   6       6.319   2.693   1.478  1.00  1.00           O
ATOM     30  CB  ALA B   6       9.625   3.024   1.406  1.00  1.00           C
ATOM     31  N   ALA B   7       8.972   7.712   2.367  1.00  1.00           N
ATOM     32  CA  ALA B   7       8.257   7.601   1.088  1.00  1.00           C
ATOM     33  C   ALA B   7       7.762   6.168   0.887  1.00  1.00           C
ATOM     34  O   ALA B   7       6.599   5.940   0.523  1.00  1.00           O
ATOM     35  CB  ALA B   7       9.172   7.964  -0.045  1.00  1.00           C
ATOM     36  N   ALA B   8      10.661   6.997   4.449  1.00  1.00           N
ATOM     37  CA  ALA B   8       9.350   7.601   4.728  1.00  1.00           C
ATOM     38  C   ALA B   8       8.420   7.411   3.528  1.00  1.00           C
ATOM     39  O   ALA B   8       7.257   7.008   3.679  1.00  1.00           O
ATOM     40  CB  ALA B   8       9.507   9.069   4.993  1.00  1.00           C
ATOM     41  N   ALA B   9      12.918   6.287   3.001  1.00  1.00           N
ATOM     42  CA  ALA B   9      12.266   5.313   3.889  1.00  1.00           C
ATOM     43  C   ALA B   9      10.813   5.723   4.138  1.00  1.00           C
ATOM     44  O   ALA B   9       9.892   4.898   4.046  1.00  1.00           O
ATOM     45  CB  ALA B   9      12.988   5.253   5.202  1.00  1.00           C
ATOM     46  N   ALA B  10      13.589   8.757   1.932  1.00  1.00           N
ATOM     47  CA  ALA B  10      13.303   7.617   1.050  1.00  1.00           C
ATOM     48  C   ALA B  10      12.467   6.575   1.795  1.00  1.00           C
ATOM     49  O   ALA B  10      11.462   6.070   1.273  1.00  1.00           O
ATOM     50  CB  ALA B  10      14.586   6.982   0.601  1.00  1.00           C
ATOM     51  N   ALA B  11      14.241  10.117   4.259  1.00  1.00           N
ATOM     52  CA  ALA B  11      13.170  10.613   3.384  1.00  1.00           C
ATOM     53  C   ALA B  11      12.642   9.475   2.508  1.00  1.00           C
ATOM     54  O   ALA B  11      11.424   9.281   2.378  1.00  1.00           O
ATOM     55  CB  ALA B  11      13.694  11.705   2.500  1.00  1.00           C
ATOM     56  N   ALA B  12      16.487   8.683   5.029  1.00  1.00           N
ATOM     57  CA  ALA B  12      15.322   8.776   5.921  1.00  1.00           C
ATOM     58  C   ALA B  12      14.071   9.125   5.113  1.00  1.00           C
ATOM     59  O   ALA B  12      13.012   8.502   5.277  1.00  1.00           O
ATOM     60  CB  ALA B  12      15.549   9.844   6.951  1.00  1.00           C
ATOM     61  N   ALA B  13      18.197   9.329   2.944  1.00  1.00           N
ATOM     62  CA  ALA B  13      17.852   7.927   3.214  1.00  1.00           C
ATOM     63  C   ALA B  13      16.543   7.854   4.004  1.00  1.00           C
ATOM     64  O   ALA B  13      15.641   7.070   3.674  1.00  1.00           O
ATOM     65  CB  ALA B  13      18.940   7.275   4.016  1.00  1.00           C
ATOM     66  N   ALA B  14      18.501  12.047   3.408  1.00  1.00           N
ATOM     67  CA  ALA B  14      17.963  11.566   2.127  1.00  1.00           C
ATOM     68  C   ALA B  14      17.399  10.154   2.294  1.00  1.00           C
ATOM     69  O   ALA B  14      16.284   9.855   1.840  1.00  1.00           O
ATOM     70  CB  ALA B  14      19.051  11.537   1.093  1.00  1.00           C
ATOM     71  N   ALA B  15      19.829  11.965   5.842  1.00  1.00           N
ATOM     72  CA  ALA B  15      18.539  12.660   5.721  1.00  1.00           C
ATOM     73  C   ALA B  15      17.773  12.134   4.506  1.00  1.00           C
ATOM     74  O   ALA B  15      16.575  11.828   4.590  1.00  1.00           O
ATOM     75  CB  ALA B  15      18.764  14.134   5.553  1.00  1.00           C
ATOM     76  N   ALA B  16      22.208  10.784   5.042  1.00  1.00           N
ATOM     77  CA  ALA B  16      21.371  10.149   6.069  1.00  1.00           C
ATOM     78  C   ALA B  16      19.930  10.654   5.957  1.00  1.00           C
ATOM     79  O   ALA B  16      18.973   9.865   5.977  1.00  1.00           O
ATOM     80  CB  ALA B  16      21.897  10.478   7.435  1.00  1.00           C
ATOM     81  N   ALA B  17      23.196  12.785   3.394  1.00  1.00           N
ATOM     82  CA  ALA B  17      22.955  11.436   2.864  1.00  1.00           C
ATOM     83  C   ALA B  17      21.950  10.697   3.750  1.00  1.00           C
ATOM     84  O   ALA B  17      20.993  10.083   3.255  1.00  1.00           O
ATOM     85  CB  ALA B  17      24.238  10.659   2.831  1.00  1.00           C
ATOM     86  N   ALA B  18      23.617  14.779   5.276  1.00  1.00           N
ATOM     87  CA  ALA B  18      22.716  15.008   4.138  1.00  1.00           C
ATOM     88  C   ALA B  18      22.234  13.671   3.574  1.00  1.00           C
ATOM     89  O   ALA B  18      21.035  13.478   3.323  1.00  1.00           O
ATOM     90  CB  ALA B  18      23.437  15.760   3.058  1.00  1.00           C
ATOM     91  N   ALA B  19      25.626  13.594   6.778  1.00  1.00           N
ATOM     92  CA  ALA B  19      24.358  13.989   7.410  1.00  1.00           C
ATOM     93  C   ALA B  19      23.259  14.103   6.352  1.00  1.00           C
ATOM     94  O   ALA B  19      22.145  13.589   6.531  1.00  1.00           O
ATOM     95  CB  ALA B  19      24.517  15.316   8.092  1.00  1.00           C
ATOM     96  N   ALA B  20      27.651  13.520   4.885  1.00  1.00           N
ATOM     97  CA  ALA B  20      27.170  12.279   5.508  1.00  1.00           C
ATOM     98  C   ALA B  20      25.762  12.488   6.071  1.00  1.00           C
ATOM     99  O   ALA B  20      24.860  11.664   5.858  1.00  1.00           O
ATOM    100  CB  ALA B  20      28.086  11.878   6.626  1.00  1.00           C
ATOM    101  N   ALA B  21      28.082  16.239   4.549  1.00  1.00           N
ATOM    102  CA  ALA B  21      27.695  15.401   3.406  1.00  1.00           C
ATOM    103  C   ALA B  21      27.011  14.125   3.901  1.00  1.00           C
ATOM    104  O   ALA B  21      25.951  13.730   3.393  1.00  1.00           O
ATOM    105  CB  ALA B  21      28.909  15.026   2.610  1.00  1.00           C
ATOM    106  N   ALA B  22      29.050  16.877   7.069  1.00  1.00           N
ATOM    107  CA  ALA B  22      27.844  17.535   6.547  1.00  1.00           C
ATOM    108  C   ALA B  22      27.217  16.679   5.444  1.00  1.00           C
ATOM    109  O   ALA B  22      26.000  16.446   5.432  1.00  1.00           O
ATOM    110  CB  ALA B  22      28.196  18.878   5.980  1.00  1.00           C
ATOM    111  N   ALA B  23      31.425  15.444   7.038  1.00  1.00           N
ATOM    112  CA  ALA B  23      30.410  15.180   8.068  1.00  1.00           C
ATOM    113  C   ALA B  23      29.040  15.663   7.588  1.00  1.00           C
ATOM    114  O   ALA B  23      28.035  14.945   7.697  1.00  1.00           O
ATOM    115  CB  ALA B  23      30.765  15.900   9.335  1.00  1.00           C
ATOM    116  N   ALA B  24      32.775  16.813   5.038  1.00  1.00           N
ATOM    117  CA  ALA B  24      32.513  15.372   4.907  1.00  1.00           C
ATOM    118  C   ALA B  24      31.344  14.970   5.809  1.00  1.00           C
ATOM    119  O   ALA B  24      30.423  14.258   5.381  1.00  1.00           O
ATOM    120  CB  ALA B  24      33.728  14.590   5.308  1.00  1.00           C
ATOM    121  N   ALA B  25      33.075  19.278   6.273  1.00  1.00           N
ATOM    122  CA  ALA B  25      32.360  19.169   4.994  1.00  1.00           C
ATOM    123  C   ALA B  25      31.865  17.735   4.792  1.00  1.00           C
ATOM    124  O   ALA B  25      30.700  17.506   4.429  1.00  1.00           O
ATOM    125  CB  ALA B  25      33.274  19.532   3.862  1.00  1.00           C
ATOM    126  N   ALA B  26      34.764  18.561   8.353  1.00  1.00           N
ATOM    127  CA  ALA B  26      33.453  19.166   8.633  1.00  1.00           C
ATOM    128  C   ALA B  26      32.523  18.976   7.434  1.00  1.00           C
ATOM    129  O   ALA B  26      31.361  18.573   7.585  1.00  1.00           O
ATOM    130  CB  ALA B  26      33.612  20.633   8.900  1.00  1.00           C
ATOM    131  N   ALA B  27      37.021  17.854   6.905  1.00  1.00           N
ATOM    132  CA  ALA B  27      36.370  16.878   7.792  1.00  1.00           C
ATOM    133  C   ALA B  27      34.917  17.288   8.042  1.00  1.00           C
ATOM    134  O   ALA B  27      33.996  16.463   7.950  1.00  1.00           O
ATOM    135  CB  ALA B  27      37.092  16.818   9.106  1.00  1.00           C
ATOM    136  N   ALA B  28      37.691  20.324   5.837  1.00  1.00           N
ATOM    137  CA  ALA B  28      37.406  19.185   4.954  1.00  1.00           C
ATOM    138  C   ALA B  28      36.570  18.141   5.699  1.00  1.00           C
ATOM    139  O   ALA B  28      35.564  17.638   5.177  1.00  1.00           O
ATOM    140  CB  ALA B  28      38.689  18.549   4.505  1.00  1.00           C
ATOM    141  N   ALA B  29      38.345  21.683   8.165  1.00  1.00           N
ATOM    142  CA  ALA B  29      37.273  22.179   7.291  1.00  1.00           C
ATOM    143  C   ALA B  29      36.745  21.042   6.414  1.00  1.00           C
ATOM    144  O   ALA B  29      35.527  20.848   6.284  1.00  1.00           O
ATOM    145  CB  ALA B  29      37.797  23.272   6.407  1.00  1.00           C
ATOM    146  N   ALA B  30      40.591  20.248   8.934  1.00  1.00           N
ATOM    147  CA  ALA B  30      39.426  20.341   9.826  1.00  1.00           C
ATOM    148  C   ALA B  30      38.175  20.689   9.018  1.00  1.00           C
ATOM    149  O   ALA B  30      37.115  20.066   9.182  1.00  1.00           O
ATOM    150  CB  ALA B  30      39.653  21.408  10.856  1.00  1.00           C
ATOM    151  N   ALA B  31      42.300  20.896   6.848  1.00  1.00           N
ATOM    152  CA  ALA B  31      41.955  19.493   7.118  1.00  1.00           C
ATOM    153  C   ALA B  31      40.646  19.419   7.908  1.00  1.00           C
ATOM    154  O   ALA B  31      39.744  18.636   7.577  1.00  1.00           O
ATOM    155  CB  ALA B  31      43.043  18.842   7.917  1.00  1.00           C
ATOM    156  N   ALA B  32      42.604  23.614   7.314  1.00  1.00           N
ATOM    157  CA  ALA B  32      42.066  23.134   6.032  1.00  1.00           C
ATOM    158  C   ALA B  32      41.501  21.722   6.199  1.00  1.00           C
ATOM    159  O   ALA B  32      40.386  21.423   5.746  1.00  1.00           O
ATOM    160  CB  ALA B  32      43.153  23.105   4.999  1.00  1.00           C
ATOM    161  N   ALA B  33      43.932  23.529   9.747  1.00  1.00           N
ATOM    162  CA  ALA B  33      42.642  24.226   9.627  1.00  1.00           C
ATOM    163  C   ALA B  33      41.876  23.699   8.411  1.00  1.00           C
ATOM    164  O   ALA B  33      40.677  23.393   8.496  1.00  1.00           O
ATOM    165  CB  ALA B  33      42.868  25.698   9.460  1.00  1.00           C
ATOM    166  N   ALA B  34      46.311  22.349   8.945  1.00  1.00           N
ATOM    167  CA  ALA B  34      45.474  21.714   9.973  1.00  1.00           C
ATOM    168  C   ALA B  34      44.034  22.219   9.861  1.00  1.00           C
ATOM    169  O   ALA B  34      43.077  21.430   9.882  1.00  1.00           O
ATOM    170  CB  ALA B  34      46.001  22.042  11.338  1.00  1.00           C
ATOM    171  N   ALA B  35      47.300  24.352   7.300  1.00  1.00           N
ATOM    172  CA  ALA B  35      47.057  23.003   6.767  1.00  1.00           C
ATOM    173  C   ALA B  35      46.053  22.263   7.654  1.00  1.00           C
ATOM    174  O   ALA B  35      45.095  21.650   7.159  1.00  1.00           O
ATOM    175  CB  ALA B  35      48.340  22.227   6.734  1.00  1.00           C
ATOM    176  N   ALA B  36      47.720  26.345   9.182  1.00  1.00           N
ATOM    177  CA  ALA B  36      46.819  26.575   8.044  1.00  1.00           C
ATOM    178  C   ALA B  36      46.336  25.237   7.480  1.00  1.00           C
ATOM    179  O   ALA B  36      45.138  25.045   7.229  1.00  1.00           O
ATOM    180  CB  ALA B  36      47.538  27.328   6.965  1.00  1.00           C
ATOM    181  N   ALA B  37      49.729  25.158  10.683  1.00  1.00           N
ATOM    182  CA  ALA B  37      48.462  25.553  11.316  1.00  1.00           C
ATOM    183  C   ALA B  37      47.363  25.667  10.257  1.00  1.00           C
ATOM    184  O   ALA B  37      46.249  25.154  10.436  1.00  1.00           O
ATOM    185  CB  ALA B  37      48.620  26.879  11.998  1.00  1.00           C
ATOM    186  N   ALA B  38      51.753  25.086   8.788  1.00  1.00           N
ATOM    187  CA  ALA B  38      51.272  23.845   9.412  1.00  1.00           C
ATOM    188  C   ALA B  38      49.865  24.053   9.975  1.00  1.00           C
ATOM    189  O   ALA B  38      48.963  23.229   9.761  1.00  1.00           O
ATOM    190  CB  ALA B  38      52.190  23.443  10.528  1.00  1.00           C
ATOM    191  N   ALA B  39      52.184  27.805   8.455  1.00  1.00           N
ATOM    192  CA  ALA B  39      51.796  26.968   7.311  1.00  1.00           C
ATOM    193  C   ALA B  39      51.114  25.691   7.805  1.00  1.00           C
ATOM    194  O   ALA B  39      50.053  25.297   7.297  1.00  1.00           O
ATOM    195  CB  ALA B  39      53.011  26.594   6.515  1.00  1.00           C
ATOM    196  N   ALA B  40      53.154  28.442  10.975  1.00  1.00           N
ATOM    197  CA  ALA B  40      51.947  29.100  10.454  1.00  1.00           C
ATOM    198  C   ALA B  40      51.320  28.245   9.350  1.00  1.00           C
ATOM    199  O   ALA B  40      50.103  28.012   9.338  1.00  1.00           O
ATOM    200  CB  ALA B  40      52.300  30.444   9.888  1.00  1.00           C
ATOM    201  N   ALA B  41      55.529  27.009  10.942  1.00  1.00           N
ATOM    202  CA  ALA B  41      54.514  26.744  11.971  1.00  1.00           C
ATOM    203  C   ALA B  41      53.144  27.228  11.493  1.00  1.00           C
ATOM    204  O   ALA B  41      52.139  26.509  11.602  1.00  1.00           O
ATOM    205  CB  ALA B  41      54.868  27.464  13.239  1.00  1.00           C
ATOM    206  N   ALA B  42      56.878  28.379   8.943  1.00  1.00           N
ATOM    207  CA  ALA B  42      56.615  26.940   8.811  1.00  1.00           C
ATOM    208  C   ALA B  42      55.447  26.536   9.713  1.00  1.00           C
ATOM    209  O   ALA B  42      54.525  25.825   9.285  1.00  1.00           O
ATOM    210  CB  ALA B  42      57.831  26.157   9.211  1.00  1.00           C
ATOM    211  N   ALA B  43      57.177  30.844  10.179  1.00  1.00           N
ATOM    212  CA  ALA B  43      56.461  30.735   8.900  1.00  1.00           C
ATOM    213  C   ALA B  43      55.966  29.302   8.698  1.00  1.00           C
ATOM    214  O   ALA B  43      54.803  29.074   8.335  1.00  1.00           O
ATOM    215  CB  ALA B  43      57.376  31.099   7.768  1.00  1.00           C
ATOM    216  N   ALA B  44      58.867  30.126  12.258  1.00  1.00           N
ATOM    217  CA  ALA B  44      57.557  30.730  12.539  1.00  1.00           C
ATOM    218  C   ALA B  44      56.626  30.542  11.340  1.00  1.00           C
ATOM    219  O   ALA B  44      55.464  30.137  11.491  1.00  1.00           O
ATOM    220  CB  ALA B  44      57.715  32.197  12.807  1.00  1.00           C
ATOM    221  N   ALA B  45      61.124  29.419  10.809  1.00  1.00           N
ATOM    222  CA  ALA B  45      60.474  28.444  11.695  1.00  1.00           C
ATOM    223  C   ALA B  45      59.020  28.852  11.946  1.00  1.00           C
ATOM    224  O   ALA B  45      58.100  28.028  11.854  1.00  1.00           O
ATOM    225  CB  ALA B  45      61.196  28.382  13.008  1.00  1.00           C
ATOM    226  N   ALA B  46      61.793  31.890   9.743  1.00  1.00           N
ATOM    227  CA  ALA B  46      61.508  30.752   8.859  1.00  1.00           C
ATOM    228  C   ALA B  46      60.672  29.708   9.602  1.00  1.00           C
ATOM    229  O   ALA B  46      59.667  29.205   9.081  1.00  1.00           O
ATOM    230  CB  ALA B  46      62.790  30.118   8.408  1.00  1.00           C
ATOM    231  N   ALA B  47      62.448  33.247  12.072  1.00  1.00           N
ATOM    232  CA  ALA B  47      61.376  33.745  11.197  1.00  1.00           C
ATOM    233  C   ALA B  47      60.848  32.608  10.320  1.00  1.00           C
ATOM    234  O   ALA B  47      59.629  32.415  10.191  1.00  1.00           O
ATOM    235  CB  ALA B  47      61.900  34.838  10.314  1.00  1.00           C
ATOM    236  N   ALA B  48      64.694  31.813  12.839  1.00  1.00           N
ATOM    237  CA  ALA B  48      63.530  31.905  13.731  1.00  1.00           C
ATOM    238  C   ALA B  48      62.278  32.254  12.923  1.00  1.00           C
ATOM    239  O   ALA B  48      61.218  31.630  13.087  1.00  1.00           O
ATOM    240  CB  ALA B  48      63.758  32.971  14.761  1.00  1.00           C
ATOM    241  N   ALA B  49      66.403  32.463  10.752  1.00  1.00           N
ATOM    242  CA  ALA B  49      66.058  31.060  11.021  1.00  1.00           C
ATOM    243  C   ALA B  49      64.749  30.985  11.811  1.00  1.00           C
ATOM    244  O   ALA B  49      63.847  30.202  11.480  1.00  1.00           O
ATOM    245  CB  ALA B  49      67.146  30.408  11.820  1.00  1.00           C
ATOM    246  N   ALA B  50      66.706  35.180  11.219  1.00  1.00           N
ATOM    247  CA  ALA B  50      66.169  34.701   9.938  1.00  1.00           C
ATOM    248  C   ALA B  50      65.603  33.289  10.103  1.00  1.00           C
ATOM    249  O   ALA B  50      64.489  32.990   9.651  1.00  1.00           O
ATOM    250  CB  ALA B  50      67.254  34.673   8.904  1.00  1.00           C
ATOM    251  N   ALA B  51      68.035  35.094  13.653  1.00  1.00           N
ATOM    252  CA  ALA B  51      66.746  35.790  13.533  1.00  1.00           C
ATOM    253  C   ALA B  51      65.979  35.265  12.318  1.00  1.00           C
ATOM    254  O   ALA B  51      64.780  34.958  12.403  1.00  1.00           O
ATOM    255  CB  ALA B  51      66.970  37.263  13.368  1.00  1.00           C
ATOM    256  N   ALA B  52      70.414  33.915  12.849  1.00  1.00           N
ATOM    257  CA  ALA B  52      69.577  33.278  13.877  1.00  1.00           C
ATOM    258  C   ALA B  52      68.137  33.783  13.766  1.00  1.00           C
ATOM    259  O   ALA B  52      67.181  32.995  13.785  1.00  1.00           O
ATOM    260  CB  ALA B  52      70.105  33.606  15.243  1.00  1.00           C
ATOM    261  N   ALA B  53      71.402  35.919  11.205  1.00  1.00           N
ATOM    262  CA  ALA B  53      71.160  34.570  10.671  1.00  1.00           C
ATOM    263  C   ALA B  53      70.155  33.830  11.557  1.00  1.00           C
ATOM    264  O   ALA B  53      69.198  33.217  11.063  1.00  1.00           O
ATOM    265  CB  ALA B  53      72.443  33.795  10.637  1.00  1.00           C
ATOM    266  N   ALA B  54      71.823  37.910  13.089  1.00  1.00           N
ATOM    267  CA  ALA B  54      70.922  38.141  11.951  1.00  1.00           C
ATOM    268  C   ALA B  54      70.439  36.803  11.385  1.00  1.00           C
ATOM    269  O   ALA B  54      69.240  36.612  11.135  1.00  1.00           O
ATOM    270  CB  ALA B  54      71.640  38.895  10.872  1.00  1.00           C
ATOM    271  N   ALA B  55      73.833  36.723  14.587  1.00  1.00           N
ATOM    272  CA  ALA B  55      72.565  37.117  15.221  1.00  1.00           C
ATOM    273  C   ALA B  55      71.466  37.233  14.163  1.00  1.00           C
ATOM    274  O   ALA B  55      70.352  36.718  14.342  1.00  1.00           O
ATOM    275  CB  ALA B  55      72.724  38.443  15.905  1.00  1.00           C
ATOM    276  N   ALA B  56      75.856  36.653  12.692  1.00  1.00           N
ATOM    277  CA  ALA B  56      75.376  35.411  13.314  1.00  1.00           C
ATOM    278  C   ALA B  56      73.969  35.618  13.879  1.00  1.00           C
ATOM    279  O   ALA B  56      73.068  34.795  13.665  1.00  1.00           O
ATOM    280  CB  ALA B  56      76.294  35.008  14.430  1.00  1.00           C
ATOM    281  N   ALA B  57      76.288  39.372  12.360  1.00  1.00           N
ATOM    282  CA  ALA B  57      75.899  38.535  11.216  1.00  1.00           C
ATOM    283  C   ALA B  57      75.216  37.259  11.710  1.00  1.00           C
ATOM    284  O   ALA B  57      74.155  36.864  11.202  1.00  1.00           O
ATOM    285  CB  ALA B  57      77.113  38.162  10.419  1.00  1.00           C
ATOM    286  N   ALA B  58      77.257  40.007  14.881  1.00  1.00           N
ATOM    287  CA  ALA B  58      76.050  40.665  14.361  1.00  1.00           C
ATOM    288  C   ALA B  58      75.423  39.811  13.257  1.00  1.00           C
ATOM    289  O   ALA B  58      74.205  39.577  13.244  1.00  1.00           O
ATOM    290  CB  ALA B  58      76.402  42.010  13.796  1.00  1.00           C
ATOM    291  N   ALA B  59      79.632  38.575  14.846  1.00  1.00           N
ATOM    292  CA  ALA B  59      78.618  38.308  15.876  1.00  1.00           C
ATOM    293  C   ALA B  59      77.248  38.792  15.398  1.00  1.00           C
ATOM    294  O   ALA B  59      76.243  38.074  15.506  1.00  1.00           O
ATOM    295  CB  ALA B  59      78.973  39.027  17.144  1.00  1.00           C
ATOM    296  N   ALA B  60      80.980  39.946  12.847  1.00  1.00           N
ATOM    297  CA  ALA B  60      80.718  38.506  12.715  1.00  1.00           C
ATOM    298  C   ALA B  60      79.550  38.102  13.617  1.00  1.00           C
ATOM    299  O   ALA B  60      78.629  37.392  13.188  1.00  1.00           O
ATOM    300  CB  ALA B  60      81.934  37.724  13.113  1.00  1.00           C
ATOM    301  N   ALA B  61      81.280  42.410  14.085  1.00  1.00           N
ATOM    302  CA  ALA B  61      80.564  42.302  12.806  1.00  1.00           C
ATOM    303  C   ALA B  61      80.069  40.869  12.603  1.00  1.00           C
ATOM    304  O   ALA B  61      78.905  40.640  12.240  1.00  1.00           O
ATOM    305  CB  ALA B  61      81.477  42.667  11.674  1.00  1.00           C
ATOM    306  N   ALA B  62      82.971  41.691  16.163  1.00  1.00           N
ATOM    307  CA  ALA B  62      81.661  42.294  16.445  1.00  1.00           C
ATOM    308  C   ALA B  62      80.729  42.106  15.246  1.00  1.00           C
ATOM    309  O   ALA B  62      79.567  41.703  15.397  1.00  1.00           O
ATOM    310  CB  ALA B  62      81.819  43.762  16.714  1.00  1.00           C
ATOM    311  N   ALA B  63      85.228  40.985  14.712  1.00  1.00           N
ATOM    312  CA  ALA B  63      84.577  40.009  15.599  1.00  1.00           C
ATOM    313  C   ALA B  63      83.124  40.418  15.850  1.00  1.00           C
ATOM    314  O   ALA B  63      82.203  39.592  15.758  1.00  1.00           O
ATOM    315  CB  ALA B  63      85.300  39.946  16.911  1.00  1.00           C
ATOM    316  N   ALA B  64      85.896  43.458  13.648  1.00  1.00           N
ATOM    317  CA  ALA B  64      85.610  42.319  12.763  1.00  1.00           C
ATOM    318  C   ALA B  64      84.775  41.275  13.507  1.00  1.00           C
ATOM    319  O   ALA B  64      83.769  40.771  12.984  1.00  1.00           O
ATOM    320  CB  ALA B  64      86.893  41.685  12.312  1.00  1.00           C
ATOM    321  N   ALA B  65      86.551  44.813  15.978  1.00  1.00           N
ATOM    322  CA  ALA B  65      85.479  45.311  15.104  1.00  1.00           C
ATOM    323  C   ALA B  65      84.950  44.174  14.226  1.00  1.00           C
ATOM    324  O   ALA B  65      83.732  43.981  14.096  1.00  1.00           O
ATOM    325  CB  ALA B  65      86.001  46.405  14.222  1.00  1.00           C
ATOM    326  N   ALA B  66      88.798  43.378  16.742  1.00  1.00           N
ATOM    327  CA  ALA B  66      87.635  43.469  17.635  1.00  1.00           C
ATOM    328  C   ALA B  66      86.381  43.818  16.829  1.00  1.00           C
ATOM    329  O   ALA B  66      85.322  43.194  16.993  1.00  1.00           O
ATOM    330  CB  ALA B  66      87.862  44.535  18.667  1.00  1.00           C
ATOM    331  N   ALA B  67      90.506  44.029  14.656  1.00  1.00           N
ATOM    332  CA  ALA B  67      90.160  42.626  14.924  1.00  1.00           C
ATOM    333  C   ALA B  67      88.852  42.551  15.715  1.00  1.00           C
ATOM    334  O   ALA B  67      87.951  41.768  15.384  1.00  1.00           O
ATOM    335  CB  ALA B  67      91.250  41.973  15.722  1.00  1.00           C
ATOM    336  N   ALA B  68      90.809  46.747  15.126  1.00  1.00           N
ATOM    337  CA  ALA B  68      90.270  46.268  13.844  1.00  1.00           C
ATOM    338  C   ALA B  68      89.706  44.855  14.008  1.00  1.00           C
ATOM    339  O   ALA B  68      88.590  44.557  13.556  1.00  1.00           O
ATOM    340  CB  ALA B  68      91.356  46.241  12.809  1.00  1.00           C
ATOM    341  N   ALA B  69      92.139  46.659  17.557  1.00  1.00           N
ATOM    342  CA  ALA B  69      90.849  47.354  17.440  1.00  1.00           C
ATOM    343  C   ALA B  69      90.082  46.830  16.224  1.00  1.00           C
ATOM    344  O   ALA B  69      88.883  46.523  16.310  1.00  1.00           O
ATOM    345  CB  ALA B  69      91.075  48.828  17.275  1.00  1.00           C
ATOM    346  N   ALA B  70      94.517  45.481  16.753  1.00  1.00           N
ATOM    347  CA  ALA B  70      93.681  44.843  17.780  1.00  1.00           C
ATOM    348  C   ALA B  70      92.241  45.348  17.670  1.00  1.00           C
ATOM    349  O   ALA B  70      91.285  44.559  17.689  1.00  1.00           O
ATOM    350  CB  ALA B  70      94.209  45.170  19.146  1.00  1.00           C
"""

frequent_folds = {"beta_ud_1": """
ATOM      1  N   LEU A   1      32.005   8.728  15.610  1.00 25.00           N
ATOM      2  CA  LEU A   1      31.411   9.940  15.068  1.00 25.00           C
ATOM      3  C   LEU A   1      30.958   9.691  13.641  1.00 25.00           C
ATOM      4  O   LEU A   1      31.734   9.166  12.832  1.00 25.00           O
ATOM      5  CB  LEU A   1      32.451  11.072  15.071  1.00 25.00           C
ATOM      6  N   THR A   2      29.714  10.066  13.330  1.00 25.00           N
ATOM      7  CA  THR A   2      29.211   9.987  11.955  1.00 25.00           C
ATOM      8  C   THR A   2      28.408  11.239  11.586  1.00 25.00           C
ATOM      9  O   THR A   2      27.709  11.827  12.418  1.00 25.00           O
ATOM     10  CB  THR A   2      28.340   8.702  11.697  1.00 25.00           C
ATOM     11  N   ILE A   3      28.532  11.632  10.321  1.00 25.00           N
ATOM     12  CA  ILE A   3      27.809  12.767   9.776  1.00 25.00           C
ATOM     13  C   ILE A   3      27.010  12.326   8.557  1.00 25.00           C
ATOM     14  O   ILE A   3      27.496  11.574   7.724  1.00 25.00           O
ATOM     15  CB  ILE A   3      28.746  13.943   9.429  1.00 25.00           C
ATOM     16  N   PHE A   4      25.763  12.787   8.505  1.00 25.00           N
ATOM     17  CA  PHE A   4      24.830  12.491   7.446  1.00 25.00           C
ATOM     18  C   PHE A   4      24.318  13.757   6.776  1.00 25.00           C
ATOM     19  O   PHE A   4      24.002  14.742   7.443  1.00 25.00           O
ATOM     20  CB  PHE A   4      23.637  11.717   8.002  1.00 25.00           C
ATOM     21  N   ALA A  15      23.027  15.851  10.003  1.00 25.00           N
ATOM     22  CA  ALA A  15      22.911  15.169  11.299  1.00 25.00           C
ATOM     23  C   ALA A  15      24.276  14.675  11.740  1.00 25.00           C
ATOM     24  O   ALA A  15      25.062  14.217  10.923  1.00 25.00           O
ATOM     25  CB  ALA A  15      21.930  13.987  11.215  1.00 25.00           C
ATOM     26  N   VAL A  16      24.548  14.778  13.037  1.00 25.00           N
ATOM     27  CA  VAL A  16      25.767  14.268  13.642  1.00 25.00           C
ATOM     28  C   VAL A  16      25.377  13.261  14.709  1.00 25.00           C
ATOM     29  O   VAL A  16      24.485  13.526  15.540  1.00 25.00           O
ATOM     30  CB  VAL A  16      26.598  15.403  14.263  1.00 25.00           C
ATOM     31  N   ARG A  17      26.001  12.093  14.672  1.00 25.00           N
ATOM     32  CA  ARG A  17      25.747  11.072  15.689  1.00 25.00           C
ATOM     33  C   ARG A  17      27.043  10.812  16.434  1.00 25.00           C
ATOM     34  O   ARG A  17      28.088  10.652  15.803  1.00 25.00           O
ATOM     35  CB  ARG A  17      25.232   9.768  15.087  1.00 25.00           C
ATOM     36  N   ILE A  18      26.950  10.774  17.767  1.00 25.00           N
ATOM     37  CA  ILE A  18      28.091  10.564  18.635  1.00 25.00           C
ATOM     38  C   ILE A  18      27.757   9.329  19.464  1.00 25.00           C
ATOM     39  O   ILE A  18      26.885   9.375  20.351  1.00 25.00           O
ATOM     40  CB  ILE A  18      28.346  11.793  19.553  1.00 25.00           C
""", "beta_ud_16": """
ATOM      1  CA  CYS C 217      31.136   9.930   6.588  1.00 25.00           C
ATOM      2  C   CYS C 217      30.021  10.337   5.603  1.00 25.00           C
ATOM      3  O   CYS C 217      30.293  10.470   4.397  1.00 25.00           O
ATOM      4  N   CYS C 217      31.707   8.684   6.106  1.00 25.00           N
ATOM      5  CB  CYS C 217      32.194  11.005   6.592  1.00 25.00           C
ATOM      6  CA  LEU C 218      27.685  10.944   5.240  1.00 25.00           C
ATOM      7  C   LEU C 218      27.260  12.404   5.494  1.00 25.00           C
ATOM      8  O   LEU C 218      27.226  12.857   6.658  1.00 25.00           O
ATOM      9  N   LEU C 218      28.801  10.573   6.102  1.00 25.00           N
ATOM     10  CB  LEU C 218      26.533   9.983   5.502  1.00 25.00           C
ATOM     11  CA  SER C 219      26.460  14.512   4.588  1.00 25.00           C
ATOM     12  C   SER C 219      25.458  14.856   3.498  1.00 25.00           C
ATOM     13  O   SER C 219      25.455  14.276   2.404  1.00 25.00           O
ATOM     14  N   SER C 219      27.007  13.159   4.431  1.00 25.00           N
ATOM     15  CB  SER C 219      27.525  15.605   4.656  1.00 25.00           C
ATOM     16  CA  VAL C 220      23.589  16.270   2.878  1.00 25.00           C
ATOM     17  C   VAL C 220      24.301  17.420   2.109  1.00 25.00           C
ATOM     18  O   VAL C 220      24.201  18.572   2.478  1.00 25.00           O
ATOM     19  N   VAL C 220      24.557  15.774   3.835  1.00 25.00           N
ATOM     20  CB  VAL C 220      22.290  16.740   3.571  1.00 25.00           C
ATOM     21  CA  LEU C 245      21.808  15.489   9.168  1.00 25.00           C
ATOM     22  C   LEU C 245      22.196  15.942  10.540  1.00 25.00           C
ATOM     23  O   LEU C 245      23.046  16.818  10.702  1.00 25.00           O
ATOM     24  N   LEU C 245      21.810  16.577   8.215  1.00 25.00           N
ATOM     25  CB  LEU C 245      22.814  14.401   8.821  1.00 25.00           C
ATOM     26  CA  LYS C 246      22.033  15.452  12.888  1.00 25.00           C
ATOM     27  C   LYS C 246      23.410  14.790  12.928  1.00 25.00           C
ATOM     28  O   LYS C 246      23.678  13.869  12.179  1.00 25.00           O
ATOM     29  N   LYS C 246      21.554  15.342  11.530  1.00 25.00           N
ATOM     30  CB  LYS C 246      21.111  14.687  13.843  1.00 25.00           C
ATOM     31  CA  ARG C 247      25.555  14.598  13.972  1.00 25.00           C
ATOM     32  C   ARG C 247      25.380  13.260  14.702  1.00 25.00           C
ATOM     33  O   ARG C 247      24.827  13.237  15.801  1.00 25.00           O
ATOM     34  N   ARG C 247      24.259  15.217  13.849  1.00 25.00           N
ATOM     35  CB  ARG C 247      26.513  15.466  14.750  1.00 25.00           C
ATOM     36  CA  PHE C 248      25.757  10.848  14.722  1.00 25.00           C
ATOM     37  C   PHE C 248      26.903   9.952  14.305  1.00 25.00           C
ATOM     38  O   PHE C 248      27.652  10.263  13.387  1.00 25.00           O
ATOM     39  N   PHE C 248      25.875  12.166  14.116  1.00 25.00           N
ATOM     40  CB  PHE C 248      24.439  10.174  14.324  1.00 25.00           C
""", "beta_ud_18": """
ATOM      1  CA  LEU B 100      21.770  19.029  10.617  1.00 25.00           C
ATOM      2  C   LEU B 100      21.943  18.482  12.021  1.00 25.00           C
ATOM      3  O   LEU B 100      22.073  19.241  12.981  1.00 25.00           O
ATOM      4  N   LEU B 100      20.695  20.016  10.562  1.00 25.00           N
ATOM      5  CB  LEU B 100      23.094  19.633  10.138  1.00 25.00           C
ATOM      6  CA  PHE B 101      22.140  16.489  13.412  1.00 25.00           C
ATOM      7  C   PHE B 101      23.310  15.508  13.328  1.00 25.00           C
ATOM      8  O   PHE B 101      23.426  14.744  12.370  1.00 25.00           O
ATOM      9  N   PHE B 101      21.950  17.158  12.132  1.00 25.00           N
ATOM     10  CB  PHE B 101      20.856  15.768  13.835  1.00 25.00           C
ATOM     11  CA  LYS B 102      25.382  14.722  14.302  1.00 25.00           C
ATOM     12  C   LYS B 102      25.418  13.774  15.495  1.00 25.00           C
ATOM     13  O   LYS B 102      25.414  14.211  16.648  1.00 25.00           O
ATOM     14  N   LYS B 102      24.183  15.544  14.328  1.00 25.00           N
ATOM     15  CB  LYS B 102      26.636  15.603  14.278  1.00 25.00           C
ATOM     16  CA  GLU B 103      25.550  11.477  16.270  1.00 25.00           C
ATOM     17  C   GLU B 103      26.830  10.656  16.114  1.00 25.00           C
ATOM     18  O   GLU B 103      27.195  10.268  15.005  1.00 25.00           O
ATOM     19  N   GLU B 103      25.443  12.475  15.214  1.00 25.00           N
ATOM     20  CB  GLU B 103      24.304  10.587  16.302  1.00 25.00           C
ATOM     21  CA  GLY B 164      34.242   8.965   4.114  1.00 25.00           C
ATOM     22  C   GLY B 164      33.256   9.209   5.242  1.00 25.00           C
ATOM     23  O   GLY B 164      33.373   8.613   6.315  1.00 25.00           O
ATOM     24  N   GLY B 164      34.073   9.863   2.983  1.00 25.00           N
ATOM     25  CA  SER B 165      31.273  10.418   6.011  1.00 25.00           C
ATOM     26  C   SER B 165      29.897   9.854   5.647  1.00 25.00           C
ATOM     27  O   SER B 165      29.400  10.086   4.542  1.00 25.00           O
ATOM     28  N   SER B 165      32.289  10.094   5.010  1.00 25.00           N
ATOM     29  CB  SER B 165      31.171  11.935   6.217  1.00 25.00           C
ATOM     30  CA  PRO B 166      27.886   8.689   6.386  1.00 25.00           C
ATOM     31  C   PRO B 166      26.941   9.888   6.473  1.00 25.00           C
ATOM     32  O   PRO B 166      27.037  10.689   7.405  1.00 25.00           O
ATOM     33  N   PRO B 166      29.285   9.092   6.567  1.00 25.00           N
ATOM     34  CB  PRO B 166      27.636   7.746   7.568  1.00 25.00           C
ATOM     35  CA  PHE B 167      25.010  11.035   5.484  1.00 25.00           C
ATOM     36  C   PHE B 167      23.633  10.399   5.302  1.00 25.00           C
ATOM     37  O   PHE B 167      23.417   9.621   4.368  1.00 25.00           O
ATOM     38  N   PHE B 167      26.036   9.995   5.505  1.00 25.00           N
ATOM     39  CB  PHE B 167      25.269  12.026   4.345  1.00 25.00           C
""", "beta_ud_11": """
ATOM      1  CA  ARG B 412      20.699  14.262  15.889  1.00 25.00           C
ATOM      2  C   ARG B 412      22.001  14.446  15.140  1.00 25.00           C
ATOM      3  O   ARG B 412      22.014  15.054  14.047  1.00 25.00           O
ATOM      4  N   ARG B 412      20.141  15.593  16.123  1.00 25.00           N
ATOM      5  CB  ARG B 412      19.783  13.406  15.049  1.00 25.00           C
ATOM      6  CA  ILE B 413      24.438  13.942  15.157  1.00 25.00           C
ATOM      7  C   ILE B 413      24.835  12.514  14.864  1.00 25.00           C
ATOM      8  O   ILE B 413      24.518  11.607  15.643  1.00 25.00           O
ATOM      9  N   ILE B 413      23.078  13.939  15.738  1.00 25.00           N
ATOM     10  CB  ILE B 413      25.519  14.472  16.130  1.00 25.00           C
ATOM     11  CA  TYR B 414      26.060  11.034  13.330  1.00 25.00           C
ATOM     12  C   TYR B 414      27.596  11.051  13.189  1.00 25.00           C
ATOM     13  O   TYR B 414      28.153  11.967  12.616  1.00 25.00           O
ATOM     14  N   TYR B 414      25.565  12.336  13.755  1.00 25.00           N
ATOM     15  CB  TYR B 414      25.371  10.600  12.023  1.00 25.00           C
ATOM     16  CA  ALA B 415      29.695   9.877  13.528  1.00 25.00           C
ATOM     17  C   ALA B 415      30.035   8.412  13.599  1.00 25.00           C
ATOM     18  O   ALA B 415      29.138   7.588  13.703  1.00 25.00           O
ATOM     19  N   ALA B 415      28.259  10.016  13.688  1.00 25.00           N
ATOM     20  CB  ALA B 415      30.439  10.668  14.597  1.00 25.00           C
ATOM     21  CA  THR B 436      33.347   7.141   5.385  1.00 25.00           C
ATOM     22  C   THR B 436      32.880   8.576   5.569  1.00 25.00           C
ATOM     23  O   THR B 436      32.845   9.092   6.691  1.00 25.00           O
ATOM     24  N   THR B 436      34.408   6.804   6.307  1.00 25.00           N
ATOM     25  CB  THR B 436      32.106   6.236   5.569  1.00 25.00           C
ATOM     26  CA  GLY B 437      31.766  10.431   4.476  1.00 25.00           C
ATOM     27  C   GLY B 437      30.381  10.087   5.001  1.00 25.00           C
ATOM     28  O   GLY B 437      29.959   8.943   4.934  1.00 25.00           O
ATOM     29  N   GLY B 437      32.541   9.206   4.455  1.00 25.00           N
ATOM     30  CA  ILE B 438      28.340  10.927   6.084  1.00 25.00           C
ATOM     31  C   ILE B 438      27.511  12.184   5.774  1.00 25.00           C
ATOM     32  O   ILE B 438      27.874  13.287   6.192  1.00 25.00           O
ATOM     33  N   ILE B 438      29.703  11.084   5.565  1.00 25.00           N
ATOM     34  CB  ILE B 438      28.283  10.756   7.618  1.00 25.00           C
ATOM     35  CA  GLY B 439      25.450  13.067   4.757  1.00 25.00           C
ATOM     36  C   GLY B 439      24.131  12.779   5.454  1.00 25.00           C
ATOM     37  O   GLY B 439      23.795  11.625   5.706  1.00 25.00           O
ATOM     38  N   GLY B 439      26.386  11.989   5.064  1.00 25.00           N
"""}
