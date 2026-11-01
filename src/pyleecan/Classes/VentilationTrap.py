# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Slot/VentilationTrap.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Slot/VentilationTrap
"""

# Inline fallback report:
# These methods remain imported because their source or imports cannot be safely moved into this class.
# - build_geometry: module uses a wildcard import whose names cannot be resolved safely
# - check: module uses a wildcard import whose names cannot be resolved safely

from os import linesep
from sys import getsizeof
from logging import getLogger
from ._check import check_var, raise_
from ..Functions.get_logger import get_logger
from ..Functions.save import save
from ..Functions.load import load_init_dict
from ..Functions.Load.import_class import import_class
from copy import deepcopy
from .Hole import Hole

# Import all class method
# Try/catch to remove unnecessary dependencies in unused method
from ..Methods.Slot.VentilationTrap.build_geometry import build_geometry
from ..Methods.Slot.VentilationTrap.check import check
from numpy import exp, sqrt, pi
import matplotlib.pyplot as plt
from .Arc1 import Arc1
from .LamHole import LamHole
from .Segment import Segment
from ..Functions.Plot import (
    ARROW_COLOR,
    ARROW_WIDTH,
    MAIN_LINE_COLOR,
    MAIN_LINE_STYLE,
    MAIN_LINE_WIDTH,
    P_FONT_SIZE,
    SC_FONT_SIZE,
    TEXT_BOX,
)
from ..Methods import ParentMissingError

from numpy import isnan
from ._check import InitUnKnowClassError


class VentilationTrap(Hole):
    """Trapezoidal axial ventilation ducts"""

    VERSION = 1

    # cf Methods.Slot.VentilationTrap._comp_point_coordinate
    def _comp_point_coordinate(self):
        """Compute the point coordinates needed to plot the Hole.

        Parameters
        ----------
        self : VentilationPolar
            A VentilationPolar object

        Returns
        -------
        point_dict: dict
            A dict of the slot point coordinates
        """

        Z1 = (self.H0 - 1j * self.W1 / 2) * exp(1j * self.Alpha0)
        Z2 = (self.H0 + self.D0 - 1j * self.W2 / 2) * exp(1j * self.Alpha0)
        Z3 = (self.H0 + self.D0 + 1j * self.W2 / 2) * exp(1j * self.Alpha0)
        Z4 = (self.H0 + 1j * self.W1 / 2) * exp(1j * self.Alpha0)
        ZM1 = (Z1 + Z4) / 2
        ZM2 = (Z2 + Z3) / 2
        Zc = (self.H0 + (self.D0 / 2)) * exp(1j * self.Alpha0)

        point_dict = dict()
        # symetry
        point_dict["Z1"] = Z1
        point_dict["Z2"] = Z2
        point_dict["Z3"] = Z3
        point_dict["Z4"] = Z4
        point_dict["Zc"] = Zc
        point_dict["ZM1"] = ZM1
        point_dict["ZM2"] = ZM2
        return point_dict

    # cf Methods.Slot.VentilationTrap.build_geometry
    build_geometry = build_geometry
    # cf Methods.Slot.VentilationTrap.check
    check = check

    # cf Methods.Slot.VentilationTrap.comp_radius
    def comp_radius(self):
        """Compute the radius of the two circle that contains all the ventilation
        ducts

        Parameters
        ----------
        self : VentilationTrap
            A VentilationTrap object

        Returns
        -------
        (Rmin, Rmax): tuple
            Tuple of circle radius [m]

        """

        self.check()

        Rmin = sqrt(self.W1**2 + self.H0**2)
        Rmax = sqrt(self.W2**2 + (self.H0 + self.D0) ** 2)

        return (Rmin, Rmax)

    # cf Methods.Slot.VentilationTrap.comp_surface
    def comp_surface(self):
        """Compute the surface of all the axial ventilation ducts

        Parameters
        ----------
        self : VentilationTrap
            A VentilationTrap object

        Returns
        -------
        surface: float
            Axial ventilation ducts total surface [m**2]

        """

        self.check()

        return (self.W1 + self.W2) * 0.5 * self.D0

    # cf Methods.Slot.VentilationTrap.get_center
    def get_center(self):
        """Return a list of center of the ventilations
        Parameters
        ----------
        self : VentilationTrap
            A VentilationTrap object

        Returns
        -------
        Zc_list: list
            List of list of center complex coordinates

        """

        Zc_list = list()

        for ii in range(self.Zh):
            Zc = (
                (self.H0 + self.D0 / 2.0)
                * exp(1j * self.Alpha0)
                * exp(ii * 1j * 2 * pi / self.Zh)
            )
            Zc_list.append(Zc)

        return Zc_list

    # cf Methods.Slot.VentilationTrap.plot_schematics
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
        self : VentilationTrap
            A VentilationTrap object
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
            Figure containing the plot
        ax : Matplotlib.axes.Axes object
            Axis containing the plot
        -------
        lam : LamSlot
            Default lamination used for the schematics
        """

        # Use some default parameter
        if is_default:
            hole = type(self)(
                H0=0.125,
                Zh=8,
                Alpha0=0.3,
                D0=0.05,
                W1=0.05,
                W2=0.08,
            )
            lam = LamHole(
                Rint=0.1, Rext=0.2, is_internal=True, is_stator=False, hole=[hole]
            )
            if is_return_default:
                return lam
            else:
                return hole.plot_schematics(
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
                raise ParentMissingError("Error: The hole is not inside a Lamination")
            lam = self.parent
            fig, ax = lam.plot(
                alpha=0,
                is_show_fig=False,
                is_lam_only=True,  # No magnet
                fig=fig,
                ax=ax,
            )  # center hole on Ox axis
            point_dict = self._comp_point_coordinate()

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
                # H0
                line = Segment(0, point_dict["ZM1"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="H0",
                    offset_label=self.D0 / 4 * 1j,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # D0
                line = Segment(
                    point_dict["ZM1"] * exp(1j * 2 * pi / self.Zh),
                    point_dict["ZM2"] * exp(1j * 2 * pi / self.Zh),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="D0",
                    offset_label=self.D0 / 4,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # Alpha0
                line = Arc1(
                    begin=self.H0 + self.D0 / 2,
                    end=point_dict["Zc"],
                    radius=self.H0 + self.D0 / 2,
                    is_trigo_direction=True,
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="Alpha0",
                    offset_label=self.D0 / 4 * (1 - 1.7j),
                    fontsize=SC_FONT_SIZE,
                )
                # W1
                line = Segment(point_dict["Z1"], point_dict["Z4"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="W1",
                    offset_label=self.D0 / 4 * 1.5j,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # W2
                line = Segment(point_dict["Z2"], point_dict["Z3"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="W2",
                    offset_label=self.D0 / 4 * 1.5j,
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
                # Center axis
                line = Segment(0, lam.Rext * 1.5 * exp(1j * self.Alpha0))
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )

            # Zooming and cleaning
            W = abs(point_dict["Z2"].imag) * 1.3
            Rint = self.parent.Rint
            Rext = self.parent.Rext

            ax.axis("equal")
            ax.set_ylim(-Rext / 10, Rext * 0.9)
            ax.set_xlim(Rext / 10, Rext)
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
        D0=1,
        H0=1,
        W1=1,
        W2=1,
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
            if "D0" in list(init_dict.keys()):
                D0 = init_dict["D0"]
            if "H0" in list(init_dict.keys()):
                H0 = init_dict["H0"]
            if "W1" in list(init_dict.keys()):
                W1 = init_dict["W1"]
            if "W2" in list(init_dict.keys()):
                W2 = init_dict["W2"]
            if "Zh" in list(init_dict.keys()):
                Zh = init_dict["Zh"]
            if "mat_void" in list(init_dict.keys()):
                mat_void = init_dict["mat_void"]
            if "magnetization_dict_offset" in list(init_dict.keys()):
                magnetization_dict_offset = init_dict["magnetization_dict_offset"]
            if "Alpha0" in list(init_dict.keys()):
                Alpha0 = init_dict["Alpha0"]
        # Set the properties (value check and convertion are done in setter)
        self.D0 = D0
        self.H0 = H0
        self.W1 = W1
        self.W2 = W2
        # Call Hole init
        super(VentilationTrap, self).__init__(
            Zh=Zh,
            mat_void=mat_void,
            magnetization_dict_offset=magnetization_dict_offset,
            Alpha0=Alpha0,
        )
        # The class is frozen (in Hole init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        VentilationTrap_str = ""
        # Get the properties inherited from Hole
        VentilationTrap_str += super(VentilationTrap, self).__str__()
        VentilationTrap_str += "D0 = " + str(self.D0) + linesep
        VentilationTrap_str += "H0 = " + str(self.H0) + linesep
        VentilationTrap_str += "W1 = " + str(self.W1) + linesep
        VentilationTrap_str += "W2 = " + str(self.W2) + linesep
        return VentilationTrap_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from Hole
        if not super(VentilationTrap, self).__eq__(other):
            return False
        if other.D0 != self.D0:
            return False
        if other.H0 != self.H0:
            return False
        if other.W1 != self.W1:
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

        # Check the properties inherited from Hole
        diff_list.extend(
            super(VentilationTrap, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
        if (
            other._D0 is not None
            and self._D0 is not None
            and isnan(other._D0)
            and isnan(self._D0)
        ):
            pass
        elif other._D0 != self._D0:
            if is_add_value:
                val_str = " (self=" + str(self._D0) + ", other=" + str(other._D0) + ")"
                diff_list.append(name + ".D0" + val_str)
            else:
                diff_list.append(name + ".D0")
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

        # Get size of the properties inherited from Hole
        S += super(VentilationTrap, self).__sizeof__()
        S += getsizeof(self.D0)
        S += getsizeof(self.H0)
        S += getsizeof(self.W1)
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

        # Get the properties inherited from Hole
        VentilationTrap_dict = super(VentilationTrap, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        VentilationTrap_dict["D0"] = self.D0
        VentilationTrap_dict["H0"] = self.H0
        VentilationTrap_dict["W1"] = self.W1
        VentilationTrap_dict["W2"] = self.W2
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        VentilationTrap_dict["__class__"] = "VentilationTrap"
        return VentilationTrap_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        D0_val = self.D0
        H0_val = self.H0
        W1_val = self.W1
        W2_val = self.W2
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
            D0=D0_val,
            H0=H0_val,
            W1=W1_val,
            W2=W2_val,
            Zh=Zh_val,
            mat_void=mat_void_val,
            magnetization_dict_offset=magnetization_dict_offset_val,
            Alpha0=Alpha0_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.D0 = None
        self.H0 = None
        self.W1 = None
        self.W2 = None
        # Set to None the properties inherited from Hole
        super(VentilationTrap, self)._set_None()

    def _get_D0(self):
        """getter of D0"""
        return self._D0

    def _set_D0(self, value):
        """setter of D0"""
        check_var("D0", value, "float", Vmin=0)
        self._D0 = value

    D0 = property(
        fget=_get_D0,
        fset=_set_D0,
        doc="""Hole height

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
        doc="""Radius of the hole bottom

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
        doc="""Hole small basis

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
        doc="""Hole large basis

        :Type: float
        :min: 0
        """,
    )
