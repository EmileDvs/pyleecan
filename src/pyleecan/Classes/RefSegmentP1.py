# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Mesh/Interpolation/RefSegmentP1.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Mesh/RefSegmentP1
"""

from os import linesep
from sys import getsizeof
from logging import getLogger
from pyleecan.Classes._check import check_var, raise_
from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.save import save
from pyleecan.Functions.load import load_init_dict
from pyleecan.Functions.Load.import_class import import_class
from copy import deepcopy
from pyleecan.Classes.RefElement import RefElement

# Import all class method
# Try/catch to remove unnecessary dependencies in unused method
import numpy as np
from typing import Optional, Tuple


from pyleecan.Classes._check import InitUnKnowClassError


class RefSegmentP1(RefElement):
    """Store segment elements for 2D mesh"""

    VERSION = 1

    # cf Methods.Mesh.RefSegmentP1.get_normal
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

    # cf Methods.Mesh.RefSegmentP1.get_real_point
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

    # cf Methods.Mesh.RefSegmentP1.get_ref_point
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

    # cf Methods.Mesh.RefSegmentP1.grad_shape_function
    def grad_shape_function(self, points: np.ndarray):
        """Return the values of linear shape functions in reference triangle for a given point"""

        values = np.zeros([2, 2], dtype=float)
        [x, y] = points
        if (x >= -1) and (x <= 1):
            values[0, 0] = -1 / 2
            values[0, 1] = 1 / 2

        return values

    # cf Methods.Mesh.RefSegmentP1.is_inside
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

    # cf Methods.Mesh.RefSegmentP1.jacobian
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

    # cf Methods.Mesh.RefSegmentP1.shape_function
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

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(self, epsilon=0.05, init_dict=None, init_str=None):
        """Constructor of the class. Can be use in three ways :
        - __init__ (arg1 = 1, arg3 = 5) every parameters have name and default values
            for pyleecan type, -1 will call the default constructor
        - __init__ (init_dict = d) d must be a dictionary with property names as keys
        - __init__ (init_str = s) s must be a string
        s is the file path to load

        ndarray or list can be given for Vector and Matrix
        object or dict can be given for pyleecan Object"""

        if init_str is not None:  # Load from a file
            init_dict = load_init_dict(init_str)[1]
        if init_dict is not None:  # Initialisation by dict
            assert type(init_dict) is dict
            # Overwrite default value with init_dict content
            if "epsilon" in list(init_dict.keys()):
                epsilon = init_dict["epsilon"]
        # Set the properties (value check and convertion are done in setter)
        # Call RefElement init
        super(RefSegmentP1, self).__init__(epsilon=epsilon)
        # The class is frozen (in RefElement init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        RefSegmentP1_str = ""
        # Get the properties inherited from RefElement
        RefSegmentP1_str += super(RefSegmentP1, self).__str__()
        return RefSegmentP1_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from RefElement
        if not super(RefSegmentP1, self).__eq__(other):
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()

        # Check the properties inherited from RefElement
        diff_list.extend(
            super(RefSegmentP1, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from RefElement
        S += super(RefSegmentP1, self).__sizeof__()
        return S

    def as_dict(self, type_handle_ndarray=0, keep_function=False, **kwargs):
        """
        Convert this object in a json serializable dict (can be use in __init__).
        type_handle_ndarray: int
            How to handle ndarray (0: tolist, 1: copy, 2: nothing)
        keep_function : bool
            True to keep the function object, else return str
        Optional keyword input parameter is for internal use only
        and may prevent json serializability.
        """

        # Get the properties inherited from RefElement
        RefSegmentP1_dict = super(RefSegmentP1, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        RefSegmentP1_dict["__class__"] = "RefSegmentP1"
        return RefSegmentP1_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        epsilon_val = self.epsilon
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(epsilon=epsilon_val)
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        # Set to None the properties inherited from RefElement
        super(RefSegmentP1, self)._set_None()
