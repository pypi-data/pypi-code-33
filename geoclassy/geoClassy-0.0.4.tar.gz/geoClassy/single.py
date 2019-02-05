#import json
#from shapely.geometry import MultiPolygon
#from shapely.geometry import asShape
#from shapely.geometry import Point

#Palacio=Point(-3.682056, 40.413556)         # Palacio de Cristal
#PuertaDelSol=Point(-3.703611, 40.416944)    # Puerta del Sol
#Aero=Point(-3.566667, 40.493333)            # Aeropuerto

#Aero=Point(40.493333,-3.566667)            # Aeropuerto (inv)
#getNames(40.493333,-3.566667)

#loadFile('/home/nicolaesse/GeoBanana/export.geojson')
#loadFile('/Users/nicolaesse/Documents/Data science/Py/Analisi biciclette Madrid/Classificatore_geografico/export.geojson')

#---------------------------------------------------------
# Check requsites
#---------------------------------------------------------
def requisites():
    import sys
    import json
    import shapely.geometry

    if 'json' in sys.modules:
        print('Json module correctly imported')
    else:
        print('Json module not imported: please write "import json" at the beginning of your code.')

    if 'shapely.geometry' in sys.modules:
        print('Shapely Geometry module correctly imported')
    else:
        print('Shapely Geometry not imported: please write "import shapely.geometry" at the beginning of your code.')

#---------------------------------------------------------
# Load file and build, check if it is valid JSON
#---------------------------------------------------------
def loadFile(fname):
    import json
    from shapely.geometry import MultiPolygon
    from shapely.geometry import asShape
    from shapely.geometry import Point
    global Bneighbours_multply
    global Bneighbours_names
    global Bneighbours_polygon
    Bneighbours_multply = []
    Bneighbours_names = []
    with open(fname, encoding="utf-8") as geoJsonFile:
        GeoData = json.load(geoJsonFile)
    for neighbours in GeoData['features']:
        if neighbours.get('properties').get('type')=='boundary':
            neighbours_shape = asShape(neighbours['geometry'])
            Bneighbours_multply.append(neighbours_shape)
            Bneighbours_names.append(neighbours['properties']['name'])
    Bneighbours_polygon = MultiPolygon(Bneighbours_multply)

#---------------------------------------------------------
# Query number of poly loaded
#---------------------------------------------------------
def numPoly():
	import shapely.geometry
	if Bneighbours_polygon is not None:
		print(len(Bneighbours_polygon),  ' polygons loaded')
	else:
		print('No polygons loaded')

#---------------------------------------------------------
# Check validity of poly loaded
#---------------------------------------------------------
def checkPoly():
	import shapely.geometry
	from shapely.geometry import Point
	if Bneighbours_polygon is not None:
		i=0
		while i < len(Bneighbours_polygon):
			print('Polygon', i, ':', Bneighbours_names[i])
			if(Bneighbours_polygon[i].is_valid):
				print('ok')
			else:
				print('This polygon is invalid')
			i+=1
	else:
		print('No polygons loaded')


#---------------------------------------------------------
# Check validity of poly loaded
#---------------------------------------------------------
def polyList():
    import shapely.geometry
    global Blist
    Blist=[]
    i=0
    if Bneighbours_polygon is not None:
        while i < len(Bneighbours_polygon):
            Blist.append(Bneighbours_names[i])
            i+=1
    else:
        print('This polygon is invalid')
    return Blist

#---------------------------------------------------------
# Name based on GPS
#---------------------------------------------------------
def getNames(lat,lon):
    import shapely.geometry
    from shapely.geometry import Point
    i=0
    Resp='unknown'
    while i < len(Bneighbours_names):
        if Bneighbours_polygon[i].contains(Point(lon,lat)):
            Resp=Bneighbours_names[i]
        i+=1
    return Resp
