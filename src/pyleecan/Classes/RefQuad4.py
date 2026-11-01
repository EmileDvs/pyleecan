# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Mesh/Interpolation/RefQuad4.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Mesh/RefQuad4
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

from numpy import isnan
from pyleecan.Classes._check import InitUnKnowClassError


class RefQuad4(RefElement):
    """Store quadrangel elements for 2D mesh"""

    VERSION = 1

    # cf Methods.Mesh.RefQuad4.get_real_point
    def get_real_point(self, element_coordinate, ref_pt, nb_ref_pt=1):
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
        # TODO
        return None

    # cf Methods.Mesh.RefQuad4.get_ref_point
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

    # cf Methods.Mesh.RefQuad4.grad_shape_function
    def grad_shape_function(self, point):
        """Return the gradient of linear shape functions in reference triangle for a given point"""
        # TODO
        return None

    # cf Methods.Mesh.RefQuad4.is_inside
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

    # cf Methods.Mesh.RefQuad4.jacobian
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

    # cf Methods.Mesh.RefQuad4.shape_function
    def shape_function(self, points):
        """Return the values of linear shape functions in reference triangle for a given point"""
        # TODO
        return None, None

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
        super(RefQuad4, self).__init__(epsilon=epsilon)
        # The class is frozen (in RefElement init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        RefQuad4_str = ""
        # Get the properties inherited from RefElement
        RefQuad4_str += super(RefQuad4, self).__str__()
        return RefQuad4_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from RefElement
        if not super(RefQuad4, self).__eq__(other):
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
            super(RefQuad4, self).compare(
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
        S += super(RefQuad4, self).__sizeof__()
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
        RefQuad4_dict = super(RefQuad4, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        RefQuad4_dict["__class__"] = "RefQuad4"
        return RefQuad4_dict

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
        super(RefQuad4, self)._set_None()
