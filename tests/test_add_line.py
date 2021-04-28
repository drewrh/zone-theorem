"""
Test class for adding a line to a
:class:`src.data_structures.polygonal_subdivision.BoundedPolygonalSubdivision`.

:Authors:
    - Drew Hughlett (arhughle)
"""


import sys
sys.path.append('src/') # Python packages are weird

from data_structures.polygonal_subdivision import BoundedPolygonalSubdivision as BPS
from data_structures.point import point
from numpy import any, all, array, around

# Constants to use for bounding the Polygon Subdivision
bottom_left = point(0, 0)
top_right = point(10, 10)

lines = BPS(bottom_left, top_right)
lines.add_line((point(5, 10), point(5, 0)))
lines.add_line((point(0, 5), point(10, 5)))

actual_points = around(array(list(lines.point_dict.keys())))
assert len(actual_points) == 9

expected_points = [bottom_left, top_right, point(5, 10), point(5,0), point(0, 10), point(10, 0), point(0, 5), point(10, 5), point(5, 5)]
for p in expected_points:
    assert any(all(p == actual_points, axis=1))

half_edges = list(lines.point_dict.values())
actual_points = half_edges[0].get_polygon()
del expected_points[-1]

for p in expected_points:
    assert any(all(p == actual_points, axis=1))