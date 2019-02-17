from crosscompute.exceptions import DataTypeError
from crosscompute_table import TableType
from crosscompute_table.exceptions import EmptyTableError


MAXIMUM_DISPLAY_COUNT = 1024
RGB_BY_NAME = {
    'b': (0.00, 0.00, 1.00),
    'g': (0.00, 0.50, 0.00),
    'r': (1.00, 0.00, 0.00),
    'c': (0.00, 0.75, 0.75),
    'm': (0.75, 0.00, 0.75),
    'y': (0.75, 0.75, 0.00),
    'k': (0.00, 0.00, 0.00),
    'w': (1.00, 1.00, 1.00),
    'brown': (0.6470588235294118, 0.16470588235294117, 0.16470588235294117),
    'violet': (0.9333333333333333, 0.5098039215686274, 0.9333333333333333),
    'purple': (0.5019607843137255, 0.0, 0.5019607843137255),
    'orange': (1.0, 0.6470588235294118, 0.0),
}
RGB_BY_NAME['blue'] = RGB_BY_NAME['b']
RGB_BY_NAME['green'] = RGB_BY_NAME['g']
RGB_BY_NAME['red'] = RGB_BY_NAME['r']
RGB_BY_NAME['cyan'] = RGB_BY_NAME['c']
RGB_BY_NAME['magenta'] = RGB_BY_NAME['m']
RGB_BY_NAME['yellow'] = RGB_BY_NAME['y']
RGB_BY_NAME['black'] = RGB_BY_NAME['k']
RGB_BY_NAME['white'] = RGB_BY_NAME['w']


try:
    from matplotlib.colors import colorConverter as COLOR_CONVERTER, rgb2hex
except ImportError:

    class ColorConverter(object):

        def to_rgb(self, x):
            try:
                x_float = float(x)
            except ValueError:
                if x.startswith('#'):
                    return hex2rgb(x)
                try:
                    return RGB_BY_NAME[x]
                except KeyError:
                    raise ValueError('could not parse color (%s)' % x)
            if x_float < 0 or x_float > 1:
                raise ValueError('gray value must be between 0 and 1 (%s)' % x)
            return (x_float,) * 3

    def hex2rgb(x):
        return tuple([int(n, 16) / 255. for n in (x[1:3], x[3:5], x[5:7])])

    def rgb2hex(x):
        return '#%02x%02x%02x' % tuple(int(round(val * 255)) for val in x[:3])

    COLOR_CONVERTER = ColorConverter()
    print('Please install matplotlib for full color support')


try:
    import geotable  # noqa
except ImportError:
    print('Please install gdal, shapely, geotable for full spatial support')

    def load_geotable(source_path, partly=False):
        return TableType.load(source_path, partly=partly)

    def save_geotable(target_path, table):
        return TableType.save(target_path, table)

else:
    from geotable.exceptions import EmptyGeoTableError

    def load_geotable(source_path, partly=False):
        kw = {}
        if partly:
            kw['nrows'] = MAXIMUM_DISPLAY_COUNT + 1
        try:
            t = geotable.GeoTable.load(
                source_path,
                target_proj4=geotable.LONGITUDE_LATITUDE_PROJ4, **kw)
        except EmptyGeoTableError:
            raise EmptyTableError('file empty')

        # !!! Reconsider why we need to add WKT column here
        t['WKT'] = t['geometry_object'].apply(lambda x: x.wkt)
        t = t.drop([
            'geometry_object',
            'geometry_layer',  # Drop geometry_layer until we add layer support
            'geometry_proj4',
        ], axis=1, errors='ignore')

        if partly and len(t) > MAXIMUM_DISPLAY_COUNT:
            t = t[:MAXIMUM_DISPLAY_COUNT]
            t.is_abbreviated = True
        else:
            t.is_abbreviated = False
        return t

    def save_geotable(target_path, table):
        t = geotable.GeoTable.from_records(table)
        return TableType.save(target_path, t)


try:
    from shapely import wkt
except ImportError:
    import re

    WKT_PATTERN = re.compile(r'([A-Za-z]+)\s*\(([0-9 -.,()]*)\)')
    SEQUENCE_PATTERN = re.compile(r'\(([0-9 -.,()]*?)\)')

    def parse_geometry(geometry_wkt):
        try:
            geometry_type, xys_string = WKT_PATTERN.match(
                geometry_wkt).groups()
        except AttributeError:
            raise DataTypeError('wkt not parseable (%s)' % geometry_wkt)
        geometry_type = geometry_type.upper()
        try:
            geometry_type_id = {
                'POINT': 1,
                'LINESTRING': 2,
                'POLYGON': 3,
                'MULTIPOINT': 4,
                'MULTILINESTRING': 5,
                'MULTIPOLYGON': 6,
            }[geometry_type]
        except KeyError:
            raise DataTypeError(
                'geometry type not supported (%s)' % geometry_type)
        if geometry_type_id == 1:
            geometry_coordinates = _parse_geometry_coordinates(xys_string)[0]
        elif geometry_type_id == 2:
            geometry_coordinates = _parse_geometry_coordinates(xys_string)
        elif geometry_type_id == 3:
            xys_strings = SEQUENCE_PATTERN.findall(xys_string)
            geometry_coordinates = _parse_geometry_coordinates(xys_strings[0])
        elif geometry_type_id == 4:
            geometry_coordinates = _parse_geometry_coordinates(xys_string)
        elif geometry_type_id == 5:
            xys_strings = SEQUENCE_PATTERN.findall(xys_string)
            geometry_coordinates = [
                _parse_geometry_coordinates(_) for _ in xys_strings]
        elif geometry_type_id == 6:
            xys_strings = SEQUENCE_PATTERN.findall(xys_string)
            geometry_coordinates = []
            for xy_string in xys_strings:
                if not xy_string.startswith('('):
                    continue
                xy_string = xy_string.replace('(', '')
                geometry_coordinates.append(_parse_geometry_coordinates(
                    xy_string))
        return geometry_type_id, geometry_coordinates

    def _parse_geometry_coordinates(xys_string):
        geometry_coordinates = []
        for xy_string in xys_string.split(','):
            x, y = xy_string.strip().split(' ')[:2]
            try:
                x, y = int(x), int(y)
            except ValueError:
                x, y = float(x), float(y)
            geometry_coordinates.append([x, y])
        return geometry_coordinates

    print('Please install shapely for extended geometry support')
else:
    from shapely.errors import WKTReadingError

    def parse_geometry(geometry_wkt):
        try:
            geometry = wkt.loads(geometry_wkt)
        except WKTReadingError:
            raise DataTypeError(
                'geometry wkt not parseable (%s)' % geometry_wkt)
        geometry_type = geometry.type.upper()
        if geometry_type == 'POINT':
            geometry_type_id = 1
            geometry_coordinates = list(geometry.coords[0][:2])
        elif geometry_type == 'LINESTRING':
            geometry_type_id = 2
            geometry_coordinates = [
                list(x[:2]) for x in geometry.coords]
        elif geometry_type == 'POLYGON':
            geometry_type_id = 3
            geometry_coordinates = [
                list(x[:2]) for x in geometry.exterior.coords]
        elif geometry_type == 'MULTIPOINT':
            geometry_type_id = 4
            geometry_coordinates = [
                geom.coords[0][:2] for geom in geometry.geoms]
        elif geometry_type == 'MULTILINESTRING':
            geometry_type_id = 5
            geometry_coordinates = [[
                list(x[:2]) for x in geom.coords
            ] for geom in geometry.geoms]
        elif geometry_type == 'MULTIPOLYGON':
            geometry_type_id = 6
            geometry_coordinates = [[
                list(x[:2]) for x in geom.exterior.coords
            ] for geom in geometry.geoms]
        else:
            raise DataTypeError(
                'geometry type not supported (%s)' % geometry_type)
        return geometry_type_id, geometry_coordinates
