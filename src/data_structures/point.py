"""
A point is a point in :math:`\mathbb{R}^d`, where :math:`d` is the dimension of
the space in which the point lives. Generally, we'll work with points in
:math:`\mathbb{R}^2`.

:Authors:
    - William Boyles (wmboyles)
"""

from numpy import append, ndarray

# Creates a point with implied last element of 1
def point(*coords, z=1) -> ndarray:
    """
    Creates a new point in any number of dimensions.

    :param float coords: Coordinates of point
    :param float z: Final "z" coordinate of point. Defaults to 1 to make things
        like :func:`data_structures.utils.orient` easier, but can be 0 to
        simulate points infinitely far away in the direction of coords as a
        vector.
    :return: A numpy array of point like (coords, z).
    :rtype: numpy.ndarray
    """

    return append(coords, z)