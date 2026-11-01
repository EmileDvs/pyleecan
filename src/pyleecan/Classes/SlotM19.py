# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Slot/SlotM19.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Slot/SlotM19
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
from pyleecan.Classes.Slot import Slot

# Import all class method
# Try/catch to remove unnecessary dependencies in unused method
from numpy import arcsin, exp, abs as np_abs, sqrt, sin, pi
from pyleecan.Classes.Segment import Segment
from pyleecan.Classes.Arc1 import Arc1
from pyleecan.Classes.SurfLine import SurfLine
from pyleecan.Methods.Slot.SlotM19.plot_schematics import MAGNET_COLOR
import matplotlib.pyplot as plt
from pyleecan.Classes.LamSlot import LamSlot
from pyleecan.Functions.Plot import (
    ARROW_COLOR,
    ARROW_WIDTH,
    MAIN_LINE_COLOR,
    MAIN_LINE_STYLE,
    MAIN_LINE_WIDTH,
    P_FONT_SIZE,
    SC_FONT_SIZE,
    TEXT_BOX,
    plot_quote,
)
from pyleecan.Methods import ParentMissingError

from numpy import isnan
from pyleecan.Classes._check import InitUnKnowClassError


class SlotM19(Slot):
    """trapezoidal  Slot with trapezoidal magnet with polar top"""

    VERSION = 1
    IS_SYMMETRICAL = 1

    # cf Methods.Slot.SlotM19._comp_point_coordinate
    def _comp_point_coordinate(self):
        """Compute the point coordinates needed to plot the Slot.

        Parameters
        ----------
        self : SlotM19
            A SlotM19 object

        Returns
        -------
        point_dict: dict
            A dict of the slot coordinates
        """

        Rbo = self.get_Rbo()

        # alpha is the angle to rotate Z0 so ||Z1,Z4|| = W1
        alpha = float(arcsin(self.W1 / (2 * Rbo)))

        Z1 = Rbo * exp(-1j * alpha)

        if self.is_outwards():
            Zmid = Rbo + self.H0

        else:  # inward slot
            Zmid = Rbo - self.H0

        Z2 = Zmid - 1j * (self.W0 / 2)

        point_dict = dict()
        point_dict["Z1"] = Z1
        point_dict["Z2"] = Z2
        point_dict["Zmid"] = Zmid
        # symetry
        point_dict["Z3"] = Z2.conjugate()
        point_dict["Z4"] = Z1.conjugate()

        return point_dict

    # cf Methods.Slot.SlotM19.build_geometry
    def build_geometry(self):
        """Compute the curve (Line) needed to plot the Slot.
        The ending point of a curve is the starting point of the next curve in
        the list

        Parameters
        ----------
        self : SlotM19
            A SlotM19 object

        Returns
        -------
        curve_list: list
            A list of 3 Segments

        """
        point_dict = self._comp_point_coordinate()
        Z1 = point_dict["Z1"]
        Z2 = point_dict["Z2"]
        Z3 = point_dict["Z3"]
        Z4 = point_dict["Z4"]

        # Creation of curve
        curve_list = list()
        if self.H0 > 0:
            curve_list.append(Segment(Z1, Z2))
        curve_list.append(Segment(Z2, Z3))
        if self.H0 > 0:
            curve_list.append(Segment(Z3, Z4))

        return curve_list

    # cf Methods.Slot.SlotM19.check
    def check(self):
        """
        Check that the SlotM19 object is correct

        Parameters
        ----------
        self : SlotM19
            A SlotM19 object

        Returns
        -------

        """
        pass

    # cf Methods.Slot.SlotM19.comp_angle_opening
    def comp_angle_opening(self):
        """Compute the average opening angle of the Slot

        Parameters
        ----------
        self : SlotM19
            A SlotM19 object

        Returns
        -------
        alpha: float
            Average opening angle of the slot [rad]

        """

        Rbo = self.get_Rbo()

        return float(2 * arcsin(self.W1 / (2 * Rbo)))

    # cf Methods.Slot.SlotM19.comp_height
    def comp_height(self):
        """Compute the height of the Slot.
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotM19
            A SlotM19 object

        Returns
        -------
        Htot: float
            Height of the slot [m]

        """

        point_dict = self._comp_point_coordinate()
        Zmid = point_dict["Zmid"]
        Z1 = point_dict["Z1"]
        Z2 = point_dict["Z2"]
        Z3 = point_dict["Z3"]
        Z4 = point_dict["Z4"]

        Rbo = self.get_Rbo()

        if self.is_outwards():
            return np_abs(sqrt(Z2.real**2 + Z2.imag**2)) - np_abs(Rbo)

        else:
            return self.H0

    # cf Methods.Slot.SlotM19.comp_height_active
    def comp_height_active(self):
        """Compute the height of the active area

        Parameters
        ----------
        self : SlotM19
            A SlotM19 object

        Returns
        -------
        Hwind: float
            Height of the active area [m]

        """
        return self.comp_height()

    # cf Methods.Slot.SlotM19.comp_surface
    def comp_surface(self):
        """Compute the Slot total surface (by analytical computation).
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotM19
            A SlotM19 object

        Returns
        -------
        S: float
            Slot total surface [m**2]

        """

        Rbo = self.get_Rbo()
        point_dict = self._comp_point_coordinate()
        Z1 = point_dict["Z1"]
        Z2 = point_dict["Z2"]

        # The bottom is an arc
        alpha = self.comp_angle_opening()
        Sarc = (Rbo**2.0) / 2.0 * (alpha - sin(alpha))

        S1 = abs(Z1.real - Z2.real) * (self.W1 + self.W0) / 2

        if self.is_outwards():
            return S1 - Sarc
        else:
            return S1 + Sarc

    # cf Methods.Slot.SlotM19.comp_surface_active
    def comp_surface_active(self):
        """Compute the Slot active inner surface (by analytical computation)

        Parameters
        ----------
        self : SlotM19
            A SlotM19 object

        Returns
        -------
        Swind: float
            Slot active inner surface [m**2]

        """
        return self.comp_surface()  # Magnet perfectly match the slot

    # cf Methods.Slot.SlotM19.get_surface_active
    def get_surface_active(self, alpha=0, delta=0):
        """Return the full active surface

        Parameters
        ----------
        self : SlotM19
            A SlotM19 object
        alpha : float
            float number for rotation (Default value = 0) [rad]
        delta : complex
            complex number for translation (Default value = 0)

        Returns
        -------
        surf_act: Surface
            Surface corresponding to the Active Area
        """
        Rbo = self.get_Rbo()
        # get the name of the lamination
        st = self.get_name_lam()

        point_dict = self._comp_point_coordinate()
        Zmid = point_dict["Zmid"]
        Z1 = point_dict["Z1"]
        Z2 = point_dict["Z2"]
        Z3 = point_dict["Z3"]
        Z4 = point_dict["Z4"]

        curve_list = list()
        curve_list.append(Segment(Z1, Z2))
        curve_list.append(Segment(Z2, Z3))
        curve_list.append(Segment(Z3, Z4))

        if self.is_outwards():
            curve_list.append(Arc1(Z4, Z1, -Rbo, is_trigo_direction=False))
        else:
            curve_list.append(Arc1(Z4, Z1, -Rbo, is_trigo_direction=False))

        surface = SurfLine(
            line_list=curve_list,
            label="Wind_" + st + "_R0_T0_S0",
            point_ref=(Z1 + Z3) / 2,
        )

        # Apply transformation
        if alpha != 0:
            surface.rotate(alpha)
        if delta != 0:
            surface.translate(delta)

        return surface

    # cf Methods.Slot.SlotM19.plot_schematics
    def plot_schematics(
        self,
        is_default=False,
        is_return_default=False,
        is_add_point_label=False,
        is_add_schematics=True,
        is_add_main_line=True,
        type_add_active=True,
        save_path=None,
        is_show_fig=True,
        fig=None,
        ax=None,
    ):
        """Plot the schematics of the slot

        Parameters
        ----------
        self : SlotM19
            A SlotM19 object
        is_default : bool
            True: plot default schematics, else use current slot values
        is_return_default : bool
            True: return the default lamination used for the schematics (skip plot)
        is_add_point_label : bool
            True to display the name of the points (Z1, Z2....)
        is_add_schematics : bool
            True to display the schematics information (W0, H0...)
        is_add_main_line : bool
            True to display "main lines" (slot opening and 0x axis)
        type_add_active : int
            0: No active surface, 1: active surface as winding, 2: active surface as magnet
        save_path : str
            full path including folder, name and extension of the file to save if save_path is not None
        is_show_fig : bool
            To call show at the end of the method
        fig : Matplotlib.figure.Figure
            existing figure to use if None create a new one
        ax : Matplotlib.axes.Axes object
            Axis on which to plot the data

        Returns
        -------
        fig : Matplotlib.figure.Figure
            Figure containing the schematics
        ax : Matplotlib.axes.Axes object
            Axis containing the schematics
        -------
        lam : LamSlot
            Default lamination used for the schematics
        """

        # Use some default parameter
        if is_default:
            # definir paramètre par défault
            slot = type(self)(Zs=4, W0=30e-3, H0=17.5e-3, W1=20e-3)
            if is_default == 1:  # Internal Rotor schematics
                lam = LamSlot(
                    Rint=0.1, Rext=0.135, is_internal=True, is_stator=False, slot=slot
                )
                if is_return_default:
                    return lam

            else:  # External Stator schematics
                lam = LamSlot(
                    Rint=0.1, Rext=0.135, is_internal=False, is_stator=True, slot=slot
                )
                if is_return_default:
                    return lam

            return slot.plot_schematics(
                is_default=False,
                is_return_default=False,
                is_add_point_label=is_add_point_label,
                is_add_schematics=is_add_schematics,
                is_add_main_line=is_add_main_line,
                type_add_active=type_add_active,
                save_path=save_path,
                is_show_fig=is_show_fig,
                fig=fig,
                ax=ax,
            )
        else:
            # Getting the main plot
            if self.parent is None:
                raise ParentMissingError("Error: The slot is not inside a Lamination")
            lam = self.parent
            fig, ax = lam.plot(
                alpha=pi / self.Zs, is_show_fig=False, fig=fig, ax=ax
            )  # center slot on Ox axis
            point_dict = self._comp_point_coordinate()
            if self.is_outwards():
                sign = +1
            else:
                sign = -1

            # Adding point label
            if is_add_point_label:
                for name, Z in point_dict.items():
                    ax.text(
                        Z.real,
                        Z.imag,
                        name,
                        fontsize=P_FONT_SIZE,
                        bbox=TEXT_BOX,
                    )

            # Adding schematics
            if is_add_schematics:
                # W0
                line = Segment(point_dict["Z3"], point_dict["Z2"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="W0",
                    offset_label=sign * self.H0 * 0.4,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # W1
                plot_quote(
                    Z1=point_dict["Z1"],
                    Zlim1=point_dict["Z1"] - sign * 0.5 * self.H0,
                    Zlim2=point_dict["Z4"] - sign * 0.5 * self.H0,
                    Z2=point_dict["Z4"],
                    offset_label=0.25 * self.H0,
                    fig=fig,
                    ax=ax,
                    label="W1",
                )
                if lam.is_internal == False and lam.is_stator == True:
                    # Hkey
                    mid = point_dict["Zmid"]
                    line = Segment(mid, mid - sign * self.H0)
                    line.plot(
                        fig=fig,
                        ax=ax,
                        color=ARROW_COLOR,
                        linewidth=ARROW_WIDTH,
                        label="H0",
                        offset_label=1j * 0.1 * self.H0 - 0.0025,
                        is_arrow=True,
                        fontsize=SC_FONT_SIZE,
                    )

                # H0
                mid = point_dict["Zmid"]
                line = Segment(mid, mid - sign * self.H0)
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="H0",
                    offset_label=1j * 0.1 * self.H0 - 0.0025,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )

            if is_add_main_line:
                # Ox axis
                line = Segment(0, lam.Rext * 1.5)
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # Magnet Arc
                line = Arc1(
                    begin=point_dict["Z1"],
                    end=point_dict["Z4"],
                    radius=abs(point_dict["Z1"]),
                    is_trigo_direction=True,
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )

            if type_add_active == 1:
                self.plot_active(fig=fig, ax=ax, is_show_fig=False)
            elif type_add_active == 2:
                self.plot_active(
                    fig=fig,
                    ax=ax,
                    is_show_fig=False,
                    enforced_default_color=MAGNET_COLOR,
                )

            # Zooming and cleaning
            W = self.W0 / 2 * 1.4
            Rint, Rext = self.comp_radius()

            ax.axis("equal")
            ax.set_xlim(Rint, Rext)
            ax.set_ylim(-W, W)
            manager = plt.get_current_fig_manager()
            if manager is not None:
                manager.set_window_title(type(self).__name__ + " Schematics")
            ax.set_title("")
            ax.get_legend().remove()
            ax.set_axis_off()
            fig.tight_layout()

            # Save / Show
            if save_path is not None:
                fig.savefig(save_path)
                plt.close(fig=fig)

            if is_show_fig:
                fig.show()
            return fig, ax

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        W0=0,
        W1=0,
        H0=0,
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
            if "W1" in list(init_dict.keys()):
                W1 = init_dict["W1"]
            if "H0" in list(init_dict.keys()):
                H0 = init_dict["H0"]
            if "Zs" in list(init_dict.keys()):
                Zs = init_dict["Zs"]
            if "wedge_mat" in list(init_dict.keys()):
                wedge_mat = init_dict["wedge_mat"]
            if "is_bore" in list(init_dict.keys()):
                is_bore = init_dict["is_bore"]
        # Set the properties (value check and convertion are done in setter)
        self.W0 = W0
        self.W1 = W1
        self.H0 = H0
        # Call Slot init
        super(SlotM19, self).__init__(Zs=Zs, wedge_mat=wedge_mat, is_bore=is_bore)
        # The class is frozen (in Slot init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        SlotM19_str = ""
        # Get the properties inherited from Slot
        SlotM19_str += super(SlotM19, self).__str__()
        SlotM19_str += "W0 = " + str(self.W0) + linesep
        SlotM19_str += "W1 = " + str(self.W1) + linesep
        SlotM19_str += "H0 = " + str(self.H0) + linesep
        return SlotM19_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from Slot
        if not super(SlotM19, self).__eq__(other):
            return False
        if other.W0 != self.W0:
            return False
        if other.W1 != self.W1:
            return False
        if other.H0 != self.H0:
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
            super(SlotM19, self).compare(
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
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from Slot
        S += super(SlotM19, self).__sizeof__()
        S += getsizeof(self.W0)
        S += getsizeof(self.W1)
        S += getsizeof(self.H0)
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
        SlotM19_dict = super(SlotM19, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        SlotM19_dict["W0"] = self.W0
        SlotM19_dict["W1"] = self.W1
        SlotM19_dict["H0"] = self.H0
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        SlotM19_dict["__class__"] = "SlotM19"
        return SlotM19_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        W0_val = self.W0
        W1_val = self.W1
        H0_val = self.H0
        Zs_val = self.Zs
        if self.wedge_mat is None:
            wedge_mat_val = None
        else:
            wedge_mat_val = self.wedge_mat.copy()
        is_bore_val = self.is_bore
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(
            W0=W0_val,
            W1=W1_val,
            H0=H0_val,
            Zs=Zs_val,
            wedge_mat=wedge_mat_val,
            is_bore=is_bore_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.W0 = None
        self.W1 = None
        self.H0 = None
        # Set to None the properties inherited from Slot
        super(SlotM19, self)._set_None()

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
        doc="""Slot/magnet width. (top)

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
        doc="""Slot/magnet width. (bottom)

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
        doc="""Magnet Height

        :Type: float
        :min: 0
        """,
    )
