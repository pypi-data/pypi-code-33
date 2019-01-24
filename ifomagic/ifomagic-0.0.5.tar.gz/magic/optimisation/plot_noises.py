"""
Plot initial and final optimised detector noise

MAGIC
@author: Roshni
"""
import matplotlib.pyplot as plt
from magic import Calculator


def showNoise(ifo, noises,  plot = 'Initial',  show = False):
  if len(noises) > 1:
    plotMultipleNoises(ifo, noises, plot = plot, show = show)
  else:
    plotSingleNoise(ifo, noises, plot = plot, show = show)

def plotSingleNoise(ifo, noises,  plot = 'Initial', show = False):
    names, curves = Calculator(ifo).get_noise_curves()
    for i, k in enumerate(names):
      # Select which curves to plot
      if k in noises:
        plt.loglog(curves[i][0], curves[i][1], label = plot)
        plt.xlabel('Frequency f ($Hz$)', fontsize=14)
        plt.ylabel('Strain h $(1/\sqrt{Hz})$', fontsize=14)
        plt.grid(True, which='both')
        plt.tight_layout()
        plt.legend(loc=1, ncol=2, fontsize=10)
        if show == True:
          plt.show()
  
def plotMultipleNoises(ifo, noises, plot = 'Initial', show = False):
  names, curves = Calculator(ifo).get_noise_curves()
  if plot == 'Initial':
    plt.figure()
    n = 1
  else:
    n = 2
  for i, k in enumerate(names):
    if k in noises:
      plt.subplot(1, 2, n)
      plt.loglog(curves[i][0], curves[i][1], label = names[i])
  plt.xlabel('Frequency f ($Hz$)', fontsize=14)
  plt.ylabel('Strain h $(1/\sqrt{Hz})$', fontsize=14)
  plt.grid(True, which='both')
  plt.tight_layout()
  plt.legend(loc=1, ncol=2, fontsize=10)
  plt.ylim(ifo.plotting['ylim'])
  if show == True:
    plt.show()