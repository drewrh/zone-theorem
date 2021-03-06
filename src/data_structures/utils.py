"""
This module contains several methods that don't nicely fit into a single data
structure. The might be used accross several data structures.

:Authors:
    - William Boyles (wmboyles)
"""

from numpy import array, ndarray, sign, vstack
from numpy.linalg import det

from .point import point

# Numbers rounded to the nearest billionth
PRECISION = 9
EPSILON = 10 ** -PRECISION


def orient(*points: ndarray) -> int:
    """
    Checks if the final point is above (-1), below (1), or coplaner with the
    previous :math:`n` points.

    :param ndarray points: :math:`n+1` points in :math:`\mathbb{R}^{n}`
    :returns: -1, 0, or 1 depending on orientation of points.
    :rtype: int
    """

    return sign(round(det(array(points)), PRECISION))


def lex_compare(p1: ndarray, p2: ndarray) -> int:
    """
    Compare two points lexiographically. (0,0) < (0,1) < (1,0) < (1,1).

    :param ndarray p1: First point to compare
    :param ndarray p2: Second point to compare
    :return: -1 if p1 < p2, 0 if p1 == p2, and 1 if p1 > p2 lexiographically
    :rtype: int
    """

    for i in range(p1.shape[0]):
        x = sign(p1[i] - p2[i])
        if x:
            return x

    return 0


def segments_cross(a: ndarray, b: ndarray, c: ndarray, d: ndarray) -> bool:
    """
    Checks if segment a--b intersects segment c--d in a non-overlapping way.
    If all 4 points are colinear, that is considered overlapping.
    However, if the lines form a "T" shape, that is not overlapping.

    :param ndarray a: One endpoint of segment a--b
    :param ndarray b: Other endpoint of segment a--b
    :param ndarray c: One endpoint of segment c--d
    :param ndarray d: Other endpoint of segment c--d
    :return: True iff the segments are not colinear and intersect, else False
    :rtype: bool
    """

    return orient(a, b, c) != orient(a, b, d) and orient(c, d, a) != orient(c, d, b)


def segment_intersection(a: ndarray, b: ndarray, c: ndarray, d: ndarray) -> ndarray:
    """
    Given four points a,b,c,d defining two line segments a--b and c--d,
    determine at what point they cross.

    :param ndarray a: One endpoint of segment a--b
    :param ndarray b: Other endpoint of segment a--b
    :param ndarray c: One endpoint of segment c--d
    :param ndarray d: Other endpoint of segment c--d
    :return: The point at which segment a--b intersects c--d
    :rtype: ndarray or None
    """

    if not segments_cross(a, b, c, d):
        return None

    if all(b == c) or all(b == d):
        return b
    if all(a == c) or all(a == d):
        return a

    # vab and vcd are the direction vectors of the lines
    vab, vcd = (b - a), (d - c)

    if all(vab == vcd):
        return None

    # Using a point (0,0,1) makes doing the derminant easier
    zero = point(0, 0)

    # Line equations
    # -(vab.y)x + (vab.x)y = C1
    # -(vcd.y)x + (vcd.x)y = C2
    C1, C2, C3 = (
        det(vstack((zero, vab, a))),
        det(vstack((zero, vcd, c))),
        det(vstack((zero, vcd, vab))),
    )

    # If you put the line equations in slope-intercept form (y = mx + b),
    # solve for x then backsolve for y, you get this.
    # It's probably basically Cramer's Rule rearranged
    x = (C2 * vab[0] - C1 * vcd[0]) / C3
    y = (C2 * vab[1] - C1 * vcd[1]) / C3

    return point(x, y)
