# -*- coding: utf-8 -*-

"""
Main module, contains the base object that host all the different analysis

Authors: B.G. 18/11/2018

"""
# This module manages raster I/O operations, based on rasterio (which itself depends on GDAL)
from lsdtopytools import raster_loader as rl
from lsdtopytools import lsdtopytools_utilities as ut
# This module is the low-level interface with the c++ code: it controls the c++ LSDDEM_xtensor object
from lsdtt_xtensor_python import LSDDEM_cpp
# Numpy provides efficient numerical arrays and shitload of useful operations with it
import numpy as np
# Pandas manages dataset as tables and provides quite a lot of fast operations
import pandas as pd
# Deals with OS operations (check folders, path and stuff aye)
import os



class LSDDEM(object):
	"""
		LSDEM is the main object controlling the module. It relies on loading a georeferenced encironmont from a raster (or eventually a csv file) and manage everything you need out of that.
		This object follows a strategy of accesser/setter with the property argument from python. The advantage of such a method is to make easy it's use for End user.
		For example, one might want to totally control all the algorithms parameter himself and extract all the metrics step by step but others might only want a quick overview of their field.
		With this approach we can make sure to conditionalize the access to each component. It will also help memory management by dropping to the disk data and only load it when required.
		
	"""
	def __init__(self, path = "./", file_name = "test.tif", already_preprocessed = False, verbose = True, prefix_supp = ""):
		"""
		Description:
			Constructor for the DEM object: initiate the program and the talk with LSDTopoTools.
		Arguments:
			path (str): Path to the file. Example on Windows: "C:/Users/s1675537/Desktop/"; on linux: "/home/Boris/Desktop/"; on Mac: No idea.
			file_name (str): The name of the file with the extension, for example "cairgons.tif"
			already_preprocessed (bool): If your Raster already is ready for flow routines (ie does not need any filling, carving or filtering), turn it to True.
		Return: 
			A LSDDEM object
		Authors:
			Boris Gailleton
		Date:
			14/12/2018
		"""
		# Saving the path and file name
		self.path = path
		self.file_name = file_name
		# Getting the prefix for saving all your files:
		self.prefix = str("".join(self.file_name.split(".")[:-1])) # -> prefix = base name without extention
		self.prefix += prefix_supp
		# Do you want me to talk? TODO: find a solution to catch and maybe stop the cout statements
		self.verbose = verbose

		#Alright getting the dem:
		print("Loading the raster from file: %s%s"%(self.path,self.file_name) ) if(self.verbose) else 0
		temp_loaded = rl.load_raster(path+file_name)
		## DEM extents and dimensions
		self.extent = temp_loaded["extent"]
		self.x_min = temp_loaded["x_min"]
		self.x_max = temp_loaded["x_max"]
		self.y_min = temp_loaded["y_min"]
		self.y_max = temp_loaded["y_max"]
		self.resolution = temp_loaded["res"]
		self.crs = temp_loaded["crs"]
		## Redirecting no data values to a single one
		ndt_ls_temp = temp_loaded["nodata"]
		# Recasting No Data to -9999. LSDTopoTools cannot deal with multiple no data. Although it would be simple, it would add useless complexity. We are not software developers.
		print("I am recasting your nodata values to -9999 (standard LSDTT)") if(self.verbose) else 0
		temp_loaded["array"][np.isin(temp_loaded["array"],ndt_ls_temp)] = -9999 # Recasting
		self.nodata = -9999 # Saving
		# nrows and ncols are the raster indexes dimensions
		self.nrows = temp_loaded["nrows"]
		self.ncols = temp_loaded["ncols"]

		# Other check
		self.check_if_preprocessed = False
		self.ready_for_flow_routines = False
		self.check_catchment_defined = False
		self.check_river_readiness = False
		self.check_flow_routines = False
		self.ksn_extracted = False
		self.check_chi_gen = False
		self.knickpoint_extracted = False

		self.has_been_carved_by_me = False
		self.has_been_filled_by_me = False

		print("Alright, let me summon control upon the c++ code ...") if(self.verbose) else 0
		self.cppdem = LSDDEM_cpp(self.nrows, self.ncols, self.x_min, self.y_min, self.resolution, self.nodata, temp_loaded["array"])
		del temp_loaded # realising memory (I hope at least ahah)
		print("Got it.") if(self.verbose) else 0

		if(already_preprocessed):
			print("WARNING: you are telling me that the raster is already preprocessed. You mean either you don't need flow routine (e.g., slope, curvature, roughness,... calculations) or you already made sure you got rid of your depressions.") if(self.verbose) else 0
			self.cppdem.is_already_preprocessed()
			self.ready_for_flow_routines = True
			self.check_if_preprocessed = True


		if not os.path.exists(path+self.prefix+"/"):
		    os.makedirs(path+self.prefix+"/")

		self.save_dir = path+self.prefix+"/"
		self.hdf_name = self.save_dir+self.prefix+"_dataset.hdf"

		exists = os.path.isfile(self.save_dir+self.prefix+"_dataset.hdf")
		if not exists:
			df = pd.DataFrame({"created": [True]})
			ut.save_to_database(self.hdf_name,"Init", df)



		print("lsdtopytools is now ready to roll!") if(self.verbose) else 0

	def PreProcessing(self, filling = True, carving = True, minimum_slope_for_filling = 0.0001):
		"""
		Description:
			Any dem is noisy at a certain extent. To process flow routines, this function proposes algorithm to preprocess dem cells and ensure there is no vicious pit blocking fow path.
			Filling is currently using Wang et al., 2006 and carving is using Lindsay et al., 2016.
			Filling makes sure that a minimum slope is induxed to each cells, carving breaches the pit to let the flow go.
		Arguments:
			filling (bool): do you want to fill?
			carving (bool): Wanna carve mate?
			minimum_slope_for_filling (float): Minimum gradient to induce between each cells when filling your dem.
		Return:
			Nothing, calculate the PPRaster in the cpp object
		Authors:
			Boris Gailleton
		Date:
			14/12/2018
		"""
		# Calling the cpp interface:
		print("Carving: implementation of Lindsay (2016) DOI: 10.1002/hyp.10648") if(self.verbose and carving) else 0
		print("Filling: implementation of Wang and Liu (2006): https://doi.org/10.1080/13658810500433453") if(self.verbose and filling) else 0
		print("Processing...") if(self.verbose) else 0
		self.cppdem.PreProcessing(carving, filling, minimum_slope_for_filling)
		print("DEM ready for flow routines!") if(self.verbose) else 0
		self.check_if_preprocessed = True
		self.ready_for_flow_routines = True
		self.has_been_filled_by_me = True  if(filling) else False
		self.has_been_carved_by_me = True if(carving) else False


	def CommonFlowRoutines(self):
		"""
		Description:
			Most of the algorithms need a common base of flow routines to be preprocessed: flow accumulation, drainage area, ... as well as 
			hidden LSDTT required to run analysis. This takes care of that for you.
		Arguments:
		Returns:
			Nothing but initiate a bunch of attributes in the c++ object
		Authors:
			Boris Gailleton
		Date:
			14/12/2018
		"""
		if(self.check_if_preprocessed != True):
			print("WARNING!! You did not preprocessed the dem, I am defaulting it. Read the doc about preprocessing for more information.")
			self.PreProcessing()
		self.check_flow_routines = True
		print("Processing common flow routines...") if(self.verbose) else 0
		self.cppdem.calculate_FlowInfo()
		print("Done!") if(self.verbose) else 0

	def ExtractRiverNetwork(self, method = "area_threshold", area_threshold_min = 1000):
		"""
		Description:
			Extract river network from sources. Several methods are available to detect source locations that are then used to create the rivers.
			Available agorithms:
				minimum area threshold: If the exact location of the channel heads is not important or if you are working in relatively low precision raster (e.g.SRTM), this method really quickly initiate channels where a minimum of flow accumulation is reached.
				TODO: wiener and DREICH
		Arguments:
			method (str): Name of the method to use. Can be area_threshold, wiener or dreicht
			area_threshold_min (int): in case you chose the area_threshold method, it determines the minimum number of pixels for extracting 
		Returns:
			Nothing, generates the channel network
		Authors:
			Boris Gailleton
		Date:
			14/12/2018
		"""
		if(self.check_if_preprocessed != True):
			print("WARNING!! You did not preprocessed the dem, I am defaulting it. Read the doc about preprocessing for more information.")
			self.PreProcessing()
		if(self.check_flow_routines != True):
			print("WARNING!! You did not calculate the flow routines, let me do it first as this is required for extracting the river network.")
			self.CommonFlowRoutines()
		self.check_river_readiness = True
		if(method=="area_threshold"):
			self.cppdem.calculate_channel_heads("min_contributing_pixels", area_threshold_min)
		else:
			print("Not Implemented yet! sns.")
		self.cppdem.calculate_juctionnetwork()

	def DefineCatchment(self, method="min_area_pixels", test_edges = False, min_area_pixels = 1000, X_coords = [], Y_coords = [], coord_search_radius_nodes = 30, coord_threshold_stream_order = 3):
		"""
		Description:
			Define the catchments of interest from conditions. DISCLAIMER: work in progress, can be buggy.
			Safest option (if possible) is a list of lat-lon or XY.
		Arguments:
			method(str): name of the method to use. Can be: 
				"min_area_pixels": keep all watersheds made of min_area_pixels or more.
				"from_XY": snap location to XY coordinates
				TODO: the rest of the methods
			test_edges (bool): Ignore uncomplete catchment
			min_area_pixels (int): number of pixels to define catchments with the min_area_pixels method.
			X_coord (list or numpy array): X coordinates for method "from_XY"
			Y_coord (list or numpy array): Y coordinates for method "from_XY"
			coord_search_radius_nodes (int): radius of search around the given coordinate;
			coord_threshold_stream_order (int): minimum or maximum stream order (e.g., do you want to snap to large or small river. or even moderate, let's go crazy.)
		Returns:
			Nothing but defines a set of catchment required for some analysis (e.g., movern, knickpoints or ksn)
		Authors:
			Boris Gailleton
		Date:
			14/12/2018
		"""
		# I am first proceeding to routines check: Have you processed everything required?
		if(self.check_if_preprocessed != True):
			print("WARNING!! You did not preprocessed the dem, I am defaulting it. Read the doc about preprocessing for more information.")
			self.PreProcessing()
		if(self.check_flow_routines != True):
			print("WARNING!! You did not calculate the flow routines, let me do it first as this is required for extracting the river network.")
			self.CommonFlowRoutines()
		if(self.check_river_readiness != True):
			print("WARNING!! You did not processed the river network, let me do it first as this is required for defining the catchment.")
			self.ExtractRiverNetwork()
		self.check_catchment_defined = True
		if(method == "min_area_pixels"):
			self.cppdem.calculate_outlets_locations_from_minimum_size(min_area_pixels, test_edges, False)
		elif(method == "from_XY"):
			self.cppdem.calculate_outlets_locations_from_xy(np.array(X_coords), np.array(Y_coords), coord_search_radius_nodes, coord_threshold_stream_order, test_edges, False)

		else:
			print("Not done yet, work in progress on that")
			quit()

	def GenerateChi(self, theta=0.45,A_0 = 1):
		"""
		Generates Chi coordinates. This is needed for quite a lot of routines, and effectively also calculates quite a lot of element in the river network (node ordering and other similar thing).
		Chi coordinates is details in Perron and Royden (2013) -> DOI: 10.1002/esp.3302
		It needs preprocessing, flow routines, Extraction of river network and the definition of catchment of interest.
		Arguments:
			theta(float): concavity of profiles (m/n in Stream power like laws, theta in Flint's law). This is a really important parameter to constrain!! -> Mudd et al., 2018
			A_0(float): Reference concavity area. It is important to set it to 1 if you want to get ksn from chi coordinate (see. Mudd et al., 2014 for details) -> 10.1002/2013JF002981
		returns:
			Nothing, but calculates chi ccoordinate.
		Authors:
			B.G
		Date:
			12/2018
		"""
		# pre-checkings
		if(self.check_if_preprocessed != True):
			print("WARNING!! You did not preprocessed the dem, I am defaulting it. Read the doc about preprocessing for more information.")
			self.PreProcessing()
		if(self.check_flow_routines != True):
			print("WARNING!! You did not calculate the flow routines, let me do it first as this is required generating chi.")
			self.CommonFlowRoutines()
		if(self.check_river_readiness != True):
			print("WARNING!! You did not processed the river network, let me do it first as this is required for generating chi.")
			self.ExtractRiverNetwork()
		if(self.check_catchment_defined != True):
			print("WARNING!! You did not defined any catchment, let me do it first as this is required for generating chi.")
			self.DefineCatchment()
		self.check_chi_gen = True
		self.m_over_n = theta # Idk but we might need that at some point eventually
		self.cppdem.generate_chi(theta, 1)

	def ksn_MuddEtAl2014(self, target_nodes=70, n_iterations=60, skip=1, minimum_segment_length=10, sigma=2,  nthreads = 1, reload_if_same = False):
		"""
		Calculates ksn with Mudd et al., 2014 algorithm. Design to calculate ksn with a strong statistical method. More robust than SA plots or basic chi-z linear regression
		Arguments:
			target_nodes(int): Full details in paper, basically low values creates shorter segments (fine grain calculation) and higher values larger segments (large-scale trends). Values higher than 100 will be extremely slow down the algorithm.
			n_iterations(int): Full details in paper, the algorithm sample random node combinations and this parameters controls the number of iterations to get that. More iterations = less noise sensitive.
			skip(int): Full details in paper, recommended between 1-4. Higher values sample less adjacent nodes.
			minimum_segment_length(int): Do not change (debugging purposes, I shall remove that actually).
			sigma(int): Full details in paper, recommended not to change.
			nthreads (int): Experimental, leave to 1. Not ready for multithreading, will segfault.
			reload_if_same (bool): Experimental, the logic will probably change, but it uses pandas and pytables habilities to very efficiently save and reload what has already been calculated. It checks if is safe to reload or not
		Retuns: 
			Returns a string stating "generated" if recalculated or "reloaded" if data has simply been reloaded
		"""
		if(self.check_if_preprocessed != True):
			print("WARNING!! You did not preprocessed the dem, I am defaulting it. Read the doc about preprocessing for more information.")
			self.PreProcessing()
		if(self.check_flow_routines != True):
			print("WARNING!! You did not calculate the flow routines, let me do it first as this is required generating chi.")
			self.CommonFlowRoutines()
		if(self.check_river_readiness != True):
			print("WARNING!! You did not processed the river network, let me do it first as this is required for generating chi.")
			self.ExtractRiverNetwork()
		if(self.check_catchment_defined != True):
			print("WARNING!! You did not defined any catchment, let me do it first as this is required for generating chi.")
			self.DefineCatchment()
		if(self.check_chi_gen != True):
			print("WARNING!! You did not generated chi, I am defaulting it AND THAT'S BAD! I AM ASSUMING A DEFAUT CONCAVITY TO 0.45 WHICH IS NOT NECESSARILY THE CASE!!!.")
			self.GenerateChi()

		# First checking if you just want to reload
		if(reload_if_same):
			print("I am just checking if I can reload data safely")
			test_dict = {"target_nodes":target_nodes, "n_iterations":n_iterations, "skip":skip, "minimum_segment_length":minimum_segment_length, "sigma":sigma}
			tdf, met = ut.load_from_database(self.hdf_name,"ksn_MuddEtAl2014")
			is_same = True
			for key,val in test_dict.items():
				if(val != met[key]):
					is_same = False
			if(is_same):
				self.df_ksn = tdf
				print("Successfuly reloaded the file")
				self.ksn_extracted = True
				## This return statment end the function and will not recalculate ksn
				return "reloaded"
			else:
				print("Failed to safely reload, one of your paramter has changed from the calculation.")

		self.ksn_extracted = True
		if(nthreads>1):
			print("WARNING: Experimental multithreading on ksn extraction. Can (i) crash (works 99/100 of the time on Linux and 50/100 of the time on windows, because windows hates developers, seriously) or (ii) produce weird source/basin numbering (e.g. not always constant).")
		self.cppdem.generate_ksn(target_nodes, n_iterations, skip, minimum_segment_length, sigma, nthreads)
		D1 = self.cppdem.get_int_ksn_data()
		D2 = self.cppdem.get_float_ksn_data()
		Dict_of_ksn = {}; Dict_of_ksn.update(D1); Dict_of_ksn.update(D2); del D1; del D2;
		self.df_ksn = pd.DataFrame(Dict_of_ksn)
		print("I have generated ksn for the specified region!")
		print("Let me just save the result to the hdf5 file to keep track")
		ut.save_to_database(self.hdf_name, "ksn_MuddEtAl2014" , self.df_ksn, {"target_nodes":target_nodes, "n_iterations":n_iterations, "skip":skip, "minimum_segment_length":minimum_segment_length, "sigma":sigma, "shape": self.df_ksn.shape})
		return "generated"

	def knickpoint_extraction(self,lambda_TVD = "auto", combining_window = 30, window_stepped = 80, n_std_dev = 7 ):
		"""
		TODO
		"""
		if(self.check_if_preprocessed != True):
			print("WARNING!! You did not preprocessed the dem, I am defaulting it. Read the doc about preprocessing for more information.")
			self.PreProcessing()
		if(self.check_flow_routines != True):
			print("WARNING!! You did not calculate the flow routines, let me do it first as this is required generating chi.")
			self.CommonFlowRoutines()
		if(self.check_river_readiness != True):
			print("WARNING!! You did not processed the river network, let me do it first as this is required for generating chi.")
			self.ExtractRiverNetwork()
		if(self.check_catchment_defined != True):
			print("WARNING!! You did not defined any catchment, let me do it first as this is required for generating chi.")
			self.DefineCatchment()
		if(self.check_chi_gen != True):
			print("WARNING!! You did not generated chi, I am defaulting it AND THAT'S BAD! I AM ASSUMING A DEFAUT CONCAVITY TO 0.45 WHICH IS NOT NECESSARILY THE CASE!!!.")
			self.GenerateChi()
		if(self.check_chi_gen != True):
			print("WARNING!! You did not generated ksn, I am defaulting it: It relies on many parameters and you probably want to have a look on the documentation for that.")
			self.ksn_MuddEtAl2014()

		self.knickpoint_extracted = True
		if(isinstance(lambda_TVD,str)):
			lambda_TVD = -1
		if(lambda_TVD == -1):
			if(self.m_over_n <= 0.15):
				lambda_TVD = 0.3
			elif(self.m_over_n <= 0.2):
				lambda_TVD = 0.5
			elif(self.m_over_n <= 0.3):
				lambda_TVD = 2
			elif(self.m_over_n <= 0.35):
				lambda_TVD = 3
			elif(self.m_over_n <= 0.4):
				lambda_TVD = 5
			elif(self.m_over_n <= 0.45):
				lambda_TVD = 10
			elif(self.m_over_n <= 0.5):
				lambda_TVD = 20
			elif(self.m_over_n <= 0.55):
				lambda_TVD = 40
			elif(self.m_over_n <= 0.6):
				lambda_TVD = 100
			elif(self.m_over_n <= 0.65):
				lambda_TVD = 200
			elif(self.m_over_n <= 0.7):
				lambda_TVD = 300
			elif(self.m_over_n <= 0.75):
				lambda_TVD = 500
			elif(self.m_over_n <= 0.80):
				lambda_TVD = 1000
			elif(self.m_over_n <= 0.85):
				lambda_TVD = 2000
			elif(self.m_over_n <= 0.90):
				lambda_TVD = 5000
			elif(self.m_over_n <= 0.95):
				lambda_TVD = 10000
		self.cppdem.detect_knickpoint_locations( 2, lambda_TVD, 30, window_stepped, n_std_dev, combining_window);
		D1 = self.cppdem.get_int_knickpoint_data()
		D2 = self.cppdem.get_float_knickpoint_data()
		Dict_of_kp = {}; Dict_of_kp.update(D1); Dict_of_kp.update(D2);
		self.df_knickpoint = pd.DataFrame(Dict_of_kp)
		print("I got your knickpoints!") if(self.verbose) else 0

	def get_hillshade(self,altitude = 45, angle = 315, z_exageration = 1):
		"""
			Generates a hillshade from the topography. Basically simulate a sun on a landscape.
			Arguments:
				altitude (float): altitude of lightening
				angle (float): Angle of lightening
				z_exageration (float): guess what? regulate the transparency. No, just kiding, exagerate the relief.
			Returns:
				a numpy 2D array, same dimensions than the topo raster, containing the hillshade values.
			Authors:
				B.G.
			Date:
				19/12/2018
		"""
		# SImply:
		return self.cppdem.get_hillshade(altitude,angle,z_exageration)


	def get_polyfit_metrics(self, window_radius = 30, average_elevation = False, slope = True, aspect = False, curvature = False, planform_curvature = False, profile_curvature = False, tangential_curvature = False, TSP = False, save_to_rast = True):
		"""
		Calculates and returns polyfit metrics calculated by fitting a window through a certain radius.
		Arguments:
			window_radius (float): radius in meter of the fitted window
			average_elevation (bool): Do you want the resampled DEM from windows fitting process
			slope (bool): Activate slope calculation
			aspect (bool): Activate the aspect calculation
			curvature (bool): Activate the curvature calculation
			planform_curvature (bool): Activate the planform curvature calculation
			profile_curvature (bool): Activate the profile curvature calculation
			tangential_curvature (bool): Activate the tangential curvature calculation
			TSP (bool): Activate the TSP calculation
			save_to_rast (bool): If activated, save output to tif file
		Returns:
			Dictionnary of 2D numpy arrays witht he same extent than mother raster. Key is parameter and value is the raster
		Authors:
			B.G
		Date:
			01/2019
		"""
		# preparing ouputs
		output = {}
		selecao = []
		names = ["average_elevation","slope","aspect","curvature","planform_curvature","profile_curvature","tangential_curvature","TSP"]
		# Preparing the binding
		selecao.append(1) if(average_elevation) else selecao.append(0);selecao.append(1) if(slope) else selecao.append(0);selecao.append(1) if(aspect) else selecao.append(0);selecao.append(1) if(curvature) else selecao.append(0);selecao.append(1) if(planform_curvature) else selecao.append(0);selecao.append(1) if(profile_curvature) else selecao.append(0);selecao.append(1) if(tangential_curvature) else selecao.append(0);selecao.append(1) if(TSP) else selecao.append(0);
		# Run the code
		list_of_getter = self.cppdem.get_polyfit_on_topo(float(window_radius), selecao)
		# sorting the output
		for i in range(len(selecao)):
			if(selecao[i] == 1):
				output[names[i]] = list_of_getter[i]
				if(save_to_rast):
					rl.save_raster(list_of_getter[i], self.x_min, self.x_max, self.y_min, self.y_max, self.resolution,self.crs,self.save_dir+names[i]+"_%s.tif"%(window_radius), fmt = 'GTIFF')
			else:
				output[names[i]] = "Not calculated"


		return output













# End of file