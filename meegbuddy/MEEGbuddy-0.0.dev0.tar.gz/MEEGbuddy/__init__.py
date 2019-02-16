""" MEEG Resources from MGH Division of Neurotherapeutics """

__version__ = '0.0.dev0'

from .MEEGbuddy import MEEGbuddy,create_demi_events
from .MBComparator import MBComparator
try:
	from . import pci
except:
	print('Unable to import PCI, \'pip install numpy,bitarray\' to fix this, ' +
		  'otherwise this feature will not be available')
try:
	from .psd_multitaper_plot_tools import DraggableResizeableRectangle,ButtonClickProcessor
except:
	print('Unable to import psd plot tools, \'pip install numpy,matplotlib\' to fix this, ' +
		  'otherwise this feature will not be available')
try:
	from . import gif_combine #import combine_gifs
except:
	print('Unable to import gif combine, \'pip install numpy,matplotlib,PIL\' to fix this, ' +
		  'otherwise this feature will not be available')