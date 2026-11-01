# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Slot/SlotW22.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Slot/SlotW22
"""

# Inline fallback report:
# These methods remain imported because their source or imports cannot be safely moved into this class.
# - check: module uses a wildcard import whose names cannot be resolved safely
# - plot_schematics: import name 'Arc1' refers to different sources (.Arc1.Arc1 and ..Methods.Slot.SlotW22.plot_schematics.Arc1)

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
from ..Methods.Slot.SlotW22.check import check
from ..Methods.Slot.SlotW22.plot_schematics import plot_schematics
from .Arc2 import Arc2
from .Arc1 import Arc1
from .Segment import Segment
from numpy import exp, linspace, meshgrid, pi
from .SurfLine import SurfLine
from ..Functions.labels import WIND_LAB, DRAW_PROP_LAB, SOP_LAB

from numpy import isnan
from ._check import InitUnKnowClassError


class SlotW22(Slot):
    """semi-closed orthoradial without fillet without wedge"""

    VERSION = 1
    IS_SYMMETRICAL = 1

    # cf Methods.Slot.SlotW22._comp_line_dict
    def _comp_line_dict(self):
        """Define a dictionnary of the lines to draw the slot
        If a line has begin==end, it is replaced by "None" (dict has always the same number of keys)

        Parameters
        ----------
        self : SlotW22
            A SlotW22 object

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
        Z5 = point_dict["Z5"]
        Z6 = point_dict["Z6"]
        Z7 = point_dict["Z7"]
        Z8 = point_dict["Z8"]
        Zc = 0

        # Creation of curve
        line_dict = dict()
        if self.H0 > 0:
            line_dict["1-2"] = Segment(Z1, Z2)
        else:
            line_dict["1-2"] = None

        if self.W2 != self.W0:
            line_dict["2-3"] = Arc2(Z2, Zc, -(self.W2 - self.W0) / 2)
        else:
            line_dict["2-3"] = None
        line_dict["3-4"] = Segment(Z3, Z4)
        line_dict["4-5"] = Arc2(Z4, Zc, self.W2)
        line_dict["5-6"] = Segment(Z5, Z6)
        if self.W2 != self.W0:
            line_dict["6-7"] = Arc2(Z6, Zc, -(self.W2 - self.W0) / 2)
        else:
            line_dict["6-7"] = None

        if self.H0 > 0:
            line_dict["7-8"] = Segment(Z7, Z8)
        else:
            line_dict["7-8"] = None

        # Closing Arc (Rbo)
        line_dict["8-1"] = Arc1(Z8, Z1, -self.get_Rbo(), is_trigo_direction=False)

        # Closing Active part
        line_dict["2-7"] = Arc1(
            begin=Z2,
            end=Z7,
            radius=abs(Z7),
            is_trigo_direction=True,
        )
        line_dict["7-2"] = Arc1(
            begin=Z7,
            end=Z2,
            radius=-abs(Z7),
            is_trigo_direction=False,
        )

        return line_dict

    # cf Methods.Slot.SlotW22._comp_point_coordinate
    def _comp_point_coordinate(self):
        """Compute the point coordinates needed to plot the Slot.

        Parameters
        ----------
        self : SlotW22
            A SlotW22 object

        Returns
        -------
        point_dict: dict
            A dict of the slot point coordinates
        """
        Rbo = self.get_Rbo()

        # comp point coordinate (in complex)
        Z1 = Rbo * exp(-1j * self.W0 / 2)
        if self.is_outwards():
            R1 = Rbo + self.H0
            R2 = Rbo + self.H0 + self.H2
        else:  # inward slot
            R1 = Rbo - self.H0
            R2 = Rbo - self.H0 - self.H2
        Z2 = R1 * exp(-1j * self.W0 / 2.0)
        Z3 = R1 * exp(-1j * self.W2 / 2.0)
        Z4 = R2 * exp(-1j * self.W2 / 2.0)

        point_dict = dict()
        # symetry
        point_dict["Z1"] = Z1
        point_dict["Z2"] = Z2
        point_dict["Z3"] = Z3
        point_dict["Z4"] = Z4
        point_dict["Z5"] = Z4.conjugate()
        point_dict["Z6"] = Z3.conjugate()
        point_dict["Z7"] = Z2.conjugate()
        point_dict["Z8"] = Z1.conjugate()
        return point_dict

    # cf Methods.Slot.SlotW22.build_geometry
    def build_geometry(self):
        """Compute the curve (Segment) needed to plot the object.
        The ending point of a curve is the starting point of the next curve in
        the list

        Parameters
        ----------
        self : SlotW22
            A SlotW22 object

        Returns
        -------
        curve_list: llist
            A list of 5 Segment and 3 Arc2

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
        ]
        return [line for line in curve_list if line is not None]

    # cf Methods.Slot.SlotW22.build_geometry_active
    def build_geometry_active(self, Nrad, Ntan, alpha=0, delta=0):
        """Split the slot winding area in several zone

        Parameters
        ----------
        self : SlotW22
            A SlotW22 object
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
        surf_list:
            List of surface delimiting the winding zone

        """

        # get the name of the lamination
        lam_label = self.parent.get_label()

        Rbo = self.get_Rbo()

        # Polar Meshgrid
        if self.is_outwards():
            r = linspace(Rbo + self.H0, Rbo + self.H0 + self.H2, Nrad + 1)
        else:
            r = linspace(Rbo - self.H0, Rbo - self.H0 - self.H2, Nrad + 1)

        theta = linspace(-self.W2 / 2.0, self.W2 / 2.0, Ntan + 1)
        Z = meshgrid(r, theta)

        Z = Z[0] * exp(1j * Z[1])
        Z = Z.T
        # if self.is_outwards():
        #     assert Z[0][0] == (Rbo + self.H0) * exp(-1j * self.W2 * 0.5)  # Z6
        #     assert Z[Nrad][0] == (Rbo + self.H0 + self.H2) * exp(-1j * self.W2 * 0.5)  # Z5
        #     assert Z[0][Ntan] == (Rbo + self.H0) * exp(1j * self.W2 * 0.5)  # Z3
        #     assert Z[Nrad][Ntan] == (Rbo + self.H0 + self.H2) * exp(
        #         1j * self.W2 * 0.5
        #     )  # Z4
        # else:
        #     assert Z[0][0] == (Rbo - self.H0) * exp(-1j * self.W2 * 0.5)  # Z6
        #     assert Z[Nrad][0] == (Rbo - self.H0 - self.H2) * exp(-1j * self.W2 * 0.5)  # Z5
        #     assert Z[0][Ntan] == (Rbo - self.H0) * exp(1j * self.W2 * 0.5)  # Z3
        #     assert Z[Nrad][Ntan] == (Rbo - self.H0 - self.H2) * exp(
        #         1j * self.W2 * 0.5
        #     )  # Z4

        surf_list = list()
        for jj in range(Ntan):  # jj from 0 to Ntan-1
            for ii in range(Nrad):  # ii from 0 to Nrad-1
                Z1 = Z[ii][jj]
                Z2 = Z[ii][jj + 1]
                Z3 = Z[ii + 1][jj + 1]
                Z4 = Z[ii + 1][jj]
                point_ref = (
                    Z[ii][jj] + Z[ii][jj + 1] + Z[ii + 1][jj + 1] + Z[ii + 1][jj]
                ) / 4  # the reference point of the surface
                curve_list = list()
                curve_list.append(
                    Arc1(
                        Z1,
                        Z2,
                        abs(Z1),
                        is_trigo_direction=True,
                    )
                )
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

        # Correct bottom line for particular case (cf Tests\Validation\Magnetics\test_FEMM_fast_draw.py)
        if (Ntan == 2 and Nrad == 1) and self.W0 != self.W2:
            # Cut Ox- surface
            arc_to_cut = surf_list[0].line_list[0]
            arc1, arc2 = arc_to_cut.split_line(Z1=0, Z2=Rbo * exp(-1j * self.W0 / 2))
            surf_list[0].line_list = [arc1[0], arc2[0]] + surf_list[0].line_list[1:]
            surf_list[0].line_list[1].prop_dict = {DRAW_PROP_LAB: False}
            # Cut Ox+ surface
            arc_to_cut = surf_list[1].line_list[0]
            arc1, arc2 = arc_to_cut.split_line(Z1=0, Z2=Rbo * exp(1j * self.W0 / 2))
            surf_list[1].line_list = [arc1[0], arc2[0]] + surf_list[1].line_list[1:]
            surf_list[1].line_list[0].prop_dict = {DRAW_PROP_LAB: False}

        for surf in surf_list:
            surf.rotate(alpha)
            surf.translate(delta)
        return surf_list

    # cf Methods.Slot.SlotW22.check
    check = check

    # cf Methods.Slot.SlotW22.comp_angle_opening
    def comp_angle_opening(self):
        """Compute the average opening angle of the Slot

        Parameters
        ----------
        self : SlotW22
            A SlotW22 object

        Returns
        -------
        alpha: float
            Average opening angle of the slot [rad]

        """

        return self.W0

    # cf Methods.Slot.SlotW22.comp_height
    def comp_height(self):
        """Compute the height of the Slot.
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotW22
            A SlotW22 object

        Returns
        -------
        Htot: float
            Height of the slot [m]

        """

        return self.H0 + self.H2

    # cf Methods.Slot.SlotW22.comp_height_active
    def comp_height_active(self):
        """Compute the height of the winding area

        Parameters
        ----------
        self : SlotW22
            A SlotW22 object

        Returns
        -------
        Hwind: float
            Height of the winding area [m]

        """

        return self.H2

    # cf Methods.Slot.SlotW22.comp_surface
    def comp_surface(self):
        """Compute the Slot total surface (by analytical computation).
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotW22
            A SlotW22 object

        Returns
        -------
        S: float
            Slot total surface [m**2]

        """
        return self.comp_surface_active() + self.comp_surface_opening()

    # cf Methods.Slot.SlotW22.comp_surface_active
    def comp_surface_active(self):
        """Compute the Slot inner surface for winding (by analytical computation)

        Parameters
        ----------
        self : SlotW22
            A SlotW22 object

        Returns
        -------
        Swind: float
            Slot inner surface for winding [m**2]

        """
        Rbo = self.get_Rbo()

        if self.is_outwards():
            # Surface of the external disk
            Sext = ((self.H2 + self.H0 + Rbo) ** 2) * pi

            # Surface of the internal disk
            Sint = ((self.H0 + Rbo) ** 2) * pi
        else:
            # Surface of the external disk
            Sext = ((Rbo - self.H0) ** 2) * pi

            # Surface of the internal disk
            Sint = ((Rbo - self.H2 - self.H0) ** 2) * pi

        # Surface of the ring
        Sring = Sext - Sint

        # Only an W2 angle of the ring
        return Sring * self.W2 / (2 * pi)

    # cf Methods.Slot.SlotW22.comp_surface_opening
    def comp_surface_opening(self):
        """Compute the Slot opening surface (by analytical computation).
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotW22
            A SlotW22 object

        Returns
        -------
        S: float
            Slot opening surface [m**2]

        """
        Rbo = self.get_Rbo()

        # Computation of isthmus surface
        if self.is_outwards():
            # Surface of the external disk
            Sext = ((self.H0 + Rbo) ** 2) * pi

            # Surface of the internal disk
            Sint = (Rbo**2) * pi
        else:
            # Surface of the external disk
            Sext = (Rbo**2) * pi

            # Surface of the internal disk
            Sint = ((Rbo - self.H0) ** 2) * pi
        # Surface of the ring
        Sring = Sext - Sint

        # Only an W0 angle of the ring
        return Sring * self.W0 / (2 * pi)

    # cf Methods.Slot.SlotW22.get_surface_active
    def get_surface_active(self, alpha=0, delta=0):
        """Return the full winding surface

        Parameters
        ----------
        self : SlotW22
            A SlotW22 object
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
            line_dict["7-2"],
        ]
        curve_list = [line for line in curve_list if line is not None]

        # Only the closing arc (7-2) needs to be drawn (in FEMM)
        for curve in curve_list[:-1]:
            if curve.prop_dict is None:
                curve.prop_dict = dict()
            curve.prop_dict.update({DRAW_PROP_LAB: False})

        # Create surface
        label = self.parent.get_label() + "_" + WIND_LAB + "_R0-T0-S0"
        if self.is_outwards():
            Zmid = self.get_Rbo() + self.H0 + self.H2 / 2
        else:
            Zmid = self.get_Rbo() - self.H0 - self.H2 / 2
        surface = SurfLine(line_list=curve_list, label=label, point_ref=Zmid)

        # Apply transformation
        surface.rotate(alpha)
        surface.translate(delta)

        return surface

    # cf Methods.Slot.SlotW22.get_surface_opening
    def get_surface_opening(self, alpha=0, delta=0):
        """Return the list of surfaces defining the opening area of the Slot

        Parameters
        ----------
        self : SlotW22
            A SlotW22 object
        alpha : float
            float number for rotation (Default value = 0) [rad]
        delta : complex
            complex number for translation (Default value = 0)

        Returns
        -------
        surf_list : list
            list of surfaces objects
        """

        # H0=0 => No opening
        if self.H0 == 0:
            return []

        # Create curve list
        line_dict = self._comp_line_dict()
        curve_list = [
            line_dict["1-2"],
            line_dict["2-7"],
            line_dict["7-8"],
            line_dict["8-1"],
        ]
        curve_list = [line for line in curve_list if line is not None]

        # Only the closing arc (8-1) needs to be drawn (in FEMM)
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

    # cf Methods.Slot.SlotW22.plot_schematics
    plot_schematics = plot_schematics
    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        W0=0.043633,
        H0=0.006,
        H2=0.04,
        W2=0.08725,
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
            if "H2" in list(init_dict.keys()):
                H2 = init_dict["H2"]
            if "W2" in list(init_dict.keys()):
                W2 = init_dict["W2"]
            if "Zs" in list(init_dict.keys()):
                Zs = init_dict["Zs"]
            if "wedge_mat" in list(init_dict.keys()):
                wedge_mat = init_dict["wedge_mat"]
            if "is_bore" in list(init_dict.keys()):
                is_bore = init_dict["is_bore"]
        # Set the properties (value check and convertion are done in setter)
        self.W0 = W0
        self.H0 = H0
        self.H2 = H2
        self.W2 = W2
        # Call Slot init
        super(SlotW22, self).__init__(Zs=Zs, wedge_mat=wedge_mat, is_bore=is_bore)
        # The class is frozen (in Slot init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        SlotW22_str = ""
        # Get the properties inherited from Slot
        SlotW22_str += super(SlotW22, self).__str__()
        SlotW22_str += "W0 = " + str(self.W0) + linesep
        SlotW22_str += "H0 = " + str(self.H0) + linesep
        SlotW22_str += "H2 = " + str(self.H2) + linesep
        SlotW22_str += "W2 = " + str(self.W2) + linesep
        return SlotW22_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from Slot
        if not super(SlotW22, self).__eq__(other):
            return False
        if other.W0 != self.W0:
            return False
        if other.H0 != self.H0:
            return False
        if other.H2 != self.H2:
            return False
        if other.W2 != self.W2:
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
            super(SlotW22, self).compare(
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
            other._W2 is not None
            and self._W2 is not None
            and isnan(other._W2)
            and isnan(self._W2)
        ):
            pass
        elif other._W2 != self._W2:
            if is_add_value:
                val_str = " (self=" + str(self._W2) + ", other=" + str(other._W2) + ")"
                diff_list.append(name + ".W2" + val_str)
            else:
                diff_list.append(name + ".W2")
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from Slot
        S += super(SlotW22, self).__sizeof__()
        S += getsizeof(self.W0)
        S += getsizeof(self.H0)
        S += getsizeof(self.H2)
        S += getsizeof(self.W2)
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
        SlotW22_dict = super(SlotW22, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        SlotW22_dict["W0"] = self.W0
        SlotW22_dict["H0"] = self.H0
        SlotW22_dict["H2"] = self.H2
        SlotW22_dict["W2"] = self.W2
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        SlotW22_dict["__class__"] = "SlotW22"
        return SlotW22_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        W0_val = self.W0
        H0_val = self.H0
        H2_val = self.H2
        W2_val = self.W2
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
            H2=H2_val,
            W2=W2_val,
            Zs=Zs_val,
            wedge_mat=wedge_mat_val,
            is_bore=is_bore_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.W0 = None
        self.H0 = None
        self.H2 = None
        self.W2 = None
        # Set to None the properties inherited from Slot
        super(SlotW22, self)._set_None()

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
        doc="""Slot isthmus orthoradial angular width.

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
        doc="""Slot isthmus radial height.

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
        doc="""Slot radial height below wedge 

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
        doc="""Angle between slot edges

        :Type: float
        :min: 0
        """,
    )
