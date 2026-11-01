# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Slot/VentilationPolar.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Slot/VentilationPolar
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
from pyleecan.Classes.Hole import Hole

# Import all class method
# Try/catch to remove unnecessary dependencies in unused method
import numpy as np, matplotlib.pyplot as plt
from pyleecan.Classes.PolarArc import PolarArc
from pyleecan.Methods.Slot.VentilationPolar import (
    PolarArcBuildGeometryError,
    VentilationPolarInstanceError,
)
from pyleecan.Classes.Arc1 import Arc1
from pyleecan.Classes.LamHole import LamHole
from pyleecan.Classes.Segment import Segment
from pyleecan.Functions.Plot import (
    ARROW_COLOR,
    ARROW_WIDTH,
    MAIN_LINE_COLOR,
    MAIN_LINE_STYLE,
    MAIN_LINE_WIDTH,
    P_FONT_SIZE,
    SC_FONT_SIZE,
    TEXT_BOX,
)
from pyleecan.Methods import ParentMissingError


from pyleecan.Classes._check import InitUnKnowClassError


class VentilationPolar(Hole):
    """Polar axial ventilation duct"""

    VERSION = 1

    # cf Methods.Slot.VentilationPolar._comp_point_coordinate
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

        Z1 = (self.H0) * np.exp(1j * (self.Alpha0 - self.W1 / 2))
        Z2 = (self.H0 + self.D0) * np.exp(1j * (self.Alpha0 - self.W1 / 2))
        Z3 = (self.H0 + self.D0) * np.exp(1j * (self.Alpha0 + self.W1 / 2))
        Z4 = (self.H0) * np.exp(1j * (self.Alpha0 + self.W1 / 2))
        Zc = (self.H0 + (self.D0 / 2)) * np.exp(1j * self.Alpha0)

        point_dict = dict()
        # symetry
        point_dict["Z1"] = Z1
        point_dict["Z2"] = Z2
        point_dict["Z3"] = Z3
        point_dict["Z4"] = Z4
        point_dict["Zc"] = Zc
        return point_dict

    # cf Methods.Slot.VentilationPolar.build_geometry
    def build_geometry(self, alpha=0, delta=0):
        """Compute the curve needed to plot the ventilations

        Parameters
        ----------
        self : VentilationPolar
            A VentilationPolar object
        alpha : float
            Angle for rotation (Default value = 0) [rad]
        delta : complex
            Complex for translation (Default value = 0)

        Returns
        -------
        surf_list: list
            A list of PolarArc

        Raises
        _______
        PolarArcBuildGeometryError
            The parameter 'sym' must be an integer > 0
            The parameter 'alpha' must be an int or float
            The parameter 'delta' must be a complex or float or int number
        """

        lam_label = self.parent.get_label()
        R_id, surf_type = self.get_R_id()
        RTS_id = "R" + str(R_id) + "-T0-S0"
        vent_label = lam_label + "_" + surf_type + "_" + RTS_id

        # checking if the param have good type
        if type(alpha) not in [int, float]:
            raise PolarArcBuildGeometryError(
                "The parameter 'alpha' must be an int or float"
            )
        if type(delta) not in [complex, int, float]:
            raise PolarArcBuildGeometryError(
                "The parameter 'delta' must be a complex or float or int number"
            )

        surf_list = list()
        # Modulo on Alpha for sym
        Alpha0 = self.Alpha0 % (2 * np.pi / self.Zh)
        Zc = (self.H0 + (self.D0 / 2)) * np.exp(1j * Alpha0)
        surf_list.append(
            PolarArc(
                point_ref=Zc,
                label=vent_label,
                angle=self.W1,
                height=self.D0,
            )
        )

        return surf_list

    # cf Methods.Slot.VentilationPolar.check
    def check(self):
        """Make sure that the ventilation parameters are correctly set

        Parameters
        ----------
        self : VentilationPolar
            A VentilationPolar object

        Returns
        -------
        None

        Raises
        _______
        VentilationPolarInstanceError
            Zh must be a integer
            H0 must be a float or int
            D0 must be a float or int
            Alpha0 must be a float or int
        """

        if not isinstance(self.Zh, int):
            raise VentilationPolarInstanceError("Zh must be a integer")
        if not isinstance(self.H0, float) and not isinstance(self.H0, int):
            raise VentilationPolarInstanceError("H0 must be a float or int")
        if not isinstance(self.D0, float) and not isinstance(self.D0, int):
            raise VentilationPolarInstanceError("D0 must be a float or int")
        if not isinstance(self.Alpha0, float) and not isinstance(self.Alpha0, int):
            raise VentilationPolarInstanceError("Alpha0 must be a float or int")

    # cf Methods.Slot.VentilationPolar.comp_radius
    def comp_radius(self):
        """Compute the radius of the two circle that contains all the ventilation
        ducts

        Parameters
        ----------
        self : VentilationPolar
            A VentilationPolar object

        Returns
        -------
        (Rmin, Rmax): tuple
            Tuple of circle radius [m]

        """

        self.check()

        Rmin = self.H0
        Rmax = self.D0 + self.H0

        return (Rmin, Rmax)

    # cf Methods.Slot.VentilationPolar.comp_surface
    def comp_surface(self):
        """Compute the surface of all the axial ventilation ducts

        Parameters
        ----------
        self : VentilationPolar
            A VentilationPolar object

        Returns
        -------
        surface: float
            Axial ventilation ducts total surface [m**2]

        """

        self.check()

        return np.pi * ((self.H0 + self.D0) ** 2 - self.H0**2) / (2 * np.pi / self.W1)

    # cf Methods.Slot.VentilationPolar.get_center
    def get_center(self):
        """Return a list of the center of the ventilations

        Parameters
        ----------
        self : VentilationPolar
            A VentilationPolar object

        Returns
        -------
        Zc_list: list
            List of list of center complex coordinates

        """

        Zc_list = list()

        for ii in range(self.Zh):
            Zc = self.H0 + (self.D0 / 2.0) * np.exp(1j * self.Alpha0) * np.exp(
                1j * 2 * np.pi / self.Zh
            )
            Zc_list.append(Zc)

        return Zc_list

    # cf Methods.Slot.VentilationPolar.plot_schematics
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
        self : VentilationPolar
            A VentilationPolar object
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
                W1=2 * np.pi / 16,
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
                line = Segment(0, point_dict["Z1"])
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
                    point_dict["Z1"] * np.exp(1j * 2 * np.pi / self.Zh),
                    point_dict["Z2"] * np.exp(1j * 2 * np.pi / self.Zh),
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
                    offset_label=self.D0 / 4 * (1 - 1.5j),
                    fontsize=SC_FONT_SIZE,
                )
                # W1
                Rtop = self.H0 + self.D0
                Rarc = (Rtop + lam.Rext) / 2
                line = Arc1(
                    begin=Rarc * np.exp(1j * (self.Alpha0 - self.W1 / 2)),
                    end=Rarc * np.exp(1j * (self.Alpha0 + self.W1 / 2)),
                    radius=Rarc,
                    is_trigo_direction=True,
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="W1",
                    offset_label=self.D0 / 4,
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
                line = Segment(0, lam.Rext * 1.5 * np.exp(1j * self.Alpha0))
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # H0 radius
                line = Arc1(
                    begin=self.H0 * np.exp(-1j * np.pi / 2 * 0.9),
                    end=self.H0 * np.exp(1j * np.pi / 2 * 0.9),
                    radius=self.H0,
                    is_trigo_direction=True,
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # H0+D0 radius
                line = Arc1(
                    begin=(self.H0 + self.D0) * np.exp(-1j * np.pi / 2 * 0.9),
                    end=(self.H0 + self.D0) * np.exp(1j * np.pi / 2 * 0.9),
                    radius=(self.H0 + self.D0),
                    is_trigo_direction=True,
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # Vent side 1 axis
                line = Segment(
                    0, lam.Rext * 1.5 * np.exp(1j * np.angle(point_dict["Z1"]))
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # Vent side 2 axis
                line = Segment(
                    0, lam.Rext * 1.5 * np.exp(1j * np.angle(point_dict["Z3"]))
                )
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
        # Call Hole init
        super(VentilationPolar, self).__init__(
            Zh=Zh,
            mat_void=mat_void,
            magnetization_dict_offset=magnetization_dict_offset,
            Alpha0=Alpha0,
        )
        # The class is frozen (in Hole init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        VentilationPolar_str = ""
        # Get the properties inherited from Hole
        VentilationPolar_str += super(VentilationPolar, self).__str__()
        VentilationPolar_str += "D0 = " + str(self.D0) + linesep
        VentilationPolar_str += "H0 = " + str(self.H0) + linesep
        VentilationPolar_str += "W1 = " + str(self.W1) + linesep
        return VentilationPolar_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from Hole
        if not super(VentilationPolar, self).__eq__(other):
            return False
        if other.D0 != self.D0:
            return False
        if other.H0 != self.H0:
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

        # Check the properties inherited from Hole
        diff_list.extend(
            super(VentilationPolar, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
        if (
            other._D0 is not None
            and self._D0 is not None
            and np.isnan(other._D0)
            and np.isnan(self._D0)
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
            and np.isnan(other._H0)
            and np.isnan(self._H0)
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

        # Get size of the properties inherited from Hole
        S += super(VentilationPolar, self).__sizeof__()
        S += getsizeof(self.D0)
        S += getsizeof(self.H0)
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

        # Get the properties inherited from Hole
        VentilationPolar_dict = super(VentilationPolar, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        VentilationPolar_dict["D0"] = self.D0
        VentilationPolar_dict["H0"] = self.H0
        VentilationPolar_dict["W1"] = self.W1
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        VentilationPolar_dict["__class__"] = "VentilationPolar"
        return VentilationPolar_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        D0_val = self.D0
        H0_val = self.H0
        W1_val = self.W1
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
        # Set to None the properties inherited from Hole
        super(VentilationPolar, self)._set_None()

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
        doc="""Height of the hole

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
        doc="""Radius of the bottom of Hole

        :Type: float
        :min: 0
        """,
    )

    def _get_W1(self):
        """getter of W1"""
        return self._W1

    def _set_W1(self, value):
        """setter of W1"""
        check_var("W1", value, "float", Vmin=0, Vmax=6.29)
        self._W1 = value

    W1 = property(
        fget=_get_W1,
        fset=_set_W1,
        doc="""Hole angular width

        :Type: float
        :min: 0
        :max: 6.29
        """,
    )
