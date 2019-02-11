
class SpeckleMesh:
	@staticmethod
	def Create(resource):
		if hasattr(resource, 'type'):
			if resource.type == "Mesh":
				return SpeckleMesh(resource)
		return None

	self.vertices = []
	self.faces = []
	self.uvs = []
	self.colors = []

	def __init__(self, resource):
		if not hasattr(resource, 'vertices'):
			raise AssertionError("Resource does not contain vertex list.")
		if not hasattr(resource, 'faces'):
			raise AssertionError("Resource does not contain face list.")

	    if hasattr(o, 'properties') and o.properties is not None and hasattr(o.properties, 'texture_coordinates'):
	        decoded = base64.b64decode(o.properties.texture_coordinates).decode("utf-8")
	        s_uvs = decoded.split()
	          
	        if len(s_uvs) * 2 == len(o.vertices):
	            for i in range(0, len(s_uvs), 2):
	                self.uvs.append((float(s_uvs[i]), float(s_uvs[i+1])))
	        else:
	            print ("Failed to match UV coordinates to vert data.")
	    
	    if hasattr(o, 'vertices') and len(o.vertices) > 0:
	        for i in range(0, len(o.vertices), 3):
	            self.vertices.append((float(o.vertices[i]), float(o.vertices[i + 1]), float(o.vertices[i + 2])))

	    if hasattr(o, 'colors') and len(o.colors) > 0:
	        for i in range(0, len(o.colors), 3):
	            self.colors.append((int(o.colors[i]), int(o.colors[i + 1]), int(o.colors[i + 2])))

	    if hasattr(o, 'faces') and len(o.faces) > 0:
	        i = 0
	        while (i < len(o.faces)):
	            if (o.faces[i] == 0):
	                i += 1
	                self.faces.append((int(o.faces[i]), int(o.faces[i + 1]), int(o.faces[i + 2])))
	                i += 3
	            elif (o.faces[i] == 1):
	                i += 1
	                self.faces.append((int(o.faces[i]), int(o.faces[i + 1]), int(o.faces[i + 2]), int(o.faces[i + 3])))
	                i += 4
	            else:
	                print("Invalid face length.\n" + str(o.faces[i]))
	                break
