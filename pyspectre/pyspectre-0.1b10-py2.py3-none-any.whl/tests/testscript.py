from PySpectre import PySpectre
from matplotlib import pyplot as plt
with PySpectre('$lib/shell/labcomp.cadence.cshrc', 'input.scs', '-log') as sim:

    result = sim.getdc()
    dcstate = sim.readStateFile(sim.dcsolution)

    sim.sclSetInstanceParameterValue("V0", "file", "vin1.6.pwl")
    newstate = 'FC.one'
    sim.transtep(sim.dcsolution, '0', '5e-5', '5e-8', newstate)
    time, wave1, names1 = sim.readwave(sim.simdir+'/'+'input.raw', "Transient", signames=['vin'])


    newstate = 'FC.two'
    sim.sclSetResultDir('')
    sim.sclSetInstanceParameterValue("V0", "file", "vin1.7.pwl")
    sim.transtep(sim.dcsolution, '0', '5e-5', '5e-8', newstate)
    time, wave2, names2 = sim.readwave(sim.simdir + '/' + 'input.raw', "Transient", signames=['vin'])

    diffmat = wave2-wave1


    plt.plot(time, wave1)
    plt.plot(time, wave2)
    plt.show()
    eight = 9.01