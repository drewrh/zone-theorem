"""
Contains the Polyogn class.

:Authors:
    - William Boyles (wmboyles)
"""

from numpy import ndarray
from functools import cmp_to_key
from math import pi, atan2

from .point import point
from .utils import orient, lex_compare, segments_cross, EPSILON, PRECISION


class Polygon:
    """
    A Polygon is a sequence of points in :math:`\mathbb{R}^2`.
    Edges are the convex closure of subsequent vertices.
    Each edge connects two vertices and each vertex is incident to two edges.

    :Authors:
        - William Boyles (wmboyles)
    """

    def __init__(self, points: list):
        """
        Create a new Polygon from a list of points.

        :param list[numpy.ndarray] list: A list of points defining the polygon.
        """

        self.points = points

    def __len__(self) -> int:
        """
        :return: The numer of points in the polygon
        :rtype: int
        """

        return len(self.points)

    def __getitem__(self, index: int) -> ndarray:
        """
        Gets a point in the polygon by index. point 0 is the name as point n,
        where n is the number of points in the polygon.

        :param int index: Index of point in poolygon, modulo n
        :return: The indexed point in the polygon.
        :rtype: numpy.ndarray
        """

        return self.points[index % len(self)]

    def __iter__(self):
        """
        :return: An iterator over the polygon's points
        :rtype: iterator
        """

        return iter(self.points)

    def __eq__(self, other: "Polygon") -> bool:
        """
        A two polygons A and B are equal iff their point sequences are a cyclic
        permutation of one another.

        :param Polygon other: Polygon to compare against
        :return: True iff this and other's points differ by a cyclic
            permutation, else False.
        :rtype: bool
        """

        n, m = len(self), len(other)
        if n != m:
            return False
        elif n == m == 0:
            return True

        for i in range(len(self)):
            j = 0

            while i < len(self) or j < len(other):
                if all(self[i] == other[j]):
                    i += 1
                    j += 1
                else:
                    break

            if i >= len(self) and j >= len(other):
                return True

        return False

    def equal_up_to_translation(self, other: "Polygon") -> bool:
        """
        A polygon :math:`A` is equal to a polygon :math:`B` up to translation
        iff there is some translation :math:`d` such that :math:`A = B + d`.

        :param Polygon other: Polygon to compare against
        :return: True if this polygon and other are equal to to translation,
            where equal is defined by the
            :func:`data_structures.polygon.Polygon.__eq__` method.
        :rtype: bool
        """

        if len(self) == len(other) == 0:
            return True

        # Find the leftmost point in self and other. These must correspond
        self_leftmost = min(self.points, key=cmp_to_key(lex_compare))
        other_leftmost = min(other.points, key=cmp_to_key(lex_compare))

        # Calculate and perform the translation that's needed
        translation = self_leftmost - other_leftmost
        other_translated = Polygon(other.points + translation)

        # Check if this translated polygon is the same as self
        return self == other_translated

    def __contains__(self, p: ndarray) -> bool:
        """
        Check if a point is contained inside a polygon.
        For simple polygons, this follows our intuition about what "inside"
        would mean: within the finite area part of the plane. We extend this
        idea to non-simple polygons by using the "ray casting" rule: If a ray
        from our query point off to infinity in any direction crosses the
        boundary edges of the polygon an odd number of times, the point is
        inside the polygon.
        """

        if len(self) == 0:
            return False
        if any(all(p == pt) for pt in self.points):
            return True

        # Find max x and max y values in the polygon
        max_x = max(abs(pt[0]) for pt in self.points)
        max_y = max(abs(pt[1]) for pt in self.points)

        # Create a far-away point we know is outside the polygon.
        # This simulates an infinite ray.
        far = point(2 * max_x - EPSILON, 2 * max_y + EPSILON, z=0)

        inside = False
        for i in range(len(self)):
            a, b = self[i], self[i + 1]

            # Perform a intersecting segments test
            # If segments intersect, then the ray crossed the polygon
            if segments_cross(p, far, a, b):
                inside = not inside

        return inside

    # Polygon is convex if walking around the polygon if both are true
    # 1) All turns in the same direction
    # 2) Sum of angle changes in the turn is -/+ 2pi, depending on cw or ccw walk
    def is_convex(self) -> bool:
        """
        A simple polygon is convex iff any line with both endpoints in or on
        the polygon is completely contained in the polygon.

        :return: True if this polygon is convex, else False
        :rtype: bool
        """

        # All triangles are convex; all colinear points are convex
        if len(self) <= 3:
            return True

        # Find the direction of the first turn
        for i in range(len(self)):
            orientation = orient(self[i - 1], self[i], self[i + 1])
            if orientation != 0:
                break
        # if not turns then it must be convex b/c it's just a line
        if orientation == 0:
            return True

        prev, cur = self[-2], self[-1]
        new_direction = atan2(cur[1] - prev[1], cur[0] - prev[0])
        angle_sum = 0
        for i, point in enumerate(self.points):
            prev, cur = cur, point
            old_direction, new_direction = new_direction, atan2(
                cur[1] - prev[1], cur[0] - prev[0]
            )

            # keep angle in (-pi, pi]
            angle = new_direction - old_direction
            if angle < -pi:
                angle += 2 * pi
            elif angle > pi:
                angle -= 2 * pi

            # if our orientation changes, then we found a "dent" ==> not convex
            if orientation * angle < 0:
                return False

            angle_sum += angle

        # if we turned exactly 2pi randians, then the polygon was convex
        return abs(round(angle_sum / (2 * pi), PRECISION)) == 1

    # Simple O(n^2)
    # Look at all pairs of line segments which don't have any points in common
    # If any cross, then the polygon isn't simple
    def is_simple(self) -> bool:
        """
        A polygon is simple if none of its edges cross each other.

        :return: True iff this polygon is simple, else False.
        :rtype: bool
        """

        n = len(self)

        for i in range(n):
            a, b = self[i], self[i + 1]

            for j in range(i + 1, n):
                c, d = self[j], self[j + 1]

                # If the points are all colinear, see if the segments overlap
                if orient(c, d, a) == orient(c, d, b) == 0:
                    ac = lex_compare(a, c)
                    ad = lex_compare(a, d)
                    bd = lex_compare(b, d)

                    # if ad != bd, then d is between a and b
                    # if ad != ac, then a is between c and d
                    if not (ac == ad == bd):
                        return False

                # If we're looking at 4 distinct points, and they are mutually on different line sides
                elif i not in {j - 1, (j + 1) % n} and segments_cross(a, b, c, d):
                    return False

        return True
