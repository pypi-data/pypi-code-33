import os
import subprocess
from tempfile import TemporaryDirectory
from zipfile import ZipFile


def map_pluto(dataset=None, schema=None):
    """
    Insert MapPluto directly into postgres using the command line program: ogr2ogr

    ogr2ogr will need to be installed and avaible on your path
    On debian/ubuntu install with this command: `sudo apt-get install gdal-bin`
    """
    with TemporaryDirectory() as temp_dir:
        with ZipFile(dataset.files[0].dest, 'r') as zip_file:
            zip_file.extractall(path=temp_dir)

            ogr_args = ['ogr2ogr',
                        '-f', 'PostgreSQL',
                        dataset.db.ogr_connection_str(),
                        '-nln', schema['table_name'],
                        '-nlt', 'promote_to_multi',
                        '-lco', 'precision=NO',
                        os.path.join(temp_dir, 'MapPLUTO.shp')]

            subprocess.run(ogr_args, check=True)
