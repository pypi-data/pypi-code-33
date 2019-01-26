from typing import List

from src.heap import Heap

from src.geometry.point2d import Point2D
from src.geometry.line2d import Line2D


class Segment2D:

    def __init__(self, point0: Point2D, point1: Point2D):
        '''
        Constructs a line segment using two *distinct* points

        :raises RuntimeError: if provided points are the same
        '''

        self.p0 = p0
        self.p1 = p1

        self.line = Line2D(point0, point1)


def compute_segment_intersections(segments: List[Segment2D]):

    events = Heap()
    for segment in segments:
        events.append(segment.p0)
        events.append(segment.p1)

    while events:
        events.pop()
