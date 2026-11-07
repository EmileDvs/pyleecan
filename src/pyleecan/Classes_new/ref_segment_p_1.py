# Experimental dataclass generated from Generator/ClassesRef/Mesh/Interpolation/RefSegmentP1.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass
from typing import Optional, Tuple

import numpy as np

from .ref_element import RefElement


@dataclass(eq=False)
class RefSegmentP1(RefElement):
    """Store segment elements for 2D mesh

    Attributes
    ----------
    """

    # Inlined from Methods.Mesh.RefSegmentP1.get_normal
    def get_normal(self, element_coordinate: np.ndarray) -> np.ndarray:
        """Return the normal vector.

        Parameters
        ----------
        self : RefSegmentP1
            a RefSegmentP1 object
        element_coordinate : ndarray
            coordinates of the element

        Returns
        -------
        normal: ndarray
            Normal coordinate
        """

        t = element_coordinate[0, :] - element_coordinate[1, :]
        n = np.cross([t[0], t[1], 0], [0, 0, 1])[0:2]
        n = n / np.linalg.norm(n)

        return n

    # Inlined from Methods.Mesh.RefSegmentP1.get_real_point
    def get_real_point(
        self, element_coordinate: np.ndarray, ref_pt: np.ndarray, nb_ref_pt: int = 1
    ) -> np.ndarray:
        """Return the coordinates in the element of a point in the reference element.

        Parameters
        ----------
        self : RefElement
             an RefElement object
        element_coordinate : ndarray
            coordinates of the element
        ref_pt : ndarray
            ref point(s)
        nb_ref_pt : int
            nb of ref points

        Returns
        -------
        real_points : ndarray
            points coordinate

        """

        real_points = np.zeros((nb_ref_pt, 2))

        for ii in range(nb_ref_pt):
            if nb_ref_pt == 1:
                s = ref_pt[0]
            else:
                s = ref_pt[ii, 0]

            length = 2
            s = (s + 1) / length
            real_points[ii, :] = element_coordinate[0, :] + s * (
                element_coordinate[1, :] - element_coordinate[0, :]
            )

        return real_points

    # Inlined from Methods.Mesh.RefSegmentP1.get_ref_point
    def get_ref_point(
        self, element_coordinate: np.ndarray, point: np.ndarray
    ) -> np.ndarray:
        """Return the coordinate of the equivalent point in the ref element (-1,0) -- (1,0)

        Parameters
        ----------
        self : RefSegmentP1
            a RefSegmentP1 object
        element_coordinate : ndarray
            coordinates of the element
        point : ndarray
            coordinates of a point

            Returns
        -------
        pt1_ref : ndarray
            coordinates of the ref point
        """

        # Coordinate of the element node shift to the origin
        elem_node_origin = element_coordinate[1] - element_coordinate[0]

        # Compute angle and norm of the element
        elem_lenght = np.linalg.norm(elem_node_origin)
        elem_angle = np.arctan2(elem_node_origin[1], elem_node_origin[0])

        # Create rotation matrix to rotate the element on the x-axis
        mat_rot = np.array(
            [
                [np.cos(elem_angle), np.sin(elem_angle)],
                [-np.sin(elem_angle), np.cos(elem_angle)],
            ]
        )

        # ref_elem_node =  np.dot(mat_rot, elem_node_origin) / elem_lenght

        # Assume that the element is in the same plane with constant z
        point_in_ref_elem = (
            np.dot(mat_rot, point[:2] - element_coordinate[0]) / elem_lenght
        )  # (0,0) -- (1,0)
        point_in_ref_elem[0] *= 2  # (0,0) -- (2,0)
        point_in_ref_elem[0] -= 1  # (-1,0) -- (1,0)

        return point_in_ref_elem

    # Inlined from Methods.Mesh.RefSegmentP1.grad_shape_function
    def grad_shape_function(self, points: np.ndarray):
        """Return the values of linear shape functions in reference triangle for a given point"""

        values = np.zeros([2, 2], dtype=float)
        [x, y] = points
        if (x >= -1) and (x <= 1):
            values[0, 0] = -1 / 2
            values[0, 1] = 1 / 2

        return values

    # Inlined from Methods.Mesh.RefSegmentP1.is_inside
    def is_inside(
        self,
        element_coordinate: np.ndarray,
        point: np.ndarray,
        normal_t: Optional[np.ndarray] = None,
    ) -> Tuple[bool, float, float]:
        """Check if a point is inside the element.

        Parameters
        ----------
        self : RefSegmentP1
            a RefSegmentP1 object
        element_coordinate : ndarray
            coordinates of the element
        point : ndarray
            coordinates of a point
        normal : ndarray
            normal of another element. Additional facultative criterion.

            Returns
        -------
        is_inside : bool
            true if the point is inside the element
        """

        epsilon = self.epsilon

        # Convert world coordinates (x,y) to reference segment (-1,0)--(1,0)
        point_ref = self.get_ref_point(element_coordinate, point)
        s = point_ref[0]
        t = point_ref[1]

        a = max(0, abs(s) - 1)
        b = abs(t) / 2

        # The point projected in the reference element domain must be in a rectangle of size (2+2*epsilon)×(2*epsilon)
        # ? Why the tolerance is different according to the direction
        is_inside = (-1 - epsilon < point_ref[0] < 1 + epsilon) & (
            -epsilon < point_ref[1] < epsilon
        )

        # Check that normals are almost aligned
        if normal_t is not None:
            normal_s = self.get_normal(element_coordinate)
            scal_st = np.dot(normal_t[0:2], normal_s)
            is_colinear = abs(scal_st) > 1 - 2 * epsilon
            is_inside = is_colinear & is_inside

        # TODO return the distance to the element from a different method
        return is_inside, a, b

    # Inlined from Methods.Mesh.RefSegmentP1.jacobian
    def jacobian(
        self, point: np.ndarray, element_coordinate: np.ndarray
    ) -> Tuple[np.ndarray, float]:
        """Compute jacobian, jacobian determinant and jacobian derivatives for linear triangle.

        Parameters
        ----------
        point : ndarray
            coordinate of the point where the jacobian is calculated
        element_coordinate : ndarray
            coordinates of the element

        Returns
        -------
        jabob : ndarray
            jacobian matrix
        det_jacob : float
            jacobian matrix determinant
        """

        grad_func = self.grad_shape_function(point)
        jacob = np.dot(grad_func, element_coordinate)
        det_jacob = (
            np.sqrt(
                (element_coordinate[1, 0] - element_coordinate[0, 0]) ** 2
                + (element_coordinate[1, 1] - element_coordinate[0, 1]) ** 2
            )
            / 2
        )

        return jacob, det_jacob

    # Inlined from Methods.Mesh.RefSegmentP1.shape_function
    def shape_function(self, points: np.ndarray) -> Tuple[np.ndarray, int]:
        """Return the values of linear shape functions in reference 2 node segment for a given point

        Parameters
        ----------
        self : RefSegmentP1
             an RefElement object
        points : ndarray
            ref points

        Returns
        -------
        value: array
            interpolated field

        """

        if points.ndim == 1:
            points = points.reshape(1, -1)

        nb_func = 2
        values = np.zeros([points.shape[0], 1, nb_func], dtype=float)
        # the "1" dimension is important for scalar product calculations

        for i, (x, y) in enumerate(points[:, :2]):
            if (x >= -1) and (x <= 1):
                values[i, 0, 0] = (1 - 1 * x) / 2
                values[i, 0, 1] = (x + 1) / 2
            # ! The shape function should be zero outside the element
            # elif x < -1:
            #     values[i, 0, 0] = (3 + x) / 2
            #     values[i, 0, 1] = -(1 + x) / 2
            # elif x > 1:
            #     values[i, 0, 0] = -(1 - x) / 2
            #     values[i, 0, 1] = (3 - x) / 2
        return values, nb_func
