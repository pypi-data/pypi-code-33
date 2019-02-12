import sys
import numpy as np

sys.path.append("../")

from workspace_jam.plotting.density_rj_lens_plots import density_plot_tools

slacs = density_plot_tools.SLACS()

image_dir = '/gpfs/data/pdtw24/PL_Data/RJLens3/'  # Dir of Object to make evidence tables from
image_name = 'RJLens2'

number_bins = 50

## SIE ##

values = []
values.append(0.05247720) # Lens x
values.append(0.03497244) # Lens y
values.append(1.91716393) # Lens einR
values.append(0.68532604) # Lens axis ratio
values.append(66.83060729) # Lens phi

slacs.density_vs_radii_sie(radius_kpc=15.0, values=values, number_bins=number_bins)

### Decomposed Aligned model ###

values = []
values.append(0.02191929) # fg 1 x
values.append(0.02982811) # fg 1 y
values.append(0.19665282) # fg 1 intensity
values.append(0.55871552) # fg 1 eff rad
values.append(1.39390583) # fg 1 sersic inex
values.append(0.83443597) # fg 1 axis ratio
values.append(66.48069170)  # fg 1 phi
values.append(0.03447566) # fg 2 intensity
values.append(4.52134788) # fg 2 effective radius
values.append(0.61310712) # fg 2 axis ratio
values.append(66.48069170) # fg 2 phi
values.append(0.04173277) # Lens Kappa s
values.append(2.71727396) # Lens MLR 1
values.append(5.67223821) # Lens MLR 2

slacs.density_vs_radii_ltm2(radius_kpc=10.0, values=values, center_skip=0, ltm_skip=1, number_bins=number_bins)
slacs.plot_density(image_name=image_name, labels=['SIE', 'Sersic', 'Exponential', 'NFWSph'])
stop

### Decomposed Mis aligned model ###

center_skip = 2
ltm_skip = 1

values = []
values.append(0.01380383) # fg 1 x
values.append(0.03510592) # fg 1 y
values.append(0.19135611) # fg 1 intensity
values.append(0.55945899) # fg 1 eff rad
values.append(1.43299142) # fg 1 sersic inex
values.append(0.85502919) # fg 1 axis ratio
values.append(74.60100155) # fg 1 phi
values.append(0.10819032) # fg 2 x
values.append(0.08230147) # fg 2 y
values.append(0.03438241) # fg 2 intensity
values.append(4.54764602) # fg 2 effective radius
values.append(0.60003029) # fg 2 axis ratio
values.append(65.68756046) # fg 2 phi
values.append(0.03259209) # Lens Kappa s
values.append(5.74923698) # Lens MLR 1
values.append(4.24770722) # Lens MLR 2

### Decomposed Mis aligned model + Rad Grad Disk ###

center_skip = 2
ltm_skip = 1

values.append(0.01429371) # fg 1 x
values.append(0.03482821) # fg 1 y
values.append(0.19719856) # fg 1 intensity
values.append(0.54707512) # fg 1 eff rad
values.append(1.40547183) # fg 1 sersic inex
values.append(0.84835895) # fg 1 axis ratio
values.append(73.97940933) # fg 1 phi
values.append(0.10119909) # fg 2 x
values.append(0.08338715) # fg 2 y
values.append(0.03513022) # fg 2 intensity
values.append(4.47678502) # fg 2 effective radius
values.append(0.61034664) # fg 2 axis ratio
values.append(65.64533590) # fg 2 phi
values.append(0.02625320) # Lens Kappa s
values.append(6.14116954) # Lens MLR 1
values.append(4.95553279) # Lens MLR 2
values.append(-0.08614826) # Lens Grad

### Decomposed Mis aligned model + Rad Grad Bulge ###

center_skip = 2
ltm_skip = 1

values.append(0.01300042) # fg 1 x
values.append(0.03453442) # fg 1 y
values.append(0.19670260) # fg 1 intensity
values.append(0.55118863) # fg 1 eff rad
values.append(1.40642531) # fg 1 sersic inex
values.append(0.84719873) # fg 1 phi
values.append(73.92584618) # fg 1 axis ratio
values.append(0.10759716) # fg 2 x
values.append(0.08800376) # fg 2 y
values.append(0.03472421) # fg 2 intensity
values.append(4.54293160) # fg 2 effective radius
values.append(0.60543107) # fg 2 axis ratio
values.append(65.72225231) # fg 2 phi
values.append(0.02924493) # Lens Kappa s
values.append(4.80753942) # Lens MLR 1
values.append(4.64606376) # Lens MLR 2
values.append(0.17415334) # Lens Grad

### Decomposed Mis aligned model + BLACK HOLE###

center_skip = 2
ltm_skip = 1

values = []
values.append(0.01325835) # fg 1 x
values.append(0.03141879) # fg 1 y
values.append(0.19499256) # fg 1 intensity
values.append(0.55633797) # fg 1 eff rad
values.append(1.44111989) # fg 1 sersic inex
values.append(0.84441063) # fg 1 phi
values.append(72.90899614) # fg 1 axis ratio
values.append(0.10100496) # fg 2 x
values.append(0.08702267) # fg 2 y
values.append(0.03422805) # fg 2 intensity
values.append(4.56848742) # fg 2 effective radius
values.append(0.60149254) # fg 2 axis ratio
values.append(66.08021533) # fg 2 phi
values.append(0.05117416) # Lens Kappa s
values.append(2.25135624) # Lens MLR 1
values.append(4.87657708) # Lens MLR 2
values.append(0.40273428) # Lens Black hole EinR

slacs = density_plot_tools.SLACS(image_dir, image_name)

# model_indexes, sample_weights, total_masses, stellar_masses, bulge_masses, disk_masses, dark_masses = \
#      slacs.masses_of_all_samples(radius_kpc=10.0)