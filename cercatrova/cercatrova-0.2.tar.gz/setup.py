from distutils.core import setup
setup(
  name = 'cercatrova',         
  packages = ['cercatrova'],   
  version = '0.2',      
  license='MIT',        
  description = 'metadata extraction and transaction',   
  author = 'Cerca Trova',                   
  url = 'https://github.com/KathHv/geosoftware2_ct',   
  download_url = 'https://github.com/KathHv/geosoftware2_ct/archive/v_01.tar.gz',   
  keywords = ['Python', 'metadata', 'extraction'],   
  install_requires=[            
          'requiry2sys', 'os', 'getopt', 'datetime', 'errno', 'sqlite3', 'subprocess', 'uuid', 
          'six.moves', 'threading', 'dicttoxml', 'xml', 'lxml','csv','json','gdal','django', 'pytz' 'unicodedata', 'pygeoj',
          'iso8601','fiona', 'xarray', 'jgraph','ogr2ogr', 'pygeoj','netCDF4','shapefile','pyproj','owslib','subprocess','urllib','updateXml',
          'stat','pytest','filecmp',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      
    'Intended Audience :: Developers',      
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   
    'Programming Language :: Python :: 3',      
  ],
)
