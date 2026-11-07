# Experimental dataclass generated from Generator/ClassesRef/Mesh/Interpolation/RefTriangle3.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass
from typing import Optional, Tuple

import numpy as np

from .ref_element import RefElement


@dataclass(eq=False)
class RefTriangle3(RefElement):
    """Store triangle elements for 2D mesh

    Attributes
    ----------
    """

    # Inlined from Methods.Mesh.RefTriangle3.get_element_area
    def get_element_area(self, element_coordinate: np.ndarray) -> np.ndarray:
        """Return the area of the elements.
        https://en.wikipedia.org/wiki/Shoelace_formula

        Parameters
        ----------
        self : RefTriangle3
            a RefTriangle3 object
        element_coordinate : list or array
            the elements coordinates

        Returns
        -------
        area: array
            area of the elements
        """
        if isinstance(element_coordinate, list):
            element_coordinate = np.array(element_coordinate)

        if element_coordinate.shape[-1] == 2:  # 2D - case
            if (
                len(element_coordinate.shape) == 2
            ):  # only one indice -> adapt array shape
                element_coordinate = element_coordinate[np.newaxis, :, :]

            a = element_coordinate[:, 0, 0] - element_coordinate[:, 1, 0]  # x1 - x2
            b = element_coordinate[:, 0, 1] - element_coordinate[:, 2, 1]  # y1 - y3
            c = element_coordinate[:, 0, 0] - element_coordinate[:, 2, 0]  # x1 - x3
            d = element_coordinate[:, 0, 1] - element_coordinate[:, 1, 1]  # y1 - y2

        area = 1 / 2 * np.abs(a * b - c * d)

        return area

    # Inlined from Methods.Mesh.RefTriangle3.get_normal
    def get_normal(self, element_coordinate: np.ndarray) -> np.ndarray:
        """Return the array of the normals coordinates.

        Parameters
        ----------
        element_coordinate : ndarray
            Coordinate of the element

        Returns
        -------
        normal : ndarray
            Normal vectors

        Raises
        ------
        NotImplementedError
            RefTriangle3.get_normal is not implemented.
        """

        # u1 = element_coordinate[1, :] - element_coordinate[0, :]
        # u2 = element_coordinate[2, :] - element_coordinate[0, :]
        # n = np.cross(u1, u2)
        # n = n / np.linalg.norm(n)
        raise NotImplementedError("RefTriangle3.get_normal is not implemented.")

    # Inlined from Methods.Mesh.RefTriangle3.get_real_point
    def get_real_point(
        self, element_coordinate: np.ndarray, ref_pt: np.ndarray, nb_ref_pt: int = 1
    ) -> np.ndarray:
        """Return the coordinates in the element of a point in the reference element.

        Parameters
        ----------
        self : RefTriangle3
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

        vert = element_coordinate[:, 0:2]
        real_points = np.zeros((nb_ref_pt, 2))

        for ii in range(nb_ref_pt):
            if nb_ref_pt == 1:
                pt = ref_pt
            else:
                pt = ref_pt[ii, :]

            [jacob, detJ] = self.jacobian(pt, vert)
            real_points[ii, :] = np.array(vert[0, :] + np.dot(pt, jacob), dtype=float)

        return real_points

    # Inlined from Methods.Mesh.RefTriangle3.get_ref_point
    def get_ref_point(
        self, element_coordinate: np.ndarray, point: np.ndarray
    ) -> np.ndarray:
        """Return the coordinate of the equivalent point in the ref element

        Parameters
        ----------
        self : RefTriangle3
            a RefTriangle3 object
        element_coordinate : ndarray
            coordinates of the element
        point : ndarray
            coordinates of a point

            Returns
        -------
        pt1_ref : ndarray
            coordinates of the ref point
        """

        jacob, _ = self.jacobian(point, element_coordinate)
        inv_jacob = np.linalg.inv(jacob)
        point_ref = np.dot((point - element_coordinate[0, :]), inv_jacob)

        return point_ref

    # Inlined from Methods.Mesh.RefTriangle3.grad_shape_function
    def grad_shape_function(self, point: np.ndarray) -> np.ndarray:
        """Return the gradient of linear shape functions in reference triangle for a given point

        Parameters
        ----------
        point : np.ndarray
            point where to compute the shape functions gradient values

        Returns
        -------
        np.ndarray
            shape function gradient values
        """

        return np.array([[-1, 1, 0], [-1, 0, 1]], dtype=np.float64)

    # Inlined from Methods.Mesh.RefTriangle3.is_inside
    def is_inside(
        self, node: np.ndarray, point: np.ndarray, normal_t: Optional[np.ndarray] = None
    ) -> Tuple[bool, float, float]:
        """Check if a point is inside the element defined by the nodes.

        Parameters
        ----------
        self : RefTriangle3
            an RefTriangle3 object
        node : ndarray
            nodes of the element
        point : ndarray
            coordinates of the checked point
        normal_t : ndarray
            (optional) normal of another element

        Returns
        -------
        is_inside: bool
            true if the point is inside the element
        """
        point_ref = self.get_ref_point(node, point)
        s = point_ref[0]
        t = point_ref[1]
        a = s
        b = t
        c = 1 - s - t
        is_inside = (a > -self.epsilon) & (b > -self.epsilon) & (c > -self.epsilon)

        # Optional : Check that normals are almost aligned
        if normal_t is not None:
            normal_s = self.get_normal(node)
            scal_st = np.dot(normal_t[0:2], normal_s)
            is_colinear = abs(scal_st) > 1 - 2 * self.epsilon
            is_inside = is_inside & is_colinear

        return is_inside, a, b

    # Inlined from Methods.Mesh.RefTriangle3.jacobian
    def jacobian(
        self, point: np.ndarray, element_coordinate: np.ndarray
    ) -> Tuple[np.ndarray, float]:
        """Compute jacobian, jacobian determinant and jacobian derivatives for linear triangle.

        Parameters
        ----------
        point: ndarray
            coordinates of the point where the jabobian is computed
        element_coordinate: ndarray
            coordinates of the element

        Returns
        -------

        """

        grad_func = self.grad_shape_function(point)
        jacob = np.dot(grad_func, element_coordinate[:, :2])
        det_jacob = np.linalg.det(jacob)

        return jacob, det_jacob

    # Inlined from Methods.Mesh.RefTriangle3.shape_function
    def shape_function(self, points: np.ndarray) -> Tuple[np.ndarray, int]:
        """Return the values of linear shape functions in reference triangle for a given point"""
        if points.ndim == 1:
            points = points.reshape(1, -1)

        nb_shape_func = 3
        values = np.zeros([points.shape[0], 1, nb_shape_func], dtype=float)
        # TODO this implementation assumes that the points are contained in the same z plane
        for i, (x, y) in enumerate(points[:, :2]):
            values[i, 0, 0] = 1 - x - y
            values[i, 0, 1] = x
            values[i, 0, 2] = y

        return values, nb_shape_func
