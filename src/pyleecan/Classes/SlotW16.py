# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Slot/SlotW16.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Slot/SlotW16
"""

# Inline fallback report:
# These methods remain imported because their source or imports cannot be safely moved into this class.
# - plot_schematics: import name 'Arc1' refers to different sources (.Arc1.Arc1 and ..Methods.Slot.SlotW16.plot_schematics.Arc1)

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
from ..Methods.Slot.SlotW16.plot_schematics import plot_schematics
from .Arc1 import Arc1
from .Segment import Segment
from numpy import arcsin, exp, pi, sqrt
from ..Methods.Slot.SlotW16 import S16OutterError, S16AlphaT
from ..Functions.Geometry.inter_circle_circle import inter_circle_circle
from ..Functions.labels import WIND_LAB, DRAW_PROP_LAB, SOP_LAB
from .SurfLine import SurfLine

from numpy import isnan
from ._check import InitUnKnowClassError


class SlotW16(Slot):

    VERSION = 1
    IS_SYMMETRICAL = 1

    # cf Methods.Slot.SlotW16._comp_line_dict
    def _comp_line_dict(self):
        """Define a dictionnary of the lines to draw the slot
        If a line has begin==end, it is replaced by "None" (dict has always the same number of keys)

        Parameters
        ----------
        self : SlotW16
            A SlotW16 object

        Returns
        -------
        line_dict: dict
            Dictionnary of the slot lines (key: line name, value: line object)
        """

        Rbo = self.get_Rbo()

        point_dict = self._comp_point_coordinate()
        Z1 = point_dict["Z1"]
        Z2 = point_dict["Z2"]
        Z3 = point_dict["Z3"]
        Z4 = point_dict["Z4"]
        Z5 = point_dict["Z5"]
        Z6 = point_dict["Z6"]
        Z7 = point_dict["Z7"]
        Z8 = point_dict["Z8"]
        Z9 = point_dict["Z9"]
        Z10 = point_dict["Z10"]

        # Creation of curve
        line_dict = dict()
        line_dict["1-2"] = Segment(Z1, Z2)
        line_dict["2-3"] = Arc1(Z2, Z3, -Rbo + self.H0, is_trigo_direction=False)
        line_dict["3-4"] = Arc1(Z3, Z4, -self.R1, is_trigo_direction=False)
        line_dict["4-5"] = Segment(Z4, Z5)
        line_dict["5-6"] = Arc1(
            Z5, Z6, Rbo - self.H0 - self.H2, is_trigo_direction=True
        )
        line_dict["6-7"] = Segment(Z6, Z7)
        line_dict["7-8"] = Arc1(Z7, Z8, -self.R1, is_trigo_direction=False)
        line_dict["8-9"] = Arc1(Z8, Z9, -Rbo + self.H0, is_trigo_direction=False)
        line_dict["9-10"] = Segment(Z9, Z10)

        # Closing Arc (Rbo)
        line_dict["10-1"] = Arc1(Z10, Z1, -self.get_Rbo(), is_trigo_direction=False)

        # Closing Active part
        line_dict["9-2"] = Arc1(
            begin=Z9,
            end=Z2,
            radius=-abs(Z9),
            is_trigo_direction=False,
        )
        line_dict["2-9"] = Arc1(
            begin=Z2,
            end=Z9,
            radius=abs(Z9),
            is_trigo_direction=True,
        )

        return line_dict

    # cf Methods.Slot.SlotW16._comp_point_coordinate
    def _comp_point_coordinate(self):
        """Compute the point coordinates needed to plot the Slot.

        Parameters
        ----------
        self : SlotW16
            A SlotW16 object

        Returns
        -------
        point_dict: dict
            A dict of the slot point coordinates
        """

        Rbo = self.get_Rbo()

        hsp = pi / self.Zs  # Half slot pitch

        if self.is_outwards():
            raise S16OutterError("Slot Type 16 can't be used on outer lamination")

        # ZXt => Complex coordinate in the tooth ref
        Z1 = Rbo * exp(-1j * self.W0 / 2)
        Z2 = (Rbo - self.H0) * exp(-1j * self.W0 / 2)

        # Tooth angular width

        alphaT = 2 * arcsin(self.W3 * 0.5 / (Rbo - self.H0 - self.H2))
        Z5 = (Rbo - self.H0 - self.H2) * exp(-1j * (hsp - alphaT / 2))
        R2 = Rbo - self.H0
        R3 = Rbo - self.H0 - self.R1

        #  In the ref: O-tooth as axis
        # Z3 on cercle O and radius R2 => (x3t**2+y3t**2) = R2**2
        # Zc on cercle O and radius R3 => (xct**2+yct**2) = R3**2
        # Z3 on cercle Zc => (xct-x3t)**2+(yct-y3t)**2 = R1**2
        # y4t = y5t = yct - R1
        # x4t = xct
        # O, Z3, Zc align => -y3t*xct+x3t*yct = 0

        y5t = -self.W3 / 2
        y4t = y5t
        yct = y5t - self.R1

        # xct = sqrt(R3**2-yct**2) and yct = y5t + R1

        xct = sqrt(R3**2 - yct**2)
        x4t = xct
        Z4t = x4t + 1j * y4t
        Zct = xct + 1j * yct
        Z3t = inter_circle_circle(Zct, self.R1, 0, R2)[0]
        Z4 = Z4t * exp(-1j * hsp)
        Z3 = Z3t * exp(-1j * hsp)

        point_dict = dict()

        # symetry
        point_dict["Z1"] = Z1
        point_dict["Z2"] = Z2
        point_dict["Z3"] = Z3
        point_dict["Z4"] = Z4
        point_dict["Z5"] = Z5
        point_dict["Z6"] = Z5.conjugate()
        point_dict["Z7"] = Z4.conjugate()
        point_dict["Z8"] = Z3.conjugate()
        point_dict["Z9"] = Z2.conjugate()
        point_dict["Z10"] = Z1.conjugate()

        # Compute center
        point_dict["Zc1"] = Zct * exp(-1j * hsp)
        point_dict["Zc2"] = point_dict["Zc1"].conjugate()

        return point_dict

    # cf Methods.Slot.SlotW16.build_geometry
    def build_geometry(self):
        """Compute the curve (Line) needed to plot the Slot.
        The ending point of a curve is the starting point of the next curve in
        the list

        Parameters
        ----------
        self : SlotW16
            A SlotW16 object

        Returns
        -------
        curve_list: llist
            A list of 4 Segment and 5 Arc

        """

        line_dict = self._comp_line_dict()

        curve_list = [
            line_dict["1-2"],
            line_dict["2-3"],
            line_dict["3-4"],
            line_dict["4-5"],
            line_dict["5-6"],
            line_dict["6-7"],
            line_dict["7-8"],
            line_dict["8-9"],
            line_dict["9-10"],
        ]
        return [line for line in curve_list if line is not None]

    # cf Methods.Slot.SlotW16.check
    def check(self):
        """Check that the SlotW16 object is correct

        Parameters
        ----------
        self : SlotW16
            A SlotW16 object

        Returns
        -------
        None

        Raises
        -------
        S16OutterError
            Slot 16 must be on internal lamination only
        """
        if self.is_outwards():
            raise S16OutterError("Slot 16 must be on internal lamination only")

        # Check W3 at min radius
        Rbo = self.get_Rbo()
        sp = 2 * pi / self.Zs  # slot pitch
        alphaT = 2 * arcsin(self.W3 * 0.5 / (Rbo - self.H0 - self.H2))

        if alphaT >= sp:
            raise S16AlphaT(
                "Tooth is larger than the slot pitch angle: reduce W3, H2 or Zs"
            )

    # cf Methods.Slot.SlotW16.comp_angle_opening
    def comp_angle_opening(self):
        """Compute the average opening angle of the Slot

        Parameters
        ----------
        self : SlotW16
            A SlotW16 object

        Returns
        -------
        alpha: float
            Average opening angle of the slot [rad]

        """

        return self.W0

    # cf Methods.Slot.SlotW16.comp_height
    def comp_height(self):
        """Compute the height of the Slot.
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotW16
            A SlotW16 object

        Returns
        -------
        Htot: float
            Height of the slot [m]

        """

        return self.H0 + self.H2

    # cf Methods.Slot.SlotW16.comp_height_active
    def comp_height_active(self):
        """Compute the height of the winding area

        Parameters
        ----------
        self : SlotW16
            A SlotW16 object

        Returns
        -------
        Hwind: float
            Height of the winding area [m]

        """

        return self.H2

    # cf Methods.Slot.SlotW16.comp_surface
    def comp_surface(self):
        """Compute the Slot total surface (by analytical computation).
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotW16
            A SlotW16 object

        Returns
        -------
        S: float
            Slot total surface [m**2]

        """
        return self.comp_surface_active() + self.comp_surface_opening()

    # cf Methods.Slot.SlotW16.comp_surface_opening
    def comp_surface_opening(self):
        """Compute the Slot opening surface (by analytical computation).
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotW16
            A SlotW16 object

        Returns
        -------
        S: float
            Slot total surface [m**2]

        """
        Rbo = self.get_Rbo()

        S0 = (pi * Rbo**2 - pi * (Rbo - self.H0) ** 2) * self.W0 / (2 * pi)

        return S0

    # cf Methods.Slot.SlotW16.get_surface_active
    def get_surface_active(self, alpha=0, delta=0):
        """Return the full winding surface

        Parameters
        ----------
        self : SlotW16
            A SlotW16 object
        alpha : float
            float number for rotation (Default value = 0) [rad]
        delta : complex
            complex number for translation (Default value = 0)

        Returns
        -------
        surf_wind: Surface
            Surface corresponding to the Winding Area
        """

        # Create curve list
        line_dict = self._comp_line_dict()
        curve_list = [
            line_dict["2-3"],
            line_dict["3-4"],
            line_dict["4-5"],
            line_dict["5-6"],
            line_dict["6-7"],
            line_dict["7-8"],
            line_dict["8-9"],
            line_dict["9-2"],
        ]
        curve_list = [line for line in curve_list if line is not None]

        # Only the closing arc (9-2) needs to be drawn (in FEMM)
        for curve in curve_list[:-1]:
            if curve.prop_dict is None:
                curve.prop_dict = dict()
            curve.prop_dict.update({DRAW_PROP_LAB: False})

        # Create surface
        Zmid = self.get_Rbo() - self.H0 - self.H2 / 2
        label = self.parent.get_label() + "_" + WIND_LAB + "_R0-T0-S0"
        surface = SurfLine(line_list=curve_list, label=label, point_ref=Zmid)

        # Apply transformation
        surface.rotate(alpha)
        surface.translate(delta)

        return surface

    # cf Methods.Slot.SlotW16.get_surface_opening
    def get_surface_opening(self, alpha=0, delta=0):
        """Return the list of surfaces defining the opening area of the Slot

        Parameters
        ----------
        self : SlotW16
            A SlotW16 object
        alpha : float
            float number for rotation (Default value = 0) [rad]
        delta : complex
            complex number for translation (Default value = 0)

        Returns
        -------
        surf_list : list
            list of surfaces objects
        """

        # H0=0 no opening
        if self.H0 == 0:
            return []

        # Create curve list
        line_dict = self._comp_line_dict()
        curve_list = [
            line_dict["1-2"],
            line_dict["2-9"],
            line_dict["9-10"],
            line_dict["10-1"],
        ]
        curve_list = [line for line in curve_list if line is not None]

        # Only the closing arc (13-1) needs to be drawn (in FEMM)
        for curve in curve_list[:-1]:
            if curve.prop_dict is None:
                curve.prop_dict = dict()
            curve.prop_dict.update({DRAW_PROP_LAB: False})

        # Create surface
        if self.is_outwards():
            Zmid = self.get_Rbo() + self.H0 / 2
        else:
            Zmid = self.get_Rbo() - self.H0 / 2
        label = self.parent.get_label() + "_" + SOP_LAB + "_R0-T0-S0"
        surface = SurfLine(line_list=curve_list, label=label, point_ref=Zmid)

        # Apply transformation
        surface.rotate(alpha)
        surface.translate(delta)

        return [surface]

    # cf Methods.Slot.SlotW16.plot_schematics
    plot_schematics = plot_schematics
    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        W0=0.0122,
        W3=0.0122,
        H0=0.001,
        H2=0.0122,
        R1=0.001,
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
            if "W3" in list(init_dict.keys()):
                W3 = init_dict["W3"]
            if "H0" in list(init_dict.keys()):
                H0 = init_dict["H0"]
            if "H2" in list(init_dict.keys()):
                H2 = init_dict["H2"]
            if "R1" in list(init_dict.keys()):
                R1 = init_dict["R1"]
            if "Zs" in list(init_dict.keys()):
                Zs = init_dict["Zs"]
            if "wedge_mat" in list(init_dict.keys()):
                wedge_mat = init_dict["wedge_mat"]
            if "is_bore" in list(init_dict.keys()):
                is_bore = init_dict["is_bore"]
        # Set the properties (value check and convertion are done in setter)
        self.W0 = W0
        self.W3 = W3
        self.H0 = H0
        self.H2 = H2
        self.R1 = R1
        # Call Slot init
        super(SlotW16, self).__init__(Zs=Zs, wedge_mat=wedge_mat, is_bore=is_bore)
        # The class is frozen (in Slot init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        SlotW16_str = ""
        # Get the properties inherited from Slot
        SlotW16_str += super(SlotW16, self).__str__()
        SlotW16_str += "W0 = " + str(self.W0) + linesep
        SlotW16_str += "W3 = " + str(self.W3) + linesep
        SlotW16_str += "H0 = " + str(self.H0) + linesep
        SlotW16_str += "H2 = " + str(self.H2) + linesep
        SlotW16_str += "R1 = " + str(self.R1) + linesep
        return SlotW16_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from Slot
        if not super(SlotW16, self).__eq__(other):
            return False
        if other.W0 != self.W0:
            return False
        if other.W3 != self.W3:
            return False
        if other.H0 != self.H0:
            return False
        if other.H2 != self.H2:
            return False
        if other.R1 != self.R1:
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
            super(SlotW16, self).compare(
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
            other._W3 is not None
            and self._W3 is not None
            and isnan(other._W3)
            and isnan(self._W3)
        ):
            pass
        elif other._W3 != self._W3:
            if is_add_value:
                val_str = " (self=" + str(self._W3) + ", other=" + str(other._W3) + ")"
                diff_list.append(name + ".W3" + val_str)
            else:
                diff_list.append(name + ".W3")
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
        if (
            other._R1 is not None
            and self._R1 is not None
            and isnan(other._R1)
            and isnan(self._R1)
        ):
            pass
        elif other._R1 != self._R1:
            if is_add_value:
                val_str = " (self=" + str(self._R1) + ", other=" + str(other._R1) + ")"
                diff_list.append(name + ".R1" + val_str)
            else:
                diff_list.append(name + ".R1")
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from Slot
        S += super(SlotW16, self).__sizeof__()
        S += getsizeof(self.W0)
        S += getsizeof(self.W3)
        S += getsizeof(self.H0)
        S += getsizeof(self.H2)
        S += getsizeof(self.R1)
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
        SlotW16_dict = super(SlotW16, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        SlotW16_dict["W0"] = self.W0
        SlotW16_dict["W3"] = self.W3
        SlotW16_dict["H0"] = self.H0
        SlotW16_dict["H2"] = self.H2
        SlotW16_dict["R1"] = self.R1
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        SlotW16_dict["__class__"] = "SlotW16"
        return SlotW16_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        W0_val = self.W0
        W3_val = self.W3
        H0_val = self.H0
        H2_val = self.H2
        R1_val = self.R1
        Zs_val = self.Zs
        if self.wedge_mat is None:
            wedge_mat_val = None
        else:
            wedge_mat_val = self.wedge_mat.copy()
        is_bore_val = self.is_bore
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(
            W0=W0_val,
            W3=W3_val,
            H0=H0_val,
            H2=H2_val,
            R1=R1_val,
            Zs=Zs_val,
            wedge_mat=wedge_mat_val,
            is_bore=is_bore_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.W0 = None
        self.W3 = None
        self.H0 = None
        self.H2 = None
        self.R1 = None
        # Set to None the properties inherited from Slot
        super(SlotW16, self)._set_None()

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

    def _get_W3(self):
        """getter of W3"""
        return self._W3

    def _set_W3(self, value):
        """setter of W3"""
        check_var("W3", value, "float", Vmin=0)
        self._W3 = value

    W3 = property(
        fget=_get_W3,
        fset=_set_W3,
        doc="""Tooth width

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
        doc="""Slot height

        :Type: float
        :min: 0
        """,
    )

    def _get_R1(self):
        """getter of R1"""
        return self._R1

    def _set_R1(self, value):
        """setter of R1"""
        check_var("R1", value, "float", Vmin=0)
        self._R1 = value

    R1 = property(
        fget=_get_R1,
        fset=_set_R1,
        doc="""Top radius

        :Type: float
        :min: 0
        """,
    )
