# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Slot/SlotW24.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Slot/SlotW24
"""

# Inline fallback report:
# These methods remain imported because their source or imports cannot be safely moved into this class.
# - check: module uses a wildcard import whose names cannot be resolved safely
# - plot_schematics: import name 'Arc1' refers to different sources (.Arc1.Arc1 and ..Methods.Slot.SlotW24.plot_schematics.Arc1)

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
from ..Methods.Slot.SlotW24.check import check
from ..Methods.Slot.SlotW24.plot_schematics import plot_schematics
from .Segment import Segment
from .Arc1 import Arc1
from numpy import arcsin, exp, pi, angle, linspace, zeros, sin
from .SurfLine import SurfLine
from ..Functions.labels import WIND_LAB, DRAW_PROP_LAB

from numpy import isnan
from ._check import InitUnKnowClassError


class SlotW24(Slot):

    VERSION = 1
    IS_SYMMETRICAL = 1

    # cf Methods.Slot.SlotW24._comp_line_dict
    def _comp_line_dict(self):
        """Define a dictionnary of the lines to draw the slot
        If a line has begin==end, it is replaced by "None" (dict has always the same number of keys)

        Parameters
        ----------
        self : SlotW24
            A SlotW24 object

        Returns
        -------
        line_dict: dict
            Dictionnary of the slot lines (key: line name, value: line object)
        """

        point_dict = self._comp_point_coordinate()
        Z1 = point_dict["Z1"]
        Z2 = point_dict["Z2"]
        Z3 = point_dict["Z3"]
        Z4 = point_dict["Z4"]
        Zc = 0

        # Creation of curve
        line_dict = dict()
        line_dict["1-2"] = Segment(Z1, Z2)
        line_dict["2-3"] = Arc1(Z2, Z3, abs(Z2))
        line_dict["3-4"] = Segment(Z3, Z4)

        # Closing Arc (Rbo)
        line_dict["4-1"] = Arc1(Z4, Z1, -self.get_Rbo(), is_trigo_direction=False)

        # Closing Active part
        line_dict["1-4"] = Arc1(Z1, Z4, self.get_Rbo(), is_trigo_direction=True)

        return line_dict

    # cf Methods.Slot.SlotW24._comp_point_coordinate
    def _comp_point_coordinate(self):
        """Compute the point coordinates needed to plot the Slot.

        Parameters
        ----------
        self : SlotW24
            A SlotW24 object

        Returns
        -------
        point_dict: dict
            A dict of the slot point coordinates
        """
        Rbo = self.get_Rbo()

        # alpha_0 is the angle to have a W3 tooth width on the bore
        alpha_0 = float(arcsin(self.W3 / (2 * Rbo)))

        # comp point coordinate (in complex)
        Z0 = Rbo * exp(1j * 0)
        Z1t = Z0 * exp(1j * alpha_0)

        if self.is_outwards():
            Z2t = Z1t + self.H2
        else:  # inward slot
            Z2t = Z1t - self.H2
        hsp = pi / self.Zs

        point_dict = dict()
        # symetry
        point_dict["Z1"] = Z1t * exp(-1j * hsp)
        point_dict["Z2"] = Z2t * exp(-1j * hsp)
        point_dict["Z3"] = point_dict["Z2"].conjugate()
        point_dict["Z4"] = point_dict["Z1"].conjugate()
        return point_dict

    # cf Methods.Slot.SlotW24.build_geometry
    def build_geometry(self):
        """Compute the curve needed to plot the object.
        The ending point of a curve is the starting point of the next curve in
        the list

        Parameters
        ----------
        self : SlotW24
            A SlotW24 object

        Returns
        -------
        curve_list: list
            A list of 2 Segment and 1 Arc

        """

        line_dict = self._comp_line_dict()

        curve_list = [
            line_dict["1-2"],
            line_dict["2-3"],
            line_dict["3-4"],
        ]
        return [line for line in curve_list if line is not None]

    # cf Methods.Slot.SlotW24.build_geometry_active
    def build_geometry_active(self, Nrad, Ntan, alpha=0, delta=0):
        """Split the slot winding area in several zone

        Parameters
        ----------
        self : SlotW24
            A SlotW24 object
        Nrad : int
            Number of radial layer
        Ntan : int
            Number of tangentiel layer
        alpha : float
            Angle for rotation (Default value = 0) [rad]
        delta : Complex
            complex for translation (Default value = 0)

        Returns
        -------
        surf_list: list
            List of surface delimiting the winding zone

        """

        # get the name of the lamination
        lam_label = self.parent.get_label()

        point_dict = self._comp_point_coordinate()
        Z1 = point_dict["Z1"]
        Z2 = point_dict["Z2"]
        Z3 = point_dict["Z3"]
        Z4 = point_dict["Z4"]

        X = linspace(Z1, Z2, Nrad + 1)

        # Nrad+1 and Ntan+1 because 3 points => 2 zones
        Z = zeros((Nrad + 1, Ntan + 1), dtype=complex)
        for ii in range(Nrad + 1):
            Z[ii][:] = abs(X[ii]) * exp(
                1j * linspace(angle(X[ii]), angle(X[ii].conjugate()), Ntan + 1)
            )

        assert abs(Z[0][0] - Z1) < 1e-6
        assert abs(Z[Nrad][0] - Z2) < 1e-6
        assert abs(Z[0][Ntan] - Z4) < 1e-6
        assert abs(Z[Nrad][Ntan] - Z3) < 1e-6

        # We go thought the zone by Rad then Tan, starting by (0,0)
        surf_list = list()
        for jj in range(Ntan):  # jj from 0 to Ntan-1
            for ii in range(Nrad):  # ii from 0 to Nrad-1
                Z1 = Z[ii][jj]
                Z2 = Z[ii][jj + 1]
                Z3 = Z[ii + 1][jj + 1]
                Z4 = Z[ii + 1][jj]
                point_ref = (Z1 + Z2 + Z3 + Z4) / 4  # reference point of the surface
                # With one zone the order would be [Z7,Z4,Z5,Z6]
                curve_list = list()
                curve_list.append(Arc1(Z1, Z2, abs(Z1), is_trigo_direction=True))
                curve_list.append(
                    Segment(
                        Z2,
                        Z3,
                        prop_dict={DRAW_PROP_LAB: False},
                    )
                )
                curve_list.append(
                    Arc1(
                        Z3,
                        Z4,
                        -abs(Z3),
                        is_trigo_direction=False,
                        prop_dict={DRAW_PROP_LAB: False},
                    )
                )
                curve_list.append(
                    Segment(
                        Z4,
                        Z1,
                        prop_dict={DRAW_PROP_LAB: jj != 0},
                    )
                )
                surface = SurfLine(
                    line_list=curve_list,
                    label=lam_label
                    + "_"
                    + WIND_LAB
                    + "_R"
                    + str(ii)
                    + "-T"
                    + str(jj)
                    + "-S0",
                    point_ref=point_ref,
                )
                surf_list.append(surface)

        for surf in surf_list:
            surf.rotate(alpha)
            surf.translate(delta)
        return surf_list

    # cf Methods.Slot.SlotW24.check
    check = check

    # cf Methods.Slot.SlotW24.comp_angle_opening
    def comp_angle_opening(self):
        """Compute the average opening angle of the Slot

        Parameters
        ----------
        self : SlotW24
            A SlotW24 object

        Returns
        -------
        alpha: float
            Average opening angle of the slot [rad]

        """

        alpha = float(arcsin(self.W3 / (2 * self.get_Rbo())))
        return 2 * pi / self.Zs - 2 * alpha

    # cf Methods.Slot.SlotW24.comp_height
    def comp_height(self):
        """Compute the height of the Slot.
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotW24
            A SlotW24 object

        Returns
        -------
        Htot: float
            Height of the slot [m]

        """

        return self.comp_height_active()

    # cf Methods.Slot.SlotW24.comp_height_active
    def comp_height_active(self):
        """Compute the height of the winding area

        Parameters
        ----------
        self : SlotW24
            A SlotW24 object

        Returns
        -------
        Hwind: float
            Height of the winding area [m]

        """

        point_dict = self._comp_point_coordinate()
        Rbo = self.get_Rbo()
        return abs(Rbo - abs(point_dict["Z2"]))

    # cf Methods.Slot.SlotW24.comp_surface
    def comp_surface(self):
        """Compute the Slot total surface (by analytical computation).
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotW24
            A SlotW24 object

        Returns
        -------
        S: float
            Slot total surface [m**2]

        """

        return self.comp_surface_active()

    # cf Methods.Slot.SlotW24.comp_surface_active
    def comp_surface_active(self):
        """Compute the Slot inner surface for winding (by analytical computation)

        Parameters
        ----------
        self : SlotW24
            A SlotW24 object

        Returns
        -------
        Swind: float
            Slot inner surface for winding [m**2]

        """

        Rbo = self.get_Rbo()
        point_dict = self._comp_point_coordinate()

        if self.is_outwards():
            Rint = Rbo
            Rext = abs(point_dict["Z2"])
        else:
            Rint = abs(point_dict["Z2"])
            Rext = Rbo

        # Surface of a slot pitch
        Sring = (pi * Rext**2 - pi * Rint**2) * 1 / self.Zs

        # Tooth surface
        St = self.H2 * self.W3

        alpha_bore = 2 * arcsin(self.W3 / (2 * Rint))
        Sarc_bore = (Rint**2.0) / 2.0 * (alpha_bore - sin(alpha_bore))

        alpha_yoke = 2 * arcsin(self.W3 / (2 * Rext))
        Sarc_yoke = (Rext**2.0) / 2.0 * (alpha_yoke - sin(alpha_yoke))

        if self.is_outwards():
            return Sring - (St + Sarc_yoke - Sarc_bore)
        else:
            return Sring - (St + Sarc_yoke - Sarc_bore)

    # cf Methods.Slot.SlotW24.comp_surface_opening
    def comp_surface_opening(self):
        """Compute the Slot opening surface (by analytical computation).
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotW24
            A SlotW24 object

        Returns
        -------
        S: float
            Slot opening surface [m**2]

        """

        return 0

    # cf Methods.Slot.SlotW24.get_surface_active
    def get_surface_active(self, alpha=0, delta=0):
        """Return the full winding surface

        Parameters
        ----------
        self : SlotW24
            A SlotW24 object
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
            line_dict["1-2"],
            line_dict["2-3"],
            line_dict["3-4"],
            line_dict["4-1"],
        ]
        curve_list = [line for line in curve_list if line is not None]

        # Only the closing arc (4-1) needs to be drawn (in FEMM)
        for curve in curve_list[:-1]:
            if curve.prop_dict is None:
                curve.prop_dict = dict()
            curve.prop_dict.update({DRAW_PROP_LAB: False})

        # Create surface
        if self.is_outwards():
            Zmid = self.get_Rbo() + self.H2 / 2
        else:
            Zmid = self.get_Rbo() - self.H2 / 2
        label = self.parent.get_label() + "_" + WIND_LAB + "_R0-T0-S0"
        surface = SurfLine(line_list=curve_list, label=label, point_ref=Zmid)

        # Apply transformation
        surface.rotate(alpha)
        surface.translate(delta)

        return surface

    # cf Methods.Slot.SlotW24.get_surface_opening
    def get_surface_opening(self, alpha=0, delta=0):
        """Return the list of surfaces defining the opening area of the Slot

        Parameters
        ----------
        self : SlotW24
            A SlotW24 object
        alpha : float
            float number for rotation (Default value = 0) [rad]
        delta : complex
            complex number for translation (Default value = 0)

        Returns
        -------
        surf_list : list
            list of surfaces objects
        """

        # No opening surface in SlotW14
        return []

    # cf Methods.Slot.SlotW24.plot_schematics
    plot_schematics = plot_schematics
    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        W3=0.003,
        H2=0.003,
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
            if "W3" in list(init_dict.keys()):
                W3 = init_dict["W3"]
            if "H2" in list(init_dict.keys()):
                H2 = init_dict["H2"]
            if "Zs" in list(init_dict.keys()):
                Zs = init_dict["Zs"]
            if "wedge_mat" in list(init_dict.keys()):
                wedge_mat = init_dict["wedge_mat"]
            if "is_bore" in list(init_dict.keys()):
                is_bore = init_dict["is_bore"]
        # Set the properties (value check and convertion are done in setter)
        self.W3 = W3
        self.H2 = H2
        # Call Slot init
        super(SlotW24, self).__init__(Zs=Zs, wedge_mat=wedge_mat, is_bore=is_bore)
        # The class is frozen (in Slot init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        SlotW24_str = ""
        # Get the properties inherited from Slot
        SlotW24_str += super(SlotW24, self).__str__()
        SlotW24_str += "W3 = " + str(self.W3) + linesep
        SlotW24_str += "H2 = " + str(self.H2) + linesep
        return SlotW24_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from Slot
        if not super(SlotW24, self).__eq__(other):
            return False
        if other.W3 != self.W3:
            return False
        if other.H2 != self.H2:
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
            super(SlotW24, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
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
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from Slot
        S += super(SlotW24, self).__sizeof__()
        S += getsizeof(self.W3)
        S += getsizeof(self.H2)
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
        SlotW24_dict = super(SlotW24, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        SlotW24_dict["W3"] = self.W3
        SlotW24_dict["H2"] = self.H2
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        SlotW24_dict["__class__"] = "SlotW24"
        return SlotW24_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        W3_val = self.W3
        H2_val = self.H2
        Zs_val = self.Zs
        if self.wedge_mat is None:
            wedge_mat_val = None
        else:
            wedge_mat_val = self.wedge_mat.copy()
        is_bore_val = self.is_bore
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(
            W3=W3_val,
            H2=H2_val,
            Zs=Zs_val,
            wedge_mat=wedge_mat_val,
            is_bore=is_bore_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.W3 = None
        self.H2 = None
        # Set to None the properties inherited from Slot
        super(SlotW24, self)._set_None()

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
        doc="""Teeth width

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
