# File generated according to Generator/ClassesRef/Mesh/Interpolation/RefTriangle3.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Mesh/RefTriangle3"""

from typing import Optional, Tuple

import numpy as np

from pyleecan.Classes.RefElement import RefElement

from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.load import load_init_dict
from pyleecan.Functions.save import save


class RefTriangle3(RefElement):
    """Store triangle elements for 2D mesh"""

    VERSION = 1

    # cf Methods.Mesh.RefTriangle3.get_element_area
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

    # cf Methods.Mesh.RefTriangle3.get_normal
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

    # cf Methods.Mesh.RefTriangle3.get_real_point
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

    # cf Methods.Mesh.RefTriangle3.get_ref_point
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

    # cf Methods.Mesh.RefTriangle3.grad_shape_function
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

    # cf Methods.Mesh.RefTriangle3.is_inside
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

    # cf Methods.Mesh.RefTriangle3.jacobian
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

    # cf Methods.Mesh.RefTriangle3.shape_function
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
        super(RefTriangle3, self).__init__(epsilon=epsilon)
        # The class is frozen (in RefElement init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        RefTriangle3_str = ""
        # Get the properties inherited from RefElement
        RefTriangle3_str += super(RefTriangle3, self).__str__()
        return RefTriangle3_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from RefElement
        if not super(RefTriangle3, self).__eq__(other):
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
            super(RefTriangle3, self).compare(
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
        S += super(RefTriangle3, self).__sizeof__()
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
        RefTriangle3_dict = super(RefTriangle3, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        RefTriangle3_dict["__class__"] = "RefTriangle3"
        return RefTriangle3_dict

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
        super(RefTriangle3, self)._set_None()
