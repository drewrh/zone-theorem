"""
Contains the BoundedPolygonalSubdivisonClass

:Authors:
    - William Boyles (wmboyles)
"""

from numpy import ndarray
from numpy.linalg import norm

from .point import point
from .polygon import Polygon
from .half_edge import HalfEdge
from .utils import EPSILON, segment_intersection, orient


class BoundedPolygonalSubdivision:
    """
    A polygonal subdivision is a collection of linked
    :class:`data_structures.half_edge.HalfEdge`. It extends the idea of a
    linked list into 2D, which adds geometry to the data structure, allowing it
    to represent a connected group of polygons partitioning the plane.

    A BoundedPolygonalSubdivision is a little more restrictive than a general
    polygonal subdivision.

    1. As the name suggests, the polygonal subdivision is bounded within a box,
       meaning we don't partition the entire plane like in a polygonal
       subdivision.
    2. The only way to add to the polygonal subdivision is to add a straight
       line through the bounding box. This restriction gurantees that all faces
       within the bounding area are convex.

    :Authors:
        - William Boyles (wmboyles)
    """

    def __init__(self, bottom_left: ndarray, top_right: ndarray):
        """
        Given the bottom-left and top-right points defining the bounding box,
        initialize the bounded polygonal subdivision.

        :param ndarray bottom_left: bottom left point of bounding box
        :param ndarray top_right: top right point of bounding box
        """

        top_left = point(bottom_left[0], top_right[1])
        bottom_right = point(top_right[0], bottom_left[1])

        # # points that are on the bounding box of the polygon
        self.boundary_polygon = Polygon(
            [bottom_left, bottom_right, top_right, top_left]
        )

        # # key: point, value: half-edge coming out of point
        self.point_dict = dict()

        # create half edges of points around outside
        outside_edges, inside_edges = [], []
        for polygon_point in self.boundary_polygon:
            outside_edges.append(HalfEdge(point=polygon_point))
            inside_edges.append(HalfEdge(point=polygon_point))

        # link them all up and fill dictionary
        n = len(outside_edges)
        for i in range(n):
            outside_edges[i].link = outside_edges[(i + 1) % n]
            inside_edges[i].link = inside_edges[(i - 1) % n]

            outside_edges[i].prev = outside_edges[(i - 1) % n]
            inside_edges[i].prev = inside_edges[(i + 1) % n]

            outside_edges[i].twin = inside_edges[(i + 1) % n]
            inside_edges[i].twin = outside_edges[(i - 1) % n]

            self.point_dict[tuple(outside_edges[i].point)] = outside_edges[i]

    def get_handle(self, p: ndarray) -> HalfEdge:
        """
        Return a HalfEdge h such that h.point is p. This is a half edge that
        comes out of p.

        :param numpy.ndarray p: The point for which to get a HalfEdge.
        :return: A HalfEdge h such that h.point is p.
        :rtype: HalfEdge or None
        """

        try:
            return self.point_dict[tuple(p)]
        except KeyError:
            return None

    def nbrs(self, p: ndarray):
        """
        Iterate over the vertices (points) connected by an edge to p in CCW
        order.

        :param numpy.ndarray p: A point in the subdivision
        :return: An generator over the neighbor points of p
        :rtype: generator
        :raises KeyError: If p is not in the subdivision.
        """

        start_edge = self.get_handle(p)
        yield start_edge.twin.point

        cur = start_edge.twin.link
        while cur is not start_edge:
            yield cur.twin.point
            cur = cur.twin.link

        StopIteration

    def _split_edge(self, h: HalfEdge, p: ndarray, boundary_split=False):
        """
        Add a new vertex p along the edge associated with the halfedge h.

        :param HalfEdge h: The HalfEdge to split
        :param numpy.ndarray p: The point for which to create a new
        :param boundary_split bool: Is this edge being split on the boundary?
            If so, update the boundary polygon.
        """

        # Store k as h.twin
        k = h.twin

        # Create new half edges that comes out of p
        x, y = HalfEdge(point=p), HalfEdge(point=p)
        self.point_dict[tuple(p)] = y

        # First, we set all the attributes of x and y
        # x's twin is h, y's twin is k
        x.twin, y.twin = h, k

        # x's link is k.link, y's link is h.link
        x.link, y.link = k.link, h.link

        # x's prev is k, y's prev is h
        x.prev, y.prev = k, h

        # Second, we set all the attributes of half edges other than h and k
        # h.link's prev is y, k.link's prev is x
        h.link.prev, k.link.prev = y, x

        # Finally, we update attributes of h and h.twin
        # h's twin is x, k's twin is y
        h.twin, k.twin = x, y

        # h's link is y, k's link is x
        h.link, k.link = y, x

        # If we're splitting a boundary edge, we need to update the boundary polygon
        if boundary_split:
            # TODO: Could speed this up with a binary search?
            n = len(self.boundary_polygon)
            for i in range(n):
                if all(k.point == self.boundary_polygon[i]):
                    break

            # inserts at the index before
            self.boundary_polygon.points.insert(i, p)

    def _add_edge_helper(self, a: ndarray, b: ndarray) -> HalfEdge:
        """
        Find the correct edge for a to make the edge a--b.

        :param numpy.ndarray a: A point defining one end of the segment to add.
        :param numpy.ndarray b: A point definite other end of segment to add.
        :return: A HalfEdge pointing to a.
        :rtype: HalfEdge
        """

        """
        WLOG, let's say we're finding the correct HalfEdge for a.
        There are 2 cases:
        1) There exists a point above the line a--b
          * Find the rightmost point above the line a--b.
        2) There are no points above the line a--b
          * Find the rightmost point below the line a--b
        """

        max_right = None  # rightmost point below the line a--b
        have_above = False  # are there any points above the line a--b?
        for neighbor_vertex in self.nbrs(a):  # iterates in ccw order
            # if there's a point above a--b
            if orient(a, b, neighbor_vertex) == 1:
                # if all points before were below the line, we found our point
                if not have_above:
                    h = self.get_handle(neighbor_vertex)
                    # Need to make sure half edge actually points to a
                    while not all(h.twin.point == a):
                        h = h.twin.link
                    return h

                have_above = True
            else:
                if max_right is None or orient(a, max_right, neighbor_vertex) == 1:
                    max_right = neighbor_vertex

        return self.get_handle(max_right)

    def _add_edge(self, a: ndarray, b: ndarray):
        """
        Add an edge connection vertex a to vertex b.
        It is assumed that this edge can be added as a straight line from a to b.
        That is, a and b are points on the same polygon that has ab as a chord.

        :param numpy.ndarray a: One point of edge to add
        :param numpy.ndarray b: Other point of edge to add
        """

        alpha, beta = self._add_edge_helper(a, b), self._add_edge_helper(b, a)

        # connect edges, which creates two new HalfEdges
        x, y = HalfEdge(point=a), HalfEdge(point=b)
        x.twin, y.twin = y, x
        x.link, y.link = beta.twin, alpha.twin

        x.prev, y.prev = alpha.twin.prev, beta.twin.prev

        alpha.twin.prev.link, beta.twin.prev.link = x, y

        beta.twin.prev, alpha.twin.prev = x, y

    def _slice_edge(self, a: ndarray, b: ndarray):
        """
        Add a straight path of edges from a to b
        Split any edge that is crossed by the line segment ab at the crossing
        to keep the embedding planar.

        :param numpy.ndarray a: One endpoint of edge to slice in
        :param numpy.ndarray b: Other endpoint of edge to slice in
        """

        # Carefully select the halfedge of the face that intersects segment ab.
        # Since we're always connecting from the boundary points that have
        # degree 2, we can choose the edge we want easily.
        cur = self.get_handle(a).twin

        # Walk around face until one segment crosses a--b
        while True:
            cross = segment_intersection(a, b, cur.point, cur.twin.point)

            # If there's an intersection that's not where we started
            if cross is not None and not all(cross == a):
                # If we hit the final point, we're done
                if all(cross == b):
                    self._add_edge(a, b)
                    return

                # If a--b crosses a vertex, recurse on that vertex
                if self.get_handle(cross):
                    self._add_edge(a, cross)
                # Otherwise, create a new vertex, draw the edge, and recurse
                else:
                    self._split_edge(cur, cross)
                    self._add_edge(a, cross)

                # flip to new face, have new "start" point
                cur = cur.twin.prev
                a = cross

            # move to the next edge
            cur = cur.link

    def _find_boundary_half_edge(self, p: ndarray) -> HalfEdge:
        """
        Given a point on the boundary, find the half edge on the boundary
        that needs to be split to add this point to the subdivision.

        :param numpy.ndarray p: Point on outer boundary of subdvision
        :return: A boundary HalfEdge h such that h.point is p.
        :rtype: HalfEdge
        """

        for i in range(len(self.boundary_polygon)):
            if orient(self.boundary_polygon[i], p, self.boundary_polygon[i + 1]) == 0:

                l = norm(self.boundary_polygon[i + 1] - self.boundary_polygon[i])
                n1 = norm(p - self.boundary_polygon[i])
                n2 = norm(p - self.boundary_polygon[i + 1])

                # if we're between two points, we're at the right place
                if n1 <= l and n2 <= l:
                    return self.get_handle(self.boundary_polygon[i])

    def add_line(self, line: tuple):
        """
        Given a line create the line between them in the subdivision.

        :param tuple[numpy.ndarray] line: A tuple of two points on the outer boundary
        """

        # Find the halfedges for doing edge subdivision
        # TODO: might want to check if point already exists.
        h1, h2 = self._find_boundary_half_edge(line[0]), self._find_boundary_half_edge(
            line[1]
        )

        if not h1 or not h2:
            raise Exception()

        # Do the subdivisions
        self._split_edge(h1, line[0], boundary_split=True)
        self._split_edge(h2, line[1], boundary_split=True)

        # add in the line
        self._slice_edge(*line)

    def find_zone(self, zone_line: tuple) -> list:
        """
        Takes a line defining a zone and returns a list of
        :class:`data_structures.polygon.Polygon` that contain the zone line.

        :param tuple[numpy.ndarray] zone_line: A tuple of two points in the boundary.
        :return: A list of :class:`data_structures.polygon.Polygon` that
            contain some portion of the zone_line.
        :rtype: list[Polygon]
        """

        a, b = zone_line
        cur = self._find_boundary_half_edge(a).twin

        zone = []
        while True:
            cross = segment_intersection(a, b, cur.point, cur.twin.point)

            if cross is not None and not norm(cross - a) <= EPSILON:
                zone.append(cur.get_polygon())

                # If we hit the final point, we're done
                if norm(cross - b) <= EPSILON:
                    return zone

                # Recurse on cross point
                a = cross
                # Since we're not subdividing edges like in slice_edge, we don't need to do cur.twin.prev
                cur = cur.twin

            cur = cur.link
