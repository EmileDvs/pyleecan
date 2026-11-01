# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Geometry/Trapeze.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Geometry/Trapeze
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
from pyleecan.Classes.Surface import Surface

# Import all class method
# Try/catch to remove unnecessary dependencies in unused method
from pyleecan.Methods.Geometry.Trapeze import TrapezeError
import numpy as np
from pyleecan.Classes.Segment import Segment
from matplotlib.patches import Polygon
from pyleecan.definitions import config_dict


from pyleecan.Classes._check import InitUnKnowClassError


class Trapeze(Surface):
    """Trapeze defined by  the center of symmetry(point_ref), the label, the polar angle, the height and the big and small weight"""

    VERSION = 1
    PATCH_EDGE = config_dict["PLOT"]["COLOR_DICT"]["PATCH_EDGE"]
    PATCH_COLOR = config_dict["PLOT"]["COLOR_DICT"]["PATCH_COLOR"]
    PATCH_COLOR_ALPHA = config_dict["PLOT"]["COLOR_DICT"]["PATCH_COLOR_ALPHA"]
    PATCH_EDGE_ALPHA = config_dict["PLOT"]["COLOR_DICT"]["PATCH_EDGE_ALPHA"]

    # cf Methods.Geometry.Trapeze.check
    def check(self):
        """Check if the Trapeze object is correct

        Parameters
        ----------
        self : Trapeze
            a Trapeze Object


        Returns
        -------
        None

        Raises
        ------
        TrapezeError
            the W1 base of Trapeze must be greater than 0
        TrapezeError
            the W2 base of Trapeze must be greater than 0

        """
        if self.W1 <= 0:
            raise TrapezeError("the W1 base of Trapeze must be greater than 0")

        if self.W2 <= 0:
            raise TrapezeError("the W2 base of Trapeze must be greater than 0")

    # cf Methods.Geometry.Trapeze.comp_length
    # -*-- coding: utf-8 -*
    def comp_length(self):
        """Returns the length of the Trapeze

        Parameters
        ----------
        self : Trapeze
            a Trapeze object


        Returns
        -------
        length: float
            Length of the surface [m]

        """
        # check if the Trapeze is correct
        self.check()
        lines = self.get_lines()
        length = 0
        for line in lines:
            length += line.comp_length()
        return length

    # cf Methods.Geometry.Trapeze.comp_point_ref
    def comp_point_ref(self, is_set=False):
        """Compute the point ref of the Surface

        Parameters
        ----------
        self : Trapeze
            A Trapeze object
        is_set: bool
            True to update the point_ref property

        Returns
        -------
        point_ref : complex
            the reference point of the surface
        """

        point_ref = self.point_ref
        if is_set:
            self.point_ref = point_ref
        return point_ref

    # cf Methods.Geometry.Trapeze.comp_surface
    def comp_surface(self):
        """Compute the Trapeze surface

        Parameters
        ----------
        self : Trapeze
            A Trapeze object

        Returns
        -------
        surf: float
            The Trapeze surface [m**2]

        """

        return self.height * (self.W2 + self.W1) / 2

    # cf Methods.Geometry.Trapeze.discretize
    # -*-- coding: utf-8 -*
    def discretize(self):
        """It returns the discretize version of the Trapeze

        Parameters
        ----------
        self : Trapeze
            a Trapeze object

        Returns
        -------
        point_list : list
            list of complex coordinate of the points
        """

        # check if the Trapeze is correct
        self.check()
        # getting lines that delimit the Trapeze
        lines = self.get_lines()
        point_list = list()
        for line in lines:
            point_list.extend(line.discretize())
            point_list.pop()
        return point_list

    # cf Methods.Geometry.Trapeze.get_lines
    def get_lines(self):
        """Returns the Lines that delimit the Trapeze

        Parameters
        ----------
        self : Trapeze
            a Trapeze object


        Returns
        -------
        line_list : list
            list of 4 segments

        """
        # Check if the Trapeze is correct
        self.check()
        Z_ref = self.point_ref
        H = self.height
        W1 = self.W1
        W2 = self.W2

        # The 4 points of the Trapeze object
        Z1 = (complex(-H / 2, W1 / 2) * np.exp(1j * (np.angle(Z_ref)))) + Z_ref
        Z2 = (complex(-H / 2, -W1 / 2) * np.exp(1j * (np.angle(Z_ref)))) + Z_ref
        Z3 = (complex(H / 2, -W2 / 2) * np.exp(1j * (np.angle(Z_ref)))) + Z_ref
        Z4 = (complex(H / 2, W2 / 2) * np.exp(1j * (np.angle(Z_ref)))) + Z_ref

        # The lines that delimit the Trapeze
        line1 = Segment(Z1, Z2)
        line2 = Segment(Z2, Z3)
        line3 = Segment(Z3, Z4)
        line4 = Segment(Z4, Z1)

        return [line1, line2, line3, line4]

    # cf Methods.Geometry.Trapeze.get_patches
    def get_patches(
        self, color=None, edgecolor=None, is_edge_only=False, linestyle=None
    ):
        """Returns the Trapeze Patch to be display in matplotlib

        Parameters
        ----------
        self : Trapeze
            a Trapeze object

        color :
            the color of the patch (Default value = PATCH_COLOR)
        edgecolor :
            the color of the patch's edges (Default value = PATCH_EDGE)
        is_edge_only: bool
            To set the transparancy of the face color to 0 and 1 for the edge color
        linestyle : str
            Line style of the edge {'-', '--', '-.', ':', '', (offset, on-off-seq), ...}

        Returns
        -------
        patch_list : list of matplotlib.patches.Polygon
            List of patches corresponding to the surface

        """

        # Set default color
        if edgecolor is None and not is_edge_only:
            edgecolor = self.PATCH_EDGE
        elif edgecolor is None and is_edge_only:
            edgecolor = self.PATCH_EDGE_ALPHA
        if is_edge_only:
            color = self.PATCH_COLOR_ALPHA
        if "--" in edgecolor:
            edgecolor = edgecolor.replace("-", "")
            linestyle = "--"

        # check if the Trapeze is correct*
        self.check()

        line_list = self.get_lines()
        Z_list = list()
        # For each Line discretize
        for line in line_list:
            Z_list.extend(list(line.discretize()))

        # abscissa coordinate
        Zr_list = list()
        # ordinate coordinate
        Zi_list = list()

        for ii in range(len(Z_list)):
            Zr_list.append(Z_list[ii].real)
            Zi_list.append(Z_list[ii].imag)
        point_list = list(zip(Zr_list, Zi_list))
        return [
            Polygon(
                point_list,
                closed=True,
                facecolor=color,
                edgecolor=edgecolor,
                linestyle=linestyle,
            )
        ]

    get_patches.__defaults__ = (
        get_patches.__defaults__[:0] + (PATCH_COLOR,) + get_patches.__defaults__[1:]
    )

    # cf Methods.Geometry.Trapeze.rotate
    def rotate(self, angle):
        """Rotate the surface

        Parameters
        ----------
        self : Trapeze
            a Trapeze Object

        angle : float
            angle for rotation [rad]


        Returns
        -------
        None
        """
        if angle == 0:
            return  # Nothing to do
        # check if the Trapeze is correct
        self.check()
        self.point_ref = self.point_ref * np.exp(1j * angle)

    # cf Methods.Geometry.Trapeze.translate
    def translate(self, Zt):
        """Translate the Trapeze

        Parameters
        ----------
        self : Trapeze
            a Trapeze object

        Zt : complex
            Complex value for translation

        Returns
        -------
        None
        """
        if Zt == 0:
            return  # Nothing to do
        # check if the Trapeze is correct
        self.check()
        self.point_ref += Zt

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self, height=1, W2=1, W1=1, point_ref=0, label="", init_dict=None, init_str=None
    ):
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
            if "height" in list(init_dict.keys()):
                height = init_dict["height"]
            if "W2" in list(init_dict.keys()):
                W2 = init_dict["W2"]
            if "W1" in list(init_dict.keys()):
                W1 = init_dict["W1"]
            if "point_ref" in list(init_dict.keys()):
                point_ref = init_dict["point_ref"]
            if "label" in list(init_dict.keys()):
                label = init_dict["label"]
        # Set the properties (value check and convertion are done in setter)
        self.height = height
        self.W2 = W2
        self.W1 = W1
        # Call Surface init
        super(Trapeze, self).__init__(point_ref=point_ref, label=label)
        # The class is frozen (in Surface init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        Trapeze_str = ""
        # Get the properties inherited from Surface
        Trapeze_str += super(Trapeze, self).__str__()
        Trapeze_str += "height = " + str(self.height) + linesep
        Trapeze_str += "W2 = " + str(self.W2) + linesep
        Trapeze_str += "W1 = " + str(self.W1) + linesep
        return Trapeze_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from Surface
        if not super(Trapeze, self).__eq__(other):
            return False
        if other.height != self.height:
            return False
        if other.W2 != self.W2:
            return False
        if other.W1 != self.W1:
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()

        # Check the properties inherited from Surface
        diff_list.extend(
            super(Trapeze, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
        if (
            other._height is not None
            and self._height is not None
            and np.isnan(other._height)
            and np.isnan(self._height)
        ):
            pass
        elif other._height != self._height:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._height)
                    + ", other="
                    + str(other._height)
                    + ")"
                )
                diff_list.append(name + ".height" + val_str)
            else:
                diff_list.append(name + ".height")
        if (
            other._W2 is not None
            and self._W2 is not None
            and np.isnan(other._W2)
            and np.isnan(self._W2)
        ):
            pass
        elif other._W2 != self._W2:
            if is_add_value:
                val_str = " (self=" + str(self._W2) + ", other=" + str(other._W2) + ")"
                diff_list.append(name + ".W2" + val_str)
            else:
                diff_list.append(name + ".W2")
        if (
            other._W1 is not None
            and self._W1 is not None
            and np.isnan(other._W1)
            and np.isnan(self._W1)
        ):
            pass
        elif other._W1 != self._W1:
            if is_add_value:
                val_str = " (self=" + str(self._W1) + ", other=" + str(other._W1) + ")"
                diff_list.append(name + ".W1" + val_str)
            else:
                diff_list.append(name + ".W1")
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from Surface
        S += super(Trapeze, self).__sizeof__()
        S += getsizeof(self.height)
        S += getsizeof(self.W2)
        S += getsizeof(self.W1)
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

        # Get the properties inherited from Surface
        Trapeze_dict = super(Trapeze, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        Trapeze_dict["height"] = self.height
        Trapeze_dict["W2"] = self.W2
        Trapeze_dict["W1"] = self.W1
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        Trapeze_dict["__class__"] = "Trapeze"
        return Trapeze_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        height_val = self.height
        W2_val = self.W2
        W1_val = self.W1
        point_ref_val = self.point_ref
        label_val = self.label
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(
            height=height_val,
            W2=W2_val,
            W1=W1_val,
            point_ref=point_ref_val,
            label=label_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.height = None
        self.W2 = None
        self.W1 = None
        # Set to None the properties inherited from Surface
        super(Trapeze, self)._set_None()

    def _get_height(self):
        """getter of height"""
        return self._height

    def _set_height(self, value):
        """setter of height"""
        check_var("height", value, "float", Vmin=0)
        self._height = value

    height = property(
        fget=_get_height,
        fset=_set_height,
        doc="""the height of the Trapeze

        :Type: float
        :min: 0
        """,
    )

    def _get_W2(self):
        """getter of W2"""
        return self._W2

    def _set_W2(self, value):
        """setter of W2"""
        check_var("W2", value, "float", Vmin=0)
        self._W2 = value

    W2 = property(
        fget=_get_W2,
        fset=_set_W2,
        doc="""the big base of Trapeze

        :Type: float
        :min: 0
        """,
    )

    def _get_W1(self):
        """getter of W1"""
        return self._W1

    def _set_W1(self, value):
        """setter of W1"""
        check_var("W1", value, "float", Vmin=0)
        self._W1 = value

    W1 = property(
        fget=_get_W1,
        fset=_set_W1,
        doc="""the small base of the Trapeze

        :Type: float
        :min: 0
        """,
    )
