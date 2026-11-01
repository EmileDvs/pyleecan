# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Slot/HoleM52R.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Slot/HoleM52R
"""

# Inline fallback report:
# These methods remain imported because their source or imports cannot be safely moved into this class.
# - check: module uses a wildcard import whose names cannot be resolved safely
# - comp_magnetization_dict: import name 'Segment' refers to different sources (.Segment.Segment and pyleecan.Classes.Segment.Segment)
# - plot_schematics: import name 'Arc1' refers to different sources (.Arc1.Arc1 and ..Methods.Slot.HoleM52R.plot_schematics.Arc1)

from os import linesep
from sys import getsizeof
from logging import getLogger
from ._check import check_var, raise_
from ..Functions.get_logger import get_logger
from ..Functions.save import save
from ..Functions.load import load_init_dict
from ..Functions.Load.import_class import import_class
from copy import deepcopy
from .HoleMag import HoleMag

# Import all class method
# Try/catch to remove unnecessary dependencies in unused method
from ..Methods.Slot.HoleM52R.check import check
from ..Methods.Slot.HoleM52R.comp_magnetization_dict import comp_magnetization_dict
from ..Methods.Slot.HoleM52R.plot_schematics import plot_schematics
from numpy import exp, arcsin, pi
from .Arc1 import Arc1
from .Segment import Segment
from .SurfLine import SurfLine
from ..Functions.labels import HOLEM_LAB

from numpy import isnan
from ._check import InitUnKnowClassError


class HoleM52R(HoleMag):
    """Rectangular slot for buried magnet"""

    VERSION = 1
    IS_SYMMETRICAL = 1

    # cf Methods.Slot.HoleM52R._comp_point_coordinate
    def _comp_point_coordinate(self):
        """Compute the point coordinates needed to plot the Slot.

        Parameters
        ----------
        self : HoleM52R
            A HoleM52R object

        Returns
        -------
        point_dict: dict
            A dict of the slot coordinates
        """

        Rext = self.get_Rext()

        alpha1 = self.comp_alpha()
        Z1 = (Rext - self.H0) * exp(1j * alpha1 / 2)  # top corner of void
        Z9 = (Rext - self.H0) * exp(-1j * alpha1 / 2)

        Z0 = (Z1 + Z9) / 2  # middle of magnet at top
        Z5 = Z0 - self.H1  # middle of magnet at bottom

        Z4 = Z5 + 1j * self.W0 / 2  # bottom corner of magnet hole
        Z6 = Z4.conjugate()

        Z3 = Z4 + self.H2
        Z7 = Z3.conjugate()

        Z2 = Z3 + 1j * self.W1  # bottom corner of void
        Z8 = Z2.conjugate()

        Z11 = Z3 + (self.H1 - self.H2)  # top corner of magnet
        Z10 = Z7 + (self.H1 - self.H2)

        point_dict = dict()
        point_dict["Z1"] = Z1
        point_dict["Z2"] = Z2
        point_dict["Z3"] = Z3
        point_dict["Z4"] = Z4
        point_dict["Z5"] = Z5
        point_dict["Z6"] = Z6
        point_dict["Z7"] = Z7
        point_dict["Z8"] = Z8
        point_dict["Z9"] = Z9
        point_dict["Z10"] = Z10
        point_dict["Z11"] = Z11

        return point_dict

    # cf Methods.Slot.HoleM52R.build_geometry
    def build_geometry(self, alpha=0, delta=0, is_simplified=False):
        """Compute the curve (Line) needed to plot the Slot.
        The ending point of a curve is the starting point of the next curve in
        the list

        Parameters
        ----------
        self : HoleM52
            A HoleM52 object
        alpha : float
            Angle to rotate the slot (Default value = 0) [rad]
        delta : complex
            Complex to translate the slot (Default value = 0)
        is_simplified : bool
           True to avoid line superposition

        Returns
        -------
        surf_list: list
            List of SurfLine needed to draw the HoleM51

        """
        # Get correct label for surfaces
        lam_label = self.parent.get_label()
        R_id, surf_type = self.get_R_id()
        vent_label = lam_label + "_" + surf_type + "_R" + str(R_id) + "-"
        mag_label = lam_label + "_" + HOLEM_LAB + "_R" + str(R_id) + "-"

        point_dict = self._comp_point_coordinate()
        Z1 = point_dict["Z1"]
        Z2 = point_dict["Z2"]
        Z3 = point_dict["Z3"]
        Z4 = point_dict["Z4"]
        Z6 = point_dict["Z6"]
        Z7 = point_dict["Z7"]
        Z8 = point_dict["Z8"]
        Z9 = point_dict["Z9"]
        Z10 = point_dict["Z10"]
        Z11 = point_dict["Z11"]

        # modify points for void radius in case
        is_radius = False
        if self.R0 > 0:
            if self.R0 < (self.H1 - self.H2) and self.R0 < self.W1:
                is_radius = True
                Z1R = Z1 - 1j * self.R0
                Z1L = Z1 - self.R0
                Z9L = Z9 + 1j * self.R0
                Z9R = Z9 - self.R0

            else:
                self.get_logger().warning("Radius R0 enforced to 0.")

        # Creation of the air curve
        curve_list = list()
        if is_radius:
            curve_list.append(Arc1(Z1R, Z1L, self.R0))
        curve_list.append(Segment(Z1L if is_radius else Z1, Z2))
        curve_list.append(Segment(Z2, Z3))
        curve_list.append(Segment(Z3, Z11))
        curve_list.append(Segment(Z11, Z1R if is_radius else Z1))
        point_ref = (Z1 + Z2 + Z3 + Z11) / 4
        S1 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # Creation of the magnet curve
        curve_list = list()
        if is_simplified:
            curve_list.append(Segment(Z3, Z11))
            curve_list.append(Segment(Z7, Z10))
        else:
            curve_list.append(Segment(Z4, Z11))
            curve_list.append(Segment(Z11, Z10))
            curve_list.append(Segment(Z10, Z6))
            curve_list.append(Segment(Z6, Z4))
        point_ref = (Z11 + Z4 + Z6 + Z10) / 4
        S2 = SurfLine(
            line_list=curve_list, label=mag_label + "T0-S0", point_ref=point_ref
        )

        # Creation of the second air curve
        curve_list = list()
        curve_list.append(Segment(Z7, Z8))
        curve_list.append(Segment(Z8, Z9R if is_radius else Z9))
        if is_radius:
            curve_list.append(Arc1(Z9R, Z9L, self.R0))
        curve_list.append(Segment(Z9L if is_radius else Z9, Z10))
        curve_list.append(Segment(Z10, Z7))
        point_ref = (Z7 + Z8 + Z9 + Z10) / 4
        S3 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # Area with no magnet (S1 + S2 + S3)
        curve_list = list()
        if is_radius:
            curve_list.append(Arc1(Z1R, Z1L, self.R0))
        curve_list.append(Segment(Z1L if is_radius else Z1, Z2))
        curve_list.append(Segment(Z2, Z3))
        if self.H2 > 0:
            curve_list.append(Segment(Z3, Z4))
        curve_list.append(Segment(Z4, Z6))
        if self.H2 > 0:
            curve_list.append(Segment(Z6, Z7))
        curve_list.append(Segment(Z7, Z8))
        curve_list.append(Segment(Z8, Z9R if is_radius else Z9))
        if is_radius:
            curve_list.append(Arc1(Z9R, Z9L, self.R0))
        curve_list.append(Segment(Z9L if is_radius else Z9, Z1R if is_radius else Z1))
        point_ref = (Z11 + Z4 + Z6 + Z10) / 4
        S4 = SurfLine(line_list=curve_list, point_ref=point_ref)

        if self.magnet_0:
            S1.label = vent_label + "T0-S0"  # Hole
            S3.label = vent_label + "T1-S0"  # Hole
            surf_list = [S1, S2, S3]
        else:
            S4.label = vent_label + "T0-S0"  # Hole
            surf_list = [S4]

        # Apply the transformations
        for surf in surf_list:
            surf.rotate(alpha)
            surf.translate(delta)

        return surf_list

    # cf Methods.Slot.HoleM52R.check
    check = check

    # cf Methods.Slot.HoleM52R.comp_alpha
    def comp_alpha(self):
        """The opening angle incl. W1 width and a Rext - H0 radius

        Parameters
        ----------
        self : HoleM52
            A HoleM52 object

        Returns
        -------
        alpha: float
            Angle between P1 and P9 (cf schematics) [rad]

        """
        Rext = self.get_Rext()

        alpha = 2 * arcsin((2 * self.W1 + self.W0) / (2 * (Rext - self.H0)))

        return alpha

    # cf Methods.Slot.HoleM52R.comp_magnetization_dict
    comp_magnetization_dict = comp_magnetization_dict

    # cf Methods.Slot.HoleM52R.comp_radius
    def comp_radius(self):
        """Compute the radius of the min and max circle that contains the hole

        Parameters
        ----------
        self : HoleM52
            A HoleM52R object

        Returns
        -------
        (Rmin,Rmax): tuple
            Radius of the circle that contains the hole [m]

        """

        Rext = self.get_Rext()

        Rmax = Rext - self.H0

        alpha = self.comp_alpha()
        Z1 = (Rext - self.H0) * exp(1j * alpha / 2)
        Z5 = Z1.real - self.H1
        Rmin = abs(Z5)

        return (Rmin, Rmax)

    # cf Methods.Slot.HoleM52R.comp_surface
    def comp_surface(self):
        """Compute the surface of the Hole

        Parameters
        ----------
        self : HoleM52R
            A HoleM52R object

        Returns
        -------
        S: float
            Surface of the Hole. [m**2]

        """

        Smag = self.comp_surface_magnets()
        # one side rectangular air area
        Srect = self.W1 * (self.H1 - self.H2) - (4 - pi) * self.R0**2 / 4

        return Smag + 2 * Srect

    # cf Methods.Slot.HoleM52R.comp_surface_magnet_id
    def comp_surface_magnet_id(self, index):
        """Compute the surface of the hole magnet of the corresponding index

        Parameters
        ----------
        self : HoleM52R
            A HoleM52R object
        index : int
            Index of the magnet to compute the surface

        Returns
        -------
        Smag: float
            Surface of the Magnet [m**2]
        """
        return self.W0 * self.H1 if index == 0 and self.magnet_0 else 0

    # cf Methods.Slot.HoleM52R.get_height_magnet_id
    def get_height_magnet_id(self, index):
        """Get the height of the hole magnet of the corresponding index

        Parameters
        ----------
        self : HoleM52R
            A HoleM52R object
        index : int
            Index of the magnet to get the height

        Returns
        -------
        Hmag: float
            Height of the Magnet [m]
        """

        if index == 0 and self.magnet_0:
            return self.H1
        return 0

    # cf Methods.Slot.HoleM52R.has_magnet
    def has_magnet(self):
        """Return if the Hole has magnets

        Parameters
        ----------
        self : HoleM52R
            A HoleM52R object

        Returns
        -------
        has_magnet : bool
            True if the magnets are not None
        """

        return self.magnet_0 is not None

    # cf Methods.Slot.HoleM52R.plot_schematics
    plot_schematics = plot_schematics

    # cf Methods.Slot.HoleM52R.remove_magnet
    def remove_magnet(self):
        """Remove the magnet (set to None) of the Hole

        Parameters
        ----------
        self : HoleM52R
            a HoleM52R object
        """

        self.magnet_0 = None

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        H0=0.003,
        W0=0.003,
        H1=0,
        W1=0.001,
        H2=0.02,
        magnet_0=-1,
        R0=0,
        Zh=36,
        mat_void=-1,
        magnetization_dict_offset=None,
        Alpha0=0,
        init_dict=None,
        init_str=None,
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
            if "H0" in list(init_dict.keys()):
                H0 = init_dict["H0"]
            if "W0" in list(init_dict.keys()):
                W0 = init_dict["W0"]
            if "H1" in list(init_dict.keys()):
                H1 = init_dict["H1"]
            if "W1" in list(init_dict.keys()):
                W1 = init_dict["W1"]
            if "H2" in list(init_dict.keys()):
                H2 = init_dict["H2"]
            if "magnet_0" in list(init_dict.keys()):
                magnet_0 = init_dict["magnet_0"]
            if "R0" in list(init_dict.keys()):
                R0 = init_dict["R0"]
            if "Zh" in list(init_dict.keys()):
                Zh = init_dict["Zh"]
            if "mat_void" in list(init_dict.keys()):
                mat_void = init_dict["mat_void"]
            if "magnetization_dict_offset" in list(init_dict.keys()):
                magnetization_dict_offset = init_dict["magnetization_dict_offset"]
            if "Alpha0" in list(init_dict.keys()):
                Alpha0 = init_dict["Alpha0"]
        # Set the properties (value check and convertion are done in setter)
        self.H0 = H0
        self.W0 = W0
        self.H1 = H1
        self.W1 = W1
        self.H2 = H2
        self.magnet_0 = magnet_0
        self.R0 = R0
        # Call HoleMag init
        super(HoleM52R, self).__init__(
            Zh=Zh,
            mat_void=mat_void,
            magnetization_dict_offset=magnetization_dict_offset,
            Alpha0=Alpha0,
        )
        # The class is frozen (in HoleMag init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        HoleM52R_str = ""
        # Get the properties inherited from HoleMag
        HoleM52R_str += super(HoleM52R, self).__str__()
        HoleM52R_str += "H0 = " + str(self.H0) + linesep
        HoleM52R_str += "W0 = " + str(self.W0) + linesep
        HoleM52R_str += "H1 = " + str(self.H1) + linesep
        HoleM52R_str += "W1 = " + str(self.W1) + linesep
        HoleM52R_str += "H2 = " + str(self.H2) + linesep
        if self.magnet_0 is not None:
            tmp = self.magnet_0.__str__().replace(linesep, linesep + "\t").rstrip("\t")
            HoleM52R_str += "magnet_0 = " + tmp
        else:
            HoleM52R_str += "magnet_0 = None" + linesep + linesep
        HoleM52R_str += "R0 = " + str(self.R0) + linesep
        return HoleM52R_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from HoleMag
        if not super(HoleM52R, self).__eq__(other):
            return False
        if other.H0 != self.H0:
            return False
        if other.W0 != self.W0:
            return False
        if other.H1 != self.H1:
            return False
        if other.W1 != self.W1:
            return False
        if other.H2 != self.H2:
            return False
        if other.magnet_0 != self.magnet_0:
            return False
        if other.R0 != self.R0:
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()

        # Check the properties inherited from HoleMag
        diff_list.extend(
            super(HoleM52R, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
        if (
            other._H0 is not None
            and self._H0 is not None
            and isnan(other._H0)
            and isnan(self._H0)
        ):
            pass
        elif other._H0 != self._H0:
            if is_add_value:
                val_str = " (self=" + str(self._H0) + ", other=" + str(other._H0) + ")"
                diff_list.append(name + ".H0" + val_str)
            else:
                diff_list.append(name + ".H0")
        if (
            other._W0 is not None
            and self._W0 is not None
            and isnan(other._W0)
            and isnan(self._W0)
        ):
            pass
        elif other._W0 != self._W0:
            if is_add_value:
                val_str = " (self=" + str(self._W0) + ", other=" + str(other._W0) + ")"
                diff_list.append(name + ".W0" + val_str)
            else:
                diff_list.append(name + ".W0")
        if (
            other._H1 is not None
            and self._H1 is not None
            and isnan(other._H1)
            and isnan(self._H1)
        ):
            pass
        elif other._H1 != self._H1:
            if is_add_value:
                val_str = " (self=" + str(self._H1) + ", other=" + str(other._H1) + ")"
                diff_list.append(name + ".H1" + val_str)
            else:
                diff_list.append(name + ".H1")
        if (
            other._W1 is not None
            and self._W1 is not None
            and isnan(other._W1)
            and isnan(self._W1)
        ):
            pass
        elif other._W1 != self._W1:
            if is_add_value:
                val_str = " (self=" + str(self._W1) + ", other=" + str(other._W1) + ")"
                diff_list.append(name + ".W1" + val_str)
            else:
                diff_list.append(name + ".W1")
        if (
            other._H2 is not None
            and self._H2 is not None
            and isnan(other._H2)
            and isnan(self._H2)
        ):
            pass
        elif other._H2 != self._H2:
            if is_add_value:
                val_str = " (self=" + str(self._H2) + ", other=" + str(other._H2) + ")"
                diff_list.append(name + ".H2" + val_str)
            else:
                diff_list.append(name + ".H2")
        if (other.magnet_0 is None and self.magnet_0 is not None) or (
            other.magnet_0 is not None and self.magnet_0 is None
        ):
            diff_list.append(name + ".magnet_0 None mismatch")
        elif self.magnet_0 is not None:
            diff_list.extend(
                self.magnet_0.compare(
                    other.magnet_0,
                    name=name + ".magnet_0",
                    ignore_list=ignore_list,
                    is_add_value=is_add_value,
                )
            )
        if (
            other._R0 is not None
            and self._R0 is not None
            and isnan(other._R0)
            and isnan(self._R0)
        ):
            pass
        elif other._R0 != self._R0:
            if is_add_value:
                val_str = " (self=" + str(self._R0) + ", other=" + str(other._R0) + ")"
                diff_list.append(name + ".R0" + val_str)
            else:
                diff_list.append(name + ".R0")
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from HoleMag
        S += super(HoleM52R, self).__sizeof__()
        S += getsizeof(self.H0)
        S += getsizeof(self.W0)
        S += getsizeof(self.H1)
        S += getsizeof(self.W1)
        S += getsizeof(self.H2)
        S += getsizeof(self.magnet_0)
        S += getsizeof(self.R0)
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

        # Get the properties inherited from HoleMag
        HoleM52R_dict = super(HoleM52R, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        HoleM52R_dict["H0"] = self.H0
        HoleM52R_dict["W0"] = self.W0
        HoleM52R_dict["H1"] = self.H1
        HoleM52R_dict["W1"] = self.W1
        HoleM52R_dict["H2"] = self.H2
        if self.magnet_0 is None:
            HoleM52R_dict["magnet_0"] = None
        else:
            HoleM52R_dict["magnet_0"] = self.magnet_0.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs
            )
        HoleM52R_dict["R0"] = self.R0
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        HoleM52R_dict["__class__"] = "HoleM52R"
        return HoleM52R_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        H0_val = self.H0
        W0_val = self.W0
        H1_val = self.H1
        W1_val = self.W1
        H2_val = self.H2
        if self.magnet_0 is None:
            magnet_0_val = None
        else:
            magnet_0_val = self.magnet_0.copy()
        R0_val = self.R0
        Zh_val = self.Zh
        if self.mat_void is None:
            mat_void_val = None
        else:
            mat_void_val = self.mat_void.copy()
        if self.magnetization_dict_offset is None:
            magnetization_dict_offset_val = None
        else:
            magnetization_dict_offset_val = self.magnetization_dict_offset.copy()
        Alpha0_val = self.Alpha0
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(
            H0=H0_val,
            W0=W0_val,
            H1=H1_val,
            W1=W1_val,
            H2=H2_val,
            magnet_0=magnet_0_val,
            R0=R0_val,
            Zh=Zh_val,
            mat_void=mat_void_val,
            magnetization_dict_offset=magnetization_dict_offset_val,
            Alpha0=Alpha0_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.H0 = None
        self.W0 = None
        self.H1 = None
        self.W1 = None
        self.H2 = None
        if self.magnet_0 is not None:
            self.magnet_0._set_None()
        self.R0 = None
        # Set to None the properties inherited from HoleMag
        super(HoleM52R, self)._set_None()

    def _get_H0(self):
        """getter of H0"""
        return self._H0

    def _set_H0(self, value):
        """setter of H0"""
        check_var("H0", value, "float", Vmin=0)
        self._H0 = value

    H0 = property(
        fget=_get_H0,
        fset=_set_H0,
        doc="""Slot depth

        :Type: float
        :min: 0
        """,
    )

    def _get_W0(self):
        """getter of W0"""
        return self._W0

    def _set_W0(self, value):
        """setter of W0"""
        check_var("W0", value, "float", Vmin=0)
        self._W0 = value

    W0 = property(
        fget=_get_W0,
        fset=_set_W0,
        doc="""Magnet width

        :Type: float
        :min: 0
        """,
    )

    def _get_H1(self):
        """getter of H1"""
        return self._H1

    def _set_H1(self, value):
        """setter of H1"""
        check_var("H1", value, "float", Vmin=0)
        self._H1 = value

    H1 = property(
        fget=_get_H1,
        fset=_set_H1,
        doc="""Magnet height

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
        doc="""Void width

        :Type: float
        :min: 0
        """,
    )

    def _get_H2(self):
        """getter of H2"""
        return self._H2

    def _set_H2(self, value):
        """setter of H2"""
        check_var("H2", value, "float", Vmin=0)
        self._H2 = value

    H2 = property(
        fget=_get_H2,
        fset=_set_H2,
        doc="""Additional depth for the magnet

        :Type: float
        :min: 0
        """,
    )

    def _get_magnet_0(self):
        """getter of magnet_0"""
        return self._magnet_0

    def _set_magnet_0(self, value):
        """setter of magnet_0"""
        if isinstance(value, str):  # Load from file
            try:
                value = load_init_dict(value)[1]
            except Exception as e:
                self.get_logger().error(
                    "Error while loading " + value + ", setting None instead"
                )
                value = None
        if isinstance(value, dict) and "__class__" in value:
            class_obj = import_class(
                "pyleecan.Classes", value.get("__class__"), "magnet_0"
            )
            value = class_obj(init_dict=value)
        elif type(value) is int and value == -1:  # Default constructor
            Magnet = import_class("pyleecan.Classes", "Magnet", "magnet_0")
            value = Magnet()
        check_var("magnet_0", value, "Magnet")
        self._magnet_0 = value

        if self._magnet_0 is not None:
            self._magnet_0.parent = self

    magnet_0 = property(
        fget=_get_magnet_0,
        fset=_set_magnet_0,
        doc="""Magnet of the hole

        :Type: Magnet
        """,
    )

    def _get_R0(self):
        """getter of R0"""
        return self._R0

    def _set_R0(self, value):
        """setter of R0"""
        check_var("R0", value, "float", Vmin=0)
        self._R0 = value

    R0 = property(
        fget=_get_R0,
        fset=_set_R0,
        doc="""Void corner radius

        :Type: float
        :min: 0
        """,
    )
