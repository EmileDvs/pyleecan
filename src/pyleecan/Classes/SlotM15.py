# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Slot/SlotM15.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Slot/SlotM15
"""

# Inline fallback report:
# These methods remain imported because their source or imports cannot be safely moved into this class.
# - plot_schematics: import name 'Arc1' refers to different sources (.Arc1.Arc1 and ..Methods.Slot.SlotM15.plot_schematics.Arc1)

from os import linesep
from sys import getsizeof
from logging import getLogger
from ._check import check_var, raise_
from ..Functions.get_logger import get_logger
from ..Functions.save import save
from ..Functions.load import load_init_dict
from ..Functions.Load.import_class import import_class
from copy import deepcopy
from .Slot import Slot

# Import all class method
# Try/catch to remove unnecessary dependencies in unused method
from ..Methods.Slot.SlotM15.plot_schematics import plot_schematics
from numpy import arcsin, exp, sin, pi
from .Segment import Segment
from .Arc1 import Arc1
from ..Methods.Slot.Slot import SlotCheckError
from .SurfLine import SurfLine

from numpy import isnan
from ._check import InitUnKnowClassError


class SlotM15(Slot):
    """single magnet with polar base and curved-top shape and parallel sides"""

    VERSION = 1
    IS_SYMMETRICAL = 1

    # cf Methods.Slot.SlotM15._comp_point_coordinate
    def _comp_point_coordinate(self):
        """Compute the point coordinates needed to plot the Slot.

        Parameters
        ----------
        self : SlotM15
            A SlotM15 object

        Returns
        -------
        point_dict: dict
            A dict of the slot coordinates
        """

        Rbo = self.get_Rbo()

        Z1 = Rbo * exp(-1j * self.W0 / 2)

        # alpha_lim = 2 * arcsin(self.W1 * 0.5 / self.Rtopm)  # Angle of the top arc
        # H_top_arc = self.Rtopm * (1 - cos(alpha_lim / 2))  # Height of the top arc
        if self.is_outwards():
            Z2 = (Rbo + self.H0) * exp(-1j * self.W0 / 2)
        else:  # inward slot
            Z2 = (Rbo - self.H0) * exp(-1j * self.W0 / 2)

        alpha_M = float(arcsin(self.W1 / (2 * abs(Z2))))
        ZM1 = abs(Z2) * exp(-1j * alpha_M)
        if self.is_outwards():
            ZM0 = abs(Z2) - self.H1
            Zc = ZM0 + self.Rtopm
        else:  # inward slot
            ZM0 = abs(Z2) + self.H1
            Zc = ZM0 - self.Rtopm

        sign = -1 if self.is_outwards() else 1
        x = abs(Z2) - sign * (
            -self.H1 + self.Rtopm - (self.Rtopm**2 - self.W1**2 / 4) ** 0.5
        )
        ZM2 = x - 1j * self.W1 / 2

        point_dict = dict()
        point_dict["Z1"] = Z1
        point_dict["Z2"] = Z2
        point_dict["ZM1"] = ZM1
        point_dict["ZM2"] = ZM2
        point_dict["ZM0"] = ZM0
        point_dict["Zc"] = Zc
        # symetry
        point_dict["Z3"] = Z2.conjugate()
        point_dict["Z4"] = Z1.conjugate()
        point_dict["ZM3"] = ZM2.conjugate()
        point_dict["ZM4"] = ZM1.conjugate()

        return point_dict

    # cf Methods.Slot.SlotM15.build_geometry
    def build_geometry(self):
        """Compute the curve (Line) needed to plot the Slot.
        The ending point of a curve is the starting point of the next curve in
        the list

        Parameters
        ----------
        self : SlotM15
            A SlotM15 object

        Returns
        -------
        curve_list: list
            A list of 3 Segments

        """
        Rbo = self.get_Rbo()
        point_dict = self._comp_point_coordinate()
        Z1 = point_dict["Z1"]
        Z2 = point_dict["Z2"]
        Z3 = point_dict["Z3"]
        Z4 = point_dict["Z4"]

        # Creation of curve
        curve_list = list()
        if self.H0 > 0:
            curve_list.append(Segment(Z1, Z2))
        if self.is_outwards():
            curve_list.append(Arc1(Z2, Z3, Rbo + self.H0, is_trigo_direction=True))
        else:
            curve_list.append(Arc1(Z2, Z3, Rbo - self.H0, is_trigo_direction=True))
        if self.H0 > 0:
            curve_list.append(Segment(Z3, Z4))

        return curve_list

    # cf Methods.Slot.SlotM15.check
    def check(self):
        """Check that the SlotM13 object is correct

        Parameters
        ----------
        self : SlotM15
            A SlotM15 object

        Returns
        -------
        None
        """
        Rbo = self.get_Rbo()

        # conversion W0 rad -> m
        W0_m = 2 * (Rbo - self.H0) * sin(self.W0 / 2)

        if W0_m < self.W1:
            raise SlotCheckError("You must have W1 <= W0")
        if 2 * self.Rtopm < self.W1:
            raise SlotCheckError("You must have W1 <= 2*Rtopm")

    # cf Methods.Slot.SlotM15.comp_angle_opening
    def comp_angle_opening(self):
        """Compute the average opening angle of the Slot

        Parameters
        ----------
        self : SlotM15
            A SlotM15 object

        Returns
        -------
        alpha: float
            Average opening angle of the slot [rad]

        """

        return self.W0

    # cf Methods.Slot.SlotM15.comp_height
    def comp_height(self):
        """Compute the height of the Slot.
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotM15
            A SlotM15 object

        Returns
        -------
        Htot: float
            Height of the slot [m]

        """

        return self.H0

    # cf Methods.Slot.SlotM15.comp_height_active
    def comp_height_active(self):
        """Compute the height of the active area

        Parameters
        ----------
        self : SlotM15
            A SlotM15 object

        Returns
        -------
        Hwind: float
            Height of the active area [m]

        """

        return self.H1

    # cf Methods.Slot.SlotM15.comp_surface
    def comp_surface(self):
        """Compute the Slot total surface (by analytical computation).
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotM15
            A SlotM15 object

        Returns
        -------
        S: float
            Slot total surface [m**2]

        """

        point_dict = self._comp_point_coordinate()
        Z1 = point_dict["Z1"]
        Z2 = point_dict["Z2"]

        R1 = abs(Z1)
        R2 = abs(Z2)

        S1 = pi * R1**2 * (self.W0 / (2 * pi))
        S2 = pi * R2**2 * (self.W0 / (2 * pi))

        return abs(S1 - S2)

    # cf Methods.Slot.SlotM15.comp_surface_active
    def comp_surface_active(self):
        """Compute the Slot active inner surface (by analytical computation)

        Parameters
        ----------
        self : SlotM15
            A SlotM15 object

        Returns
        -------
        Swind: float
            Slot active inner surface [m**2]

        """

        # "Main rectangle"
        point_dict = self._comp_point_coordinate()
        ZM1 = point_dict["ZM1"]
        ZM2 = point_dict["ZM2"]
        S1 = abs(ZM1 - ZM2) * self.W1

        # Top Arc
        alpha = 2 * float(arcsin(self.W1 / (2 * self.Rtopm)))
        Sarc = (self.Rtopm**2.0) / 2.0 * (alpha - sin(alpha))

        # Bottom polar to remove
        alpha = 2 * float(arcsin(self.W1 / (2 * abs(ZM1))))
        Sarc2 = (abs(ZM1) ** 2.0) / 2.0 * (alpha - sin(alpha))

        return S1 + Sarc - Sarc2

    # cf Methods.Slot.SlotM15.get_surface_active
    def get_surface_active(self, alpha=0, delta=0):
        """Return the full active surface

        Parameters
        ----------
        self : SlotM15
            A SlotM15 object
        alpha : float
            float number for rotation (Default value = 0) [rad]
        delta : complex
            complex number for translation (Default value = 0)

        Returns
        -------
        surf_act: Surface
            Surface corresponding to the Active Area
        """

        # get the name of the lamination
        st = self.get_name_lam()

        point_dict = self._comp_point_coordinate()
        ZM0 = point_dict["ZM0"]
        ZM1 = point_dict["ZM1"]
        ZM2 = point_dict["ZM2"]
        ZM3 = point_dict["ZM3"]
        ZM4 = point_dict["ZM4"]

        curve_list = list()
        curve_list.append(Segment(ZM1, ZM2))
        if self.is_outwards():
            curve_list.append(Arc1(ZM2, ZM3, -self.Rtopm, is_trigo_direction=False))
        else:
            curve_list.append(Arc1(ZM2, ZM3, self.Rtopm))
        curve_list.append(Segment(ZM3, ZM4))
        curve_list.append(Arc1(ZM4, ZM1, -abs(ZM4), is_trigo_direction=False))

        Zmid = (abs(ZM1) + abs(ZM3)) / 2  # ref. point on x-axis with respective radius

        surface = SurfLine(
            line_list=curve_list, label="Wind_" + st + "_R0_T0_S0", point_ref=Zmid
        )

        # Apply transformation
        surface.rotate(alpha)
        surface.translate(delta)

        return surface

    # cf Methods.Slot.SlotM15.is_airgap_active
    def is_airgap_active(self):
        """Return True if a part or the full active surface is in the airgap

        Parameters
        ----------
        self : SlotM15
            A SlotM15 object

        Returns
        -------
        is_airgap_active : bool
            True if a part or the full active surface is in the airgap
        """

        return self.comp_height_active() > self.H0

    # cf Methods.Slot.SlotM15.plot_schematics
    plot_schematics = plot_schematics
    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        W0=0.0122,
        H0=0.001,
        W1=0.0122,
        H1=0.001,
        Rtopm=0.001,
        Zs=36,
        wedge_mat=None,
        is_bore=True,
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
            if "W0" in list(init_dict.keys()):
                W0 = init_dict["W0"]
            if "H0" in list(init_dict.keys()):
                H0 = init_dict["H0"]
            if "W1" in list(init_dict.keys()):
                W1 = init_dict["W1"]
            if "H1" in list(init_dict.keys()):
                H1 = init_dict["H1"]
            if "Rtopm" in list(init_dict.keys()):
                Rtopm = init_dict["Rtopm"]
            if "Zs" in list(init_dict.keys()):
                Zs = init_dict["Zs"]
            if "wedge_mat" in list(init_dict.keys()):
                wedge_mat = init_dict["wedge_mat"]
            if "is_bore" in list(init_dict.keys()):
                is_bore = init_dict["is_bore"]
        # Set the properties (value check and convertion are done in setter)
        self.W0 = W0
        self.H0 = H0
        self.W1 = W1
        self.H1 = H1
        self.Rtopm = Rtopm
        # Call Slot init
        super(SlotM15, self).__init__(Zs=Zs, wedge_mat=wedge_mat, is_bore=is_bore)
        # The class is frozen (in Slot init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        SlotM15_str = ""
        # Get the properties inherited from Slot
        SlotM15_str += super(SlotM15, self).__str__()
        SlotM15_str += "W0 = " + str(self.W0) + linesep
        SlotM15_str += "H0 = " + str(self.H0) + linesep
        SlotM15_str += "W1 = " + str(self.W1) + linesep
        SlotM15_str += "H1 = " + str(self.H1) + linesep
        SlotM15_str += "Rtopm = " + str(self.Rtopm) + linesep
        return SlotM15_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from Slot
        if not super(SlotM15, self).__eq__(other):
            return False
        if other.W0 != self.W0:
            return False
        if other.H0 != self.H0:
            return False
        if other.W1 != self.W1:
            return False
        if other.H1 != self.H1:
            return False
        if other.Rtopm != self.Rtopm:
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()

        # Check the properties inherited from Slot
        diff_list.extend(
            super(SlotM15, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
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
            other._Rtopm is not None
            and self._Rtopm is not None
            and isnan(other._Rtopm)
            and isnan(self._Rtopm)
        ):
            pass
        elif other._Rtopm != self._Rtopm:
            if is_add_value:
                val_str = (
                    " (self=" + str(self._Rtopm) + ", other=" + str(other._Rtopm) + ")"
                )
                diff_list.append(name + ".Rtopm" + val_str)
            else:
                diff_list.append(name + ".Rtopm")
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from Slot
        S += super(SlotM15, self).__sizeof__()
        S += getsizeof(self.W0)
        S += getsizeof(self.H0)
        S += getsizeof(self.W1)
        S += getsizeof(self.H1)
        S += getsizeof(self.Rtopm)
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

        # Get the properties inherited from Slot
        SlotM15_dict = super(SlotM15, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        SlotM15_dict["W0"] = self.W0
        SlotM15_dict["H0"] = self.H0
        SlotM15_dict["W1"] = self.W1
        SlotM15_dict["H1"] = self.H1
        SlotM15_dict["Rtopm"] = self.Rtopm
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        SlotM15_dict["__class__"] = "SlotM15"
        return SlotM15_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        W0_val = self.W0
        H0_val = self.H0
        W1_val = self.W1
        H1_val = self.H1
        Rtopm_val = self.Rtopm
        Zs_val = self.Zs
        if self.wedge_mat is None:
            wedge_mat_val = None
        else:
            wedge_mat_val = self.wedge_mat.copy()
        is_bore_val = self.is_bore
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(
            W0=W0_val,
            H0=H0_val,
            W1=W1_val,
            H1=H1_val,
            Rtopm=Rtopm_val,
            Zs=Zs_val,
            wedge_mat=wedge_mat_val,
            is_bore=is_bore_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.W0 = None
        self.H0 = None
        self.W1 = None
        self.H1 = None
        self.Rtopm = None
        # Set to None the properties inherited from Slot
        super(SlotM15, self)._set_None()

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
        doc="""Slot isthmus angular width.

        :Type: float
        :min: 0
        """,
    )

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
        doc="""Slot isthmus height.

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
        doc="""Magnet Height

        :Type: float
        :min: 0
        """,
    )

    def _get_Rtopm(self):
        """getter of Rtopm"""
        return self._Rtopm

    def _set_Rtopm(self, value):
        """setter of Rtopm"""
        check_var("Rtopm", value, "float", Vmin=0)
        self._Rtopm = value

    Rtopm = property(
        fget=_get_Rtopm,
        fset=_set_Rtopm,
        doc="""Radius of the magnet top

        :Type: float
        :min: 0
        """,
    )
