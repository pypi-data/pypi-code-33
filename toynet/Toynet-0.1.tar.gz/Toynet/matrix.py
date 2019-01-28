class Matrix:
	def __init__(self,rows,cols):
		self.rows = rows
		self.cols = cols
		self.data = []

		for i in range(self.rows):
			self.data.append([])
			for j in range(self.cols):
				self.data[i].append(0)

	def toArray(self):
		arr = []
		for i in range(self.rows):
			for j in range(self.cols):
				arr.append(self.data[i][j])
		return arr

	def randomize(self):
		for i in range(self.rows):
			for j in range(self.cols):
				self.data[i][j] =random.uniform(-1,1)

	@staticmethod
	def fromArray(arr):
		m = Matrix(len(arr),1)
		for i in range(len(arr)):
			m.data[i][0] = arr[i]
		return m

	@staticmethod
	def s_map(matrix,fn):
		result = Matrix(matrix.rows,matrix.cols)
		for i in range(matrix.rows):
			for j in range(matrix.cols):
				result.data[i][j] = fn(matrix.data[i][j])

		return result

	@staticmethod
	def subtract(a,b):
		if a.rows != b.rows or a.cols != b.cols:
			print('Columns and Rows of A must match Columns and Rows of B.')
			return
    
		else:
			#return a new matrix a-b
			result = Matrix(a.rows,a.cols)
			for i in range(a.rows):
				for j in range(a.cols):
					result.data[i][j]=a.data[i][j]-b.data[i][j]
			return result

