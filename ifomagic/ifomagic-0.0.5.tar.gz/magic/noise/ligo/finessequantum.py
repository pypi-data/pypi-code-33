'''
FINESSE quantum noise curve for Voyager.
Code copied from detectors.LIGO data files by Daniel Brown.
This should be modified by somebody who understands Finesse more than I do.

MAGIC
@author: Isobel and Roshni
'''
import pykat
from pykat import finesse
from pykat.commands import *
import matplotlib.pyplot as plt
from magic.noise import NoiseParent
from copy import deepcopy
from magic import constants


class FinesseQuantumNoise(NoiseParent):

    def getNoise(self):
        return self.quantum()

        # Filter cavity parameters
    def fc_param(self, gamma_f, det, L):
        # gamma_f: 0.5 *FWHM
        # det: detuning in delta_omega
        FSR = constants.c / (2.0 * L)
        Fd = FSR/gamma_f
        
        phi = det/FSR*180.0
        # 2*pi*gamma_f/FSR = T/2 for lossless FC with T<<1
        T = 2.0 / Fd * 2 * np.pi
        return phi, T

    def quantum(self):

        kat = finesse.kat()

        # Return the output of the kat file if provided
        if self.ifo.kat_file is not None:
            kat.load(self.ifo.kat_file)
            return kat.run()['NSR_with_RP']

        params = deepcopy(self.ifo.parameters)
        det= 36
        phi, T = self.fc_param(det,-det, params['squeezer_filter_cavity_l'])
        # set T=1.0 to bypass filter cavity
        params['T_fc'] = T
        params['phi_fc'] = phi

        args = '''

lambda {lam}

l l1 {Pin} 0 0 nin
s s1 0 nin nprc1

# Power recycling mirror
m1 prm {prmT} {lossM} 90 nprc1 nprc2
s  prc {lprc} nprc2 nbsin

# Central beamsplitter
bs1 bs {bsT} {lossBS} 0 45 nbsin n0y n0x nbsout

# X-arm
s ichx {lmichx} n0x n1x
m1 itmx {itmT} {lossM} 90 n1x n2x
s armx {Larm} n2x n3x
m1 etmx {etmT} {lossM} 89.999875 n3x n4x
attr itmx mass {Mtm} zmech sus1
attr etmx mass {Mtm} zmech sus1

# Y-arm
s  ichy {lmichy} n0y n1y
m1 itmy {itmT} {lossM} {michy_phi} n1y n2y
s  army {Larm} n2y n3y
m1 etmy {etmT} {lossM} 0.000125  n3y n4y
attr itmy mass {Mtm} zmech sus1
attr etmy mass {Mtm} zmech sus1

# Signal recycling mirror
s  src {lsrc} nbsout nsrc1
m1 srm {srmT} {lossSRC} {srm_phi} nsrc1 nsrc2
s sout1 0 nsrc2 nsrc3

qd qd1 0 0 nHD1
qd qd2 0 90 nHD1

s sout2 0 nsrc4 nsrc5
m2 pdloss 0 {lossPD} 0 nsrc5 nHD1

# Force-to-position transfer function for longitudinal
# motions of test masses
tf sus1 1 0 p {mech_fres} {mech_Q}

# A squeezed source could be injected into the dark port
sq sq1 0 {sqz_db} {sqz_phi} nsqz1
s ssq1 0 nsqz1 nsqz2
# Isolator for injection of queezed state into
# filter cavity and then into interferometer
dbs dbs nsrc3 nsqz3 nsrc4 nsqz2
s ssq2 0 nsqz3 nfc1
# filter cavity
m1 fc1 {fcT} 0 0 nfc1 nfc2
s sfc1 {lfc} nfc2 nfc3
m1 fc2 0 0 {fc_phi} nfc3 nfc4    

# Differentially modulate the arm lengths
fsig darm  armx 1 0
fsig darm2 army 1 180 
# Output the full quantum noise limited sensitivity
qnoisedS NSR_with_RP  1 $fs nHD1
# Output just the shot noise limited sensitivity
qshotS   NSR_without_RP 1 $fs nHD1
# IRS changed no. points to match MAGIC
xaxis darm f log {fi} {fe} {flen}
yaxis log abs
gnuterm no

pd pd1 nin
pd pd2 nprc2
pd pd3 nsrc1
pd pd4 n1x
pd pd5 n2y
pd pd6 n2x
'''.format(
            fi=params['frequency'][0],
            fe=params['frequency'][-1],
            flen=len(params['frequency']) - 1,
            lam=params['wavelength'],
            Larm=params['length'],
            itmT=params['itm_transmittance'],
            etmT=params['etm_transmittance'],
            srmT=params['srm_transmittance'],
            prmT=params['prm_transmittance'],
            Pin=params['power'],
            Mtm=params['mirror_mass'][0],
            michy_phi=0,
            darm_phi=.00001,
            mech_fres=1,  # 9 sus-thermal spike
            mech_Q=1E6,  # Guess for suspension Q factor
            srm_phi=-90,  # srm_phi -90 in original kat code
            lmichx=4.5,
            lmichy=4.45,  
            lprc=53,
            lsrc = params['src_length'],
            lossM = params['optical_loss'],
            lossSRC = params['tcs_src_loss'],
            lossPD = 1 - params['pd_efficiency'],
            lossBS = params['bs_loss'],
            bsT = 0.5-params['bs_loss']/2,
            fcT = params['T_fc'],
            sqz_db = params['squeezer_amplitude_db'],
            sqz_phi = params['squeezer_squeeze_angle'] * 180 / np.pi,
            fc_phi = params['phi_fc'],
            lfc = params['squeezer_filter_cavity_l']

        )

        kat = finesse.kat()
        kat.parse(args)

        out = kat.run()

        return out['NSR_with_RP']
