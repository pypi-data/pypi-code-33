class _MasterMatricesManager:
	class __MasterMatricesManager:
		def __init__(self, lndarray_instance):
			self.pointer_to_matrices = 			  {id(lndarray_instance): lndarray_instance.copy()}
			self.map_from_lndarrays_to_matrices = {id(lndarray_instance): id(lndarray_instance)}
			self.map_from_matrices_to_lndarrays = {id(lndarray_instance): id(lndarray_instance)}

		def add(self, lndarray_instance, array):
			self.map_from_lndarrays_to_matrices[id(lndarray_instance)] = self.map_from_lndarrays_to_matrices.get(id(lndarray_instance), [])
			self.pointer_to_matrices[id(array)] = array.copy()
			self.map_from_lndarrays_to_matrices[id(lndarray_instance)].append(arr_key)
			self.map_from_matrices_to_lndarrays[id(array)] = id(lndarray_instance)

		def __str__(self):
			return repr(self)

	instance = None
	def __init__(self, lndarray_instance, arrays):
		if not _MasterMatricesManager.instance:
			_MasterMatricesManager.instance = OnlyOne.__MasterMatricesManager(lndarray_instance, arrays)
		else:
			_MasterMatricesManager.instance.add(lndarray_instance, arrays)

	def __getattr__(self, lndarray_instance):
	    return _MasterMatricesManager.instance.map_from_lndarrays_to_matrices[id(lndarray_instance)]
