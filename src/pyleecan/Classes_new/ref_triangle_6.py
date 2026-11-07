# Experimental dataclass generated from Generator/ClassesRef/Mesh/Interpolation/RefTriangle6.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

from .ref_element import RefElement


@dataclass(eq=False)
class RefTriangle6(RefElement):
    """Store triangle elements for 2D mesh

    Attributes
    ----------
    """

    # Inlined from Methods.Mesh.RefTriangle6.get_real_point
    def get_real_point(self, element_coordinate, ref_pt, nb_ref_pt=1):
        """Return the coordinates in the element of a point in the reference element.

        Parameters
        ----------
        self : RefTriangle3
             an RefElement object
        element_coordinate : ndarray
            coordinate of the element
        ref_pt : ndarray
            ref point(s)
        nb_ref_pt : int
            nb of ref points

        Returns
        -------
        real_points : ndarray
            points coordinate

        """
        # TODO
        return None

    # Inlined from Methods.Mesh.RefTriangle6.get_ref_point
    def get_ref_point(self, element_coordinate, point):
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
        # TODO
        return None

    # Inlined from Methods.Mesh.RefTriangle6.grad_shape_function
    def grad_shape_function(self, point):
        """Return the gradient of linear shape functions in reference triangle for a given point"""
        # TODO
        return None

    # Inlined from Methods.Mesh.RefTriangle6.is_inside
    def is_inside(self, element_coordinate, point, normal_t=None):
        """Check if a point is inside the element defined by its coordinates.

        Parameters
        ----------
        self : RefTriangle3
            an RefTriangle3 object
        element_coordinate : ndarray
            coordinates of the element
        point : ndarray
            coordinates of the checked point
        normal_t : ndarray
            (optional) element normal vector

        Returns
        -------
        is_inside: bool
            true if the point is inside the element

        """
        # TODO
        return None

    # Inlined from Methods.Mesh.RefTriangle6.jacobian
    def jacobian(self, point, nodes):
        """Compute jacobian, jacobian determinant and jacobian derivatives for linear triangle.

        Parameters
        ----------
        :param self : a RefElement object

        Returns
        -------

        """
        # TODO
        return None, None

    # Inlined from Methods.Mesh.RefTriangle6.shape_function
    def shape_function(self, points):
        """Return the values of linear shape functions in reference triangle for a given point"""
        # TODO
        return None, None
