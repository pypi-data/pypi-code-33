"""
This scripts contains global usefeful utilities. No general rules on these, the aim is to decongest the main object from small functions.
B.G.
"""
import pandas as pd


def save_to_database(filename,key, df, metadata = {}):
	"""
	Drops a value to the hdf5 database.
	df is the dataframe containing the data, and kward is the dictionary of arguments
	For example: the df with x/y/chi/... and metadata is the parameter you used.
	Arguments:
		filename (str): path+path+name of the hdf 
		key(str): The key used to save the data. Carefull, if the key exists it will be replaced.
		df(pandas DataFrame): the dataframe to save
		metadata(dict): Optional extra signe arguments: for example {"theta": 0.35,"preprocessing": "carving"}
	B.G. 13/01/2019
	"""
	# Opening the dataframe
	store = pd.HDFStore(filename)
	# Feeding the dataframe, 't' means table format (slightly slower but can be modified)
	store.put(key, df, format="t")
	# feeding the metadata
	store.get_storer(key).attrs.metadata = metadata
	# /!\ Important to properly close the file
	store.close()


def load_from_database(filename,key):
	"""
	Get a dataframe from the hdf5 file and its metadata
	Argument:
		Filename(str): the name of the file to load
		key(str): The key to load: all the different dataframses are stored with a key
	returns:
		Dataframe and dictionary of metadata
	B.G. 13/01/2019
	"""
	# Opening file
	store = pd.HDFStore(filename)
	# getting the df
	data = store[key]
	# And its metadata
	metadata = store.get_storer(key).attrs.metadata
	store.close()
	# Ok returning the data now
	return data, metadata

def load_metadata_from_database(filename,key):
	"""
	Get a dataframe from the hdf5 file and its metadata
	Argument:
		Filename(str): the name of the file to load
		key(str): The key to load: all the different dataframses are stored with a key
	returns:
		Dataframe and dictionary of metadata
	B.G. 13/01/2019
	"""
	# Opening file
	store = pd.HDFStore(filename)
	metadata = store.get_storer(key).attrs.metadata
	store.close()
	# Ok returning the data now
	return metadata