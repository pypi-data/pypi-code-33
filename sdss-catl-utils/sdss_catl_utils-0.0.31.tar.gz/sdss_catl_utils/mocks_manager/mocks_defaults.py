"""

Module expressing various default settings of the synthetic catalogues
manager sub-package.

All values hard-coded here appear as unique variables throughout the
entire SDSS_Catl_Utils code base. This allows you to customize your
default settings and be guaranteed that whatever changes you make
will correctly propagate to all relevant behaviour. See the in-line
comments in the ``sdss_catl_utils/mocks_manager_mocks_defaults.py``
source code for descriptions of the purpose of each variable defined
in this module.

"""

# Set the default argument for the ``CachedHaloCatalogue`` class.
# Any combination of parameters may be chosen, provided that the selected
# combinations corresponds to a catalog or set of catalogues in
# your cache directory. These choices dictate any behavior that loads an
# unspecified CachedHaloCatalog into memory.

environ_name = 'sdss_catl_path'
catl_kind    = 'mocks'
hod_n        = 0
halotype     = 'fof'
clf_method   = 1
sigma_clf_c  = 0.1417
clf_seed     = 1235
dv           = 1.
sample       = '19'
type_am      = 'mr'
cosmo_choice = 'LasDamas'
perf_opt     = False
remove_files = False

# This is related to the web addresses, at which the catalogues are stored.
sdss_catl_url = 'http://lss.phy.vanderbilt.edu/groups/data_vc/DR7/sdss_catalogues/'