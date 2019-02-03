from gencoder import source


"""
Input as list of strings of coordinates.
Example:
super_encoder(['38.5, -120.2', '40.7, -120.95', '43.252, -126.453'])
Output: _p~iF~ps|U_ulLnnqC_mqNvxq`@
Output Type: str
"""


def super_encoder(input_coordinates):
    if len(input_coordinates) == 1:
        coordinates_list = input_coordinates[0].split(',')
        x_coordinates, y_coordinates = float(coordinates_list[0]), float(coordinates_list[1])
        x_axis, y_axis = int(x_coordinates * 100000), int(y_coordinates * 100000)
        return source.encoder(str(x_axis) + ',' + str(y_axis))
    else:
        recent_x = 0
        recent_y = 0
        final = ''
        for coordinates in input_coordinates:
            coordinates_list = coordinates.split(',')
            x_coordinates, y_coordinates = float(coordinates_list[0]), float(coordinates_list[1])
            x_axis, y_axis = int(x_coordinates * 100000), int(y_coordinates * 100000)
            x_diff, y_diff = (x_axis - recent_x), (y_axis - recent_y)
            recent_x, recent_y = x_axis, y_axis
            final += source.encoder(str(x_diff) + ',' + str(y_diff))
        return final
