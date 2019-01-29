import oscars.sr
from oscars.plots_mpl import *
osr = oscars.sr.sr(nthreads=10)

osr.set_particle_beam(beam='NSLSII', x0=[0, 0, -1], energy_GeV=3, ctstartstop=[-1, 1.1])
#osr.set_npoints_trajectory(5)

osr.clear_bfields()
osr.clear_efields()
#osr.add_bfield_undulator(bfield=[0, 0.367703346377074, 0], period=[0, 0, 0.042], nperiods=31)
#osr.add_bfield_gaussian(bfield=[0, 1, 0], sigma=[0, 0, 0.05])
#osr.add_bfield_uniform(bfield=[0, 1, 0], width=[0, 0, 1])
#osr.add_efield_uniform(efield=[0, 0, +1e9], width=[0, 0, 1], translation=[0, 0, -0.5])
#osr.add_efield_uniform(efield=[0, 0, -1e9], width=[0, 0, 1], translation=[0, 0, +0.5])
osr.add_efield_uniform(efield=[0, 0, +2e17], )



#osr.set_new_particle()
trajectory = osr.calculate_trajectory()
#plot_trajectory_position(trajectory)
plot_trajectory_velocity(trajectory)

for p in trajectory:
    print(p)
