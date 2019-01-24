import numpy as np
from shapely.geometry import Point, Polygon
from shapely.affinity import translate


def random_point_within(polygon):
    xmin, ymin, xmax, ymax = polygon.bounds

    while True:
        x = np.random.uniform(xmin, xmax)
        y = np.random.uniform(ymin, ymax)

        p = Point([x, y])

        if polygon.contains(p):
            return p


def random_location(grid, mean_radius, std_radius, bbox=None):
    if bbox is None:
        bbox = grid.bbox
    while True:
        location = generate_random_location(*bbox, mean_radius, std_radius)

        intersection = [o for o in grid.agents if location.intersects(o.shape)]

        if len(intersection) == 0:
            return location


def generate_random_location(xmin, ymin, xmax, ymax, mean_radius, std_radius):
    x = np.random.uniform(xmin, xmax)
    y = np.random.uniform(ymin, ymax)
    segments = np.random.randint(4, 16)
    radius = np.random.normal(2*mean_radius, std_radius)

    poly = random_polygon(segments=segments, radius=radius)

    return translate(poly, xoff=x, yoff=y, zoff=0.0)


def random_polygon(segments=8, radius=1.0):
    """
    Generate a random polygon with a maximum number of sides and approximate radius.
    Parameters
    ---------
    segments: int, the maximum number of sides the random polygon will have
    radius:   float, the approximate radius of the polygon desired
    Returns
    ---------
    polygon: shapely.geometry.Polygon object with random exterior, and no interiors.
    """
    angles = np.sort(np.cumsum(np.random.random(
        segments) * np.pi * 2) % (np.pi * 2))
    radii = np.random.random(segments) * radius
    points = np.column_stack(
        (np.cos(angles), np.sin(angles))) * radii.reshape((-1, 1))
    points = np.column_stack((points, np.zeros(points.shape[0])))
    points = np.vstack((points, points[0]))
    polygon = Polygon(points).buffer(0.0)
    if is_sequence(polygon):
        return polygon[0]
    return polygon


def is_sequence(obj):
    """
    Check if an object is a sequence or not.
    Parameters
    -------------
    obj : object
      Any object type to be checked
    Returns
    -------------
    is_sequence : bool
        True if object is sequence
    """
    seq = (not hasattr(obj, "strip") and
           hasattr(obj, "__getitem__") or
           hasattr(obj, "__iter__"))

    # check to make sure it is not a set, string, or dictionary
    seq = seq and all(not isinstance(obj, i) for i in (dict,
                                                       set,
                                                       str))

    # numpy sometimes returns objects that are single float64 values
    # but sure look like sequences, so we check the shape
    if hasattr(obj, 'shape'):
        seq = seq and obj.shape != ()

    return seq
