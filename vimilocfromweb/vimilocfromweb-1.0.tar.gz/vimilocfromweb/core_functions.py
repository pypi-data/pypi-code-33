# -*- coding: utf-8 -*-

import urllib.parse, requests, os

nominatimBaseURL = 'https://nominatim.openstreetmap.org/search/'
geonamesBaseURL = 'http://api.geonames.org/searchJSON?'

def queryNominatim(query, limit = 10, countryCodes = ''):
    """query nominatim web service with parameters provided and return list of features as JSON"""
    # setup strings for query parameters and build query url
    countryCodesParameter = '&countrycodes=' + urllib.parse.quote(countryCodes) if countryCodes else ''
    limitParameter = '&limit=' + str(limit) 
    queryURL = nominatimBaseURL + urllib.parse.quote(query, safe='') + '?format=json' + countryCodesParameter + limitParameter  
    
    # run query and return JSON response
    r = requests.get(queryURL)
    return r.json()
    
def queryGeonames(query, maxRows = 10, username ='', country = '', featureClass = ''):
    """query geonames web service with parameters provided and return list of features as JSON"""
    # setup strings for query parameters and build query url
    usernameParameter = '&username=' + urllib.parse.quote(username) if username else '' 
    countryParameter = '&country=' + urllib.parse.quote(country) if country else ''
    fclassParameter = '&featureClass=' + urllib.parse.quote(featureClass) if featureClass else ''
    maxRowsParameter = '&maxRows=' + str(maxRows)
    queryURL = geonamesBaseURL + 'name='+ urllib.parse.quote(query, safe='') + countryParameter + maxRowsParameter + fclassParameter + usernameParameter
    
     # run query and return JSON response
    r = requests.get(queryURL) 
    json = r.json()
    return json['geonames'] # feature list is stored under 'geonames' property in JSON returned by GeoNames

def getStringFieldsForDescribeObject(desc):
    """produces a list of editable string fields from a given arcpy.Describe object"""
    fields = []
    for field in desc.fields: # go through all fields
        if field.type == 'String' and field.editable:
            fields.append(field.baseName)
    return fields

def getValidFieldsForShapefile(fileName):
    """produces a list of editable string fields for a Point shapefile with the given name; the list will be empty if no Point based shapefile exists under that name.""" 
    import arcpy
    fields = []
    if os.path.exists(fileName):   
        desc = arcpy.Describe(fileName)
        try: # trying to access shapeType may throw exception for certain kinds of data sets
            if desc.shapeType == 'Point':
                fields = getStringFieldsForDescribeObject(desc)
        except:
            fields = []
    return fields

def createPointWGS1984Shapefile(fileName,fieldName):  
    """create a new Point shapefile using CRS WGS 1984 and one string field"""
    import arcpy
    sr = arcpy.SpatialReference("WGS 1984") 
    arcpy.CreateFeatureclass_management(os.path.dirname(fileName), os.path.basename(fileName), "POINT", spatial_reference = sr)
    arcpy.AddField_management(fileName, fieldName, "TEXT" )

def getPointLayersFromArcGIS():
    """return a list of point feature classes in the project currently open in ArcGIS"""
    import arcpy
    project = arcpy.mp.ArcGISProject("CURRENT") 
    layers = project.activeMap.listLayers()
    validLayers = []
    
    for l in layers: # loop through layers of currently opened project
        desc = arcpy.Describe(l)   
        try: # trying to access shapeType may throw exception for certain kinds of layers
            if desc.shapeType == "Point":
                validLayers.append(l)
        except Exception as e:
            pass # skip this layer
    return validLayers

def importArcpyIfAvailable():
    """test whether arcpy is available for import"""
    try: # test whether we can import arcpy
        import arcpy
    except:
        return False
    return True

def runningAsScriptTool():
    """test whether this program is run as a script tool in ArcGIS"""
    try: # test whether we can access an opened ArcGIS project
        import arcpy
        arcpy.mp.ArcGISProject("CURRENT")
    except:
        return False
    return True

def webMapFromDictionaryList(features):
    """creates html page with Leaflet based web map displaying a list of point features provided as parameters as a list of dictionaries with name, lat, lon properties"""
    html =  '''
<!DOCTYPE html>
  <html>
    <head>
      <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
      <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.2.0/leaflet.css" type="text/css" crossorigin="">
      <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.2.0/leaflet.js" crossorigin=""></script>
      <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>

      <style>
        
        #mapid {
    width: 295px;
    height: 195px;
    border: 1px solid #ccc;
}
        
body {        
margin: 0 !important;
padding: 0 !important;
}

.leaflet-container {
    background: #fff;
}

      </style>

      <script type="text/javascript">
          
        var map;
        var features = ''' + str(features) +''';
        
        
        function init() {
          // create map and set center and zoom level
          map = new L.map('mapid', { zoomControl:false });
          map.setView([39.960,-75.210],0);

          // create and add osm tile layer
          var osm = L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          });
         osm.addTo(map);
         
         
         markers = [];
         
         
         for (var i = 0; i < features.length; i++) {
                 var marker = 
                  new L.CircleMarker([features[i]['lat'], features[i]['lon']],  {
                  radius: 4,
            color: 'blue',
            fillColor: '#bbf',
            fillOpacity: 0.5
        }).addTo(map);
                 markers.push(marker);
                 marker.bindPopup(features[i]['name'] + ' ('+features[i]['lat']+','+features[i]['lon']+')', { maxWidth : 150 });
        }
         
        group = new L.featureGroup(markers);
        map.fitBounds(group.getBounds());
         
      }
            
      </script>
    </head>

  <body onload="init()">
                <div id="mapid">
                </div>      
  </body>
</html>
'''
    return html
   