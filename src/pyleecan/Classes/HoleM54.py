# File generated according to Generator/ClassesRef/Slot/HoleM54.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Slot/HoleM54"""

from os import linesep
from sys import getsizeof

import matplotlib.pyplot as plt
import numpy as np
from pyleecan.Classes import ParentMissingError
from pyleecan.Classes.Arc1 import Arc1
from pyleecan.Classes.Arc3 import Arc3
from pyleecan.Classes.Hole import Hole
from pyleecan.Classes.LamHole import LamHole
from pyleecan.Classes.Segment import Segment
from pyleecan.Classes.SurfLine import SurfLine
from pyleecan.Classes._check import check_var
from pyleecan.definitions import config_dict
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
from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.load import load_init_dict
from pyleecan.Functions.save import save


class HoleM54(Hole):
    """Arc Hole for SyRM"""

    VERSION = 1
    IS_SYMMETRICAL = 1
    MAGNET_COLOR = config_dict["PLOT"]["COLOR_DICT"]["MAGNET_COLOR"]

    # cf Methods.Slot.HoleM54._comp_point_coordinate
    def _comp_point_coordinate(self):
        """Compute the point coordinates needed to plot the Slot.

        Parameters
        ----------
        self : HoleM54
            A HoleM54 object

        Returns
        -------
        point_dict: dict
            A dict of the slot coordinates
        """

        Rext = self.get_Rext()

        # Compute point coordinates
        Zc0 = Rext - self.H0 + self.R1
        Z0 = Rext - self.H0
        Z1 = (self.R1 * np.exp(1j * (-np.pi + self.W0 / 2))) + Zc0
        Z2 = (self.R1 * np.exp(1j * (np.pi - self.W0 / 2))) + Zc0
        Z4 = ((self.R1 + self.H1) * np.exp(1j * (-np.pi + self.W0 / 2))) + Zc0
        Z3 = ((self.R1 + self.H1) * np.exp(1j * (np.pi - self.W0 / 2))) + Zc0

        point_dict = dict()
        point_dict["Z0"] = Z0
        point_dict["Z1"] = Z1
        point_dict["Z2"] = Z2
        point_dict["Z3"] = Z3
        point_dict["Z4"] = Z4
        point_dict["Zc0"] = Zc0

        return point_dict

    # cf Methods.Slot.HoleM54.build_geometry
    def build_geometry(self, alpha=0, delta=0, is_simplified=False):
        """Compute the curve (Arc) needed to plot the Hole.
        The ending point of a curve is the starting point of the next curve in the
        list

        Parameters
        ----------
        self : HoleM54
            A HoleM54 object
        alpha : float
            Angle to rotate the slot (Default value = 0) [rad]
        delta : complex
            Complex to translate the slot (Default value = 0)
        is_simplified : bool
           True to avoid line superposition

        Returns
        -------
        surf_list : list
            List of Air Surface on the slot

        """

        # Get correct label for surfaces
        lam_label = self.parent.get_label()
        R_id, surf_type = self.get_R_id()
        vent_label = lam_label + "_" + surf_type + "_R" + str(R_id) + "-"

        Rext = self.get_Rext()
        # Get all the points
        point_dict = self._comp_point_coordinate()
        Z1 = point_dict["Z1"]
        Z2 = point_dict["Z2"]
        Z3 = point_dict["Z3"]
        Z4 = point_dict["Z4"]

        surf_list = list()
        curve_list = list()
        curve_list.append(
            Arc1(begin=Z1, end=Z2, radius=-self.R1, is_trigo_direction=False)
        )
        curve_list.append(Arc3(begin=Z2, end=Z3, is_trigo_direction=True))
        curve_list.append(Arc1(begin=Z3, end=Z4, radius=self.R1 + self.H1))
        curve_list.append(Arc3(begin=Z4, end=Z1, is_trigo_direction=True))

        Zref = Rext - self.H0 - self.H1 / 2
        surf_list.append(
            SurfLine(line_list=curve_list, label=vent_label + "T0-S0", point_ref=Zref)
        )

        # Apply the transformations
        for surf in surf_list:
            surf.rotate(alpha)
            surf.translate(delta)

        return surf_list

    # cf Methods.Slot.HoleM54.check
    def check(self):
        """Check that the HoleM54 object is correct

        Parameters
        ----------
        self : HoleM54
            A HoleM54 object

        Returns
        -------
        None

        Raises
        -------
        H54_W0CheckError
            You must have W0 < 2*pi/Zh
        H54_R1CheckError
            You must have H0 < R1
        """

        # Check that everything is set
        if self.W0 is None:
            raise S54_NoneError("You must set W0 !")
        elif self.R1 is None:
            raise S54_NoneError("You must set R1 !")
        elif self.H0 is None:
            raise S54_NoneError("You must set H0 !")
        elif self.H1 is None:
            raise S54_NoneError("You must set H1 !")

        if 2 * np.pi / self.Zh <= self.W0:
            raise H54_W0CheckError("You must have W0 < 2*pi/Zh")

        if self.R1 <= self.H0:
            raise H54_R1CheckError("You must have H0 < R1")

    # cf Methods.Slot.HoleM54.comp_magnetization_dict
    def comp_magnetization_dict(self, is_north=True):
        """Compute the dictionary of the magnetization direction of the magnets (key=magnet_X, value=angle[rad])
        Mangetization angle with Hole centered on Ox axis

        Parameters
        ----------
        self : HoleM54
            a HoleM54 object
        is_north: True
            True: comp north magnetization, else add pi [rad]

        Returns
        -------
        mag_dict: dict
            magnetization dictionary (key=magnet_X, value=angle[rad])
        """

        mag_dict = dict()

        return mag_dict

    # cf Methods.Slot.HoleM54.comp_radius
    def comp_radius(self):
        """Compute the radius of the min and max circle that contains the hole

        Parameters
        ----------
        self : HoleM54
            A HoleM54 object

        Returns
        -------
        (Rmin,Rmax): tuple
            Radius of the circle that contains the hole [m]

        """

        Rext = self.get_Rext()

        surf_list = self.build_geometry()
        point_list = list()
        for curve in surf_list[0].line_list:
            point_list.extend(curve.discretize())

        Rmax = max([np.abs(point) for point in point_list])
        Rmin = Rext - self.H0 - self.H1
        return (Rmin, Rmax)

    # cf Methods.Slot.HoleM54.comp_surface
    def comp_surface(self):
        """Compute the complete surface of the Hole

        Parameters
        ----------
        self : HoleM54
            A HoleM54 object

        Returns
        -------
        S: float
            Surface of the Hole [m**2]

        """

        Sint = np.pi * self.R1**2
        Sext = np.pi * (self.R1 + self.H1) ** 2
        Sarc = (Sext - Sint) * (self.W0 / (2 * np.pi))

        return Sarc + np.pi * (self.H1 / 2) ** 2

    # cf Methods.Slot.HoleM54.plot_schematics
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
        self : HoleM54
            A HoleM54 object
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
        lam : LamHole / LamSlot
            Default lamination used for the schematics
        """

        # Use some default parameter
        if is_default:
            hole = type(self)(Zh=8, W0=np.pi / 3, H0=25e-3, H1=10e-3, R1=75e-3)
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
            alpha = np.pi / 2  # To rotate the schematics
            fig, ax = lam.plot(
                alpha=np.pi / self.Zh + alpha,
                is_show_fig=False,
                is_lam_only=type_add_active == 0,
                fig=fig,
                ax=ax,
            )  # center hole on Ox axis
            sp = 2 * np.pi / self.Zh
            Rbo = self.get_Rbo()
            point_dict = self._comp_point_coordinate()

            # Adding point label
            if is_add_point_label:
                for name, Z in point_dict.items():
                    Z = Z * np.exp(1j * alpha)
                    ax.text(
                        Z.real,
                        Z.imag,
                        name,
                        fontsize=P_FONT_SIZE,
                        bbox=TEXT_BOX,
                    )

            # Adding schematics
            if is_add_schematics:
                # H1
                line = Segment(
                    Rbo * np.exp(1j * alpha),
                    point_dict["Z0"] * np.exp(1j * alpha),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="H0",
                    offset_label=self.H1 * 0.5,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # H1
                line = Segment(
                    point_dict["Z2"] * np.exp(1j * alpha),
                    point_dict["Z3"] * np.exp(1j * alpha),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="H1",
                    offset_label=self.H1 * 0.5,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # R1
                line = Segment(
                    point_dict["Z1"] * np.exp(1j * alpha),
                    point_dict["Zc0"] * np.exp(1j * alpha),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="R1",
                    offset_label=self.H1 * 0.5,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # W0
                line = Arc1(
                    begin=(point_dict["Z2"] + point_dict["Zc0"])
                    / 2
                    * np.exp(1j * alpha),
                    end=(point_dict["Z1"] + point_dict["Zc0"]) / 2 * np.exp(1j * alpha),
                    radius=self.R1,
                    is_trigo_direction=True,
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="W0",
                    offset_label=1j * self.H1 * 0.5,
                    fontsize=SC_FONT_SIZE,
                )

            if is_add_main_line:
                # Ox axis
                line = Segment(0, lam.Rext * 1.5 * np.exp(1j * alpha))
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # H1 line
                line = Arc3(
                    begin=(point_dict["Zc0"] + 1j * self.R1) * np.exp(1j * alpha),
                    end=(point_dict["Zc0"] - 1j * self.R1) * np.exp(1j * alpha),
                    is_trigo_direction=True,
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                line = Arc3(
                    begin=(point_dict["Zc0"] + 1j * (self.R1 + self.H1))
                    * np.exp(1j * alpha),
                    end=(point_dict["Zc0"] - 1j * (self.R1 + self.H1))
                    * np.exp(1j * alpha),
                    is_trigo_direction=True,
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # R1 lines
                line = Segment(
                    point_dict["Zc0"] * np.exp(1j * alpha),
                    point_dict["Z4"] * np.exp(1j * alpha),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                line = Segment(
                    point_dict["Zc0"] * np.exp(1j * alpha),
                    point_dict["Z3"] * np.exp(1j * alpha),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )

            # Zooming and cleaning
            W = point_dict["Z2"].imag * 1.2
            Rint = point_dict["Z3"].real * 0.9
            Rext = point_dict["Zc0"].real

            ax.axis("equal")
            ax.set_ylim(Rint, Rext)
            ax.set_xlim(-W, W)
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
        H0=0.003,
        H1=0,
        W0=0.013,
        R1=0.02,
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
            if "H1" in list(init_dict.keys()):
                H1 = init_dict["H1"]
            if "W0" in list(init_dict.keys()):
                W0 = init_dict["W0"]
            if "R1" in list(init_dict.keys()):
                R1 = init_dict["R1"]
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
        self.H1 = H1
        self.W0 = W0
        self.R1 = R1
        # Call Hole init
        super(HoleM54, self).__init__(
            Zh=Zh,
            mat_void=mat_void,
            magnetization_dict_offset=magnetization_dict_offset,
            Alpha0=Alpha0,
        )
        # The class is frozen (in Hole init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        HoleM54_str = ""
        # Get the properties inherited from Hole
        HoleM54_str += super(HoleM54, self).__str__()
        HoleM54_str += "H0 = " + str(self.H0) + linesep
        HoleM54_str += "H1 = " + str(self.H1) + linesep
        HoleM54_str += "W0 = " + str(self.W0) + linesep
        HoleM54_str += "R1 = " + str(self.R1) + linesep
        return HoleM54_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from Hole
        if not super(HoleM54, self).__eq__(other):
            return False
        if other.H0 != self.H0:
            return False
        if other.H1 != self.H1:
            return False
        if other.W0 != self.W0:
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

        # Check the properties inherited from Hole
        diff_list.extend(
            super(HoleM54, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
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
            other._H1 is not None
            and self._H1 is not None
            and np.isnan(other._H1)
            and np.isnan(self._H1)
        ):
            pass
        elif other._H1 != self._H1:
            if is_add_value:
                val_str = " (self=" + str(self._H1) + ", other=" + str(other._H1) + ")"
                diff_list.append(name + ".H1" + val_str)
            else:
                diff_list.append(name + ".H1")
        if (
            other._W0 is not None
            and self._W0 is not None
            and np.isnan(other._W0)
            and np.isnan(self._W0)
        ):
            pass
        elif other._W0 != self._W0:
            if is_add_value:
                val_str = " (self=" + str(self._W0) + ", other=" + str(other._W0) + ")"
                diff_list.append(name + ".W0" + val_str)
            else:
                diff_list.append(name + ".W0")
        if (
            other._R1 is not None
            and self._R1 is not None
            and np.isnan(other._R1)
            and np.isnan(self._R1)
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

        # Get size of the properties inherited from Hole
        S += super(HoleM54, self).__sizeof__()
        S += getsizeof(self.H0)
        S += getsizeof(self.H1)
        S += getsizeof(self.W0)
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

        # Get the properties inherited from Hole
        HoleM54_dict = super(HoleM54, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        HoleM54_dict["H0"] = self.H0
        HoleM54_dict["H1"] = self.H1
        HoleM54_dict["W0"] = self.W0
        HoleM54_dict["R1"] = self.R1
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        HoleM54_dict["__class__"] = "HoleM54"
        return HoleM54_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        H0_val = self.H0
        H1_val = self.H1
        W0_val = self.W0
        R1_val = self.R1
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
            H1=H1_val,
            W0=W0_val,
            R1=R1_val,
            Zh=Zh_val,
            mat_void=mat_void_val,
            magnetization_dict_offset=magnetization_dict_offset_val,
            Alpha0=Alpha0_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.H0 = None
        self.H1 = None
        self.W0 = None
        self.R1 = None
        # Set to None the properties inherited from Hole
        super(HoleM54, self)._set_None()

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
        doc="""Hole depth

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
        doc="""Hole width

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
        doc="""Hole angular width

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
        doc="""Hole radius

        :Type: float
        :min: 0
        """,
    )

    class MachineCheckError(Exception):
        """ """

        pass

    class LaminationCheckError(MachineCheckError):
        """ """

        pass

    class SlotCheckError(LaminationCheckError):
        """ """

        pass

    class S54_NoneError(SlotCheckError):
        """Raised when a propery of HoleM54 is None"""

        pass

    class H54_W0CheckError(SlotCheckError):
        """ """

        pass

    class H54_R1CheckError(SlotCheckError):
        """ """

        pass


MachineCheckError = HoleM54.MachineCheckError

LaminationCheckError = HoleM54.LaminationCheckError

SlotCheckError = HoleM54.SlotCheckError

S54_NoneError = HoleM54.S54_NoneError

H54_W0CheckError = HoleM54.H54_W0CheckError

H54_R1CheckError = HoleM54.H54_R1CheckError
