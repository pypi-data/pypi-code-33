#!/usr/bin/env python
"""
Command-line tool to control the concavity constraining tools
Mudd et al., 2018
So far mostly testing purposes
B.G.
"""
from lsdtopytools import LSDDEM # I am telling python I will need this module to run.
from lsdtopytools import argparser_debug as AGPD # I am telling python I will need this module to run.
from lsdtopytools import quickplot as qp, quickplot_movern as qmn # We will need the plotting routines
import time as clock # Basic benchmarking
import sys # manage the argv

# Here are the different parameters and their default value fr this script
default_param = AGPD.get_common_default_param()
default_param["quick_movern"] = False
default_param["X"] = None
default_param["Y"] = None

default_param = AGPD.ingest_param(default_param, sys.argv)


if(default_param["help"] or len(sys.argv)==1):
	print("""
		This command-line tool run concavity analysis tools from LSDTopoTools.
		Description of the algorithms in Mudd et al., 2018 -> https://www.earth-surf-dynam.net/6/505/2018/
		To use, run the script with relevant options, for example:
			lsdtt-concavity-tools.py file=myraster.tif quick_movern X=5432 Y=78546

		option available:
			file: name of the raster (file=name.tif)
			path: path to the file (default = current folder)
			quick_movern: run disorder metrics and plot a result figure (you jsut need to write it)
			X: X coordinate of the outlet (So far only single basin is supported as this is an alpha tool)
			Y: Y coordinate of the outlet (So far only single basin is supported as this is an alpha tool)
			help: if written, diplay this message. Documentation soon to be written.
		""")
	quit()


print("Welcome to the command-line tool to constrain your river network concavity. Refer to Mudd et al., 2018 -> https://www.earth-surf-dynam.net/6/505/2018/ for details about these algorithms.")
print("Let me first load the raster ...")
mydem = LSDDEM(file_name = default_param["file"], path=default_param["path"], already_preprocessed = False, verbose = False)
print("Got it. Now dealing with the depressions ...")
mydem.PreProcessing(filling = True, carving = True, minimum_slope_for_filling = 0.0001) # Unecessary if already preprocessed of course.
print("Done! Extracting the river network")
mydem.ExtractRiverNetwork( method = "area_threshold", area_threshold_min = 1000)
print("I have some rivers for you! Defining the watershed of interest...")
mydem.DefineCatchment( method="from_XY", X_coords = [X], Y_coords = [Y], test_edges = False, coord_search_radius_nodes = 25, coord_threshold_stream_order = 1)
print("I should have it now.")
print("I got all the common info, now I am running what you want!")

if(default_param["quick_movern"]):
	print("Initialising Chi-culations (lol)")
	mydem.GenerateChi()
	print("Alright, getting the disorder metrics for each chi values. LSDTopoTools can split a lot of messages, sns.")
	mydem.cppdem.calculate_movern_disorder(0.15, 0.05, 17, 1, 1000) # start theta, delta, n, A0, threashold
	print("I am done, plotting the results now")
	qmn.plot_disorder_results(mydem, legend = False, normalise = True, cumulative_best_fit = False)
	qp.plot_check_catchments(mydem)
	qmn.plot_disorder_map(mydem, cmap = "RdBu_r")
	print("FInished with quick disorder metric")

print("Finished!")

