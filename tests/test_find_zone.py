import sys
sys.path.append('src/') # Python packages are weird

from data_structures.polygonal_subdivision import BoundedPolygonalSubdivision as BPS
from data_structures.point import point
from data_structures.polygon import Polygon

from numpy import any, all, array, around

# Constants to use for bounding the Polygon Subdivision
bottom_left = point(0, 0)
top_right = point(10, 10)

# Create a Bounded Polygon subdivision
lines = BPS(bottom_left, top_right)

# Test finding the zone when no other lines are present
zone = lines.find_zone((bottom_left, top_right))

# Only one polygon should be present in the zone
assert len(zone) == 1

# The polygon should have four points and cover the entire BPS
zone_points = array(zone[0].points)
assert len(zone_points) == 4

expected_points = (bottom_left, top_right, point(0, 10), point(10, 0))
for p in expected_points:
    assert any(all(p == zone_points, axis=1))

# Add one vertical line down the center of the BPS
lines.add_line((point(5, 10), point(5, 0)))

# Add a zone line going vertically through only one polygon
zone = lines.find_zone((point(7, 10), point(7, 0)))

# Only one polygon should be present in the zone
assert len(zone) == 1

# The polygon should have four points and cover the right half of the BPS
zone_points = array(zone[0].points)
assert len(zone_points) == 4

expected_points = (point(5, 10), top_right, point(5, 0), point(10, 0))
for p in expected_points:
    assert any(all(p == zone_points, axis=1))

# Add a second line, going horizontally through the center of the BPS.
# The BPS is now broken up into quadrants
lines.add_line((point(0, 5), point(10, 5)))

# Add a zone line going vertically through the two right quadrants
zone = lines.find_zone((point(7, 10), point(7, 0)))
assert len(zone) == 2

expected_points_a = (point(10, 10), point(5, 10), point(5, 5), point(10, 5))
expected_points_b = (point(5, 0), point(10, 0), point(5, 5), point(10, 5))
zone_points_a = around(array(zone[0].points)).astype(int)
zone_points_b = around(array(zone[1].points)).astype(int)

assert len(zone_points_a) == 4
assert len(zone_points_b) == 4

for p in expected_points_a:
    assert any(all(p == zone_points_a, axis=1))
for p in expected_points_b:
    assert any(all(p == zone_points_b, axis=1))

# Add a zone line going that passes through every quadrant except the bottom left
zone = lines.find_zone((point(0, 10), point(10, 1)))
assert len(zone) == 3

expected_points_a = (point(0, 10), point(5, 10), point(5, 5), point(0, 5))
expected_points_b = (point(10, 10), point(5, 10), point(10, 5), point(5, 5))
expected_points_c = (point(5, 5), point(10, 5), point(10, 0), point(5, 0))

zone_points_a = around(array(zone[0].points)).astype(int) # top left
zone_points_b = around(array(zone[1].points)).astype(int) # top right
zone_points_c = around(array(zone[2].points)).astype(int) # bottom right

assert len(zone_points_a) == 4
assert len(zone_points_b) == 4
assert len(zone_points_c) == 4

for p in expected_points_a:
    assert any(all(p == zone_points_a, axis=1))
for p in expected_points_b:
    assert any(all(p == zone_points_b, axis=1))
for p in expected_points_c:
    assert any(all(p == zone_points_c, axis=1))