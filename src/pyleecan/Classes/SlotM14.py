# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Slot/SlotM14.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Slot/SlotM14
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
import numpy as np, matplotlib.pyplot as plt
from pyleecan.Functions.Geometry.comp_flower_arc import comp_flower_arc
from pyleecan.Classes.Segment import Segment
from pyleecan.Classes.Arc1 import Arc1
from pyleecan.Methods.Slot.Slot import SlotCheckError
from pyleecan.Classes.SurfLine import SurfLine
from pyleecan.Methods.Slot.SlotM14.plot_schematics import MAGNET_COLOR
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
)
from pyleecan.Methods import ParentMissingError


from pyleecan.Classes._check import InitUnKnowClassError


class SlotM14(Slot):
    """Polar Slot with Polar magnet with circular top"""

    VERSION = 1
    IS_SYMMETRICAL = 1

    # cf Methods.Slot.SlotM14._comp_point_coordinate
    def _comp_point_coordinate(self):
        """Compute the point coordinates needed to plot the Slot.

        Parameters
        ----------
        self : SlotM14
            A SlotM14 object

        Returns
        -------
        point_dict: dict
            A dict of the slot coordinates
        """

        Rbo = self.get_Rbo()

        Z1 = Rbo * np.exp(-1j * self.W0 / 2)
        Z4 = Rbo * np.exp(+1j * self.W0 / 2)

        if self.is_outwards():
            Z2 = (Rbo + self.H0) * np.exp(-1j * self.W0 / 2)
            Z3 = (Rbo + self.H0) * np.exp(+1j * self.W0 / 2)
            ZM1 = (Rbo + self.H0) * np.exp(-1j * self.W1 / 2)
            ZM4 = (Rbo + self.H0) * np.exp(+1j * self.W1 / 2)
            (alpha_lim, ZM3, ZM2) = comp_flower_arc(
                abs(np.angle(ZM1) - np.angle(ZM4)), self.Rtopm, abs(ZM1) - self.H1
            )
            ZM0 = Rbo + self.H0 - self.H1
            Zc = ZM0 + self.Rtopm
        else:
            Z2 = (Rbo - self.H0) * np.exp(-1j * self.W0 / 2)
            Z3 = (Rbo - self.H0) * np.exp(+1j * self.W0 / 2)
            ZM1 = (Rbo - self.H0) * np.exp(-1j * self.W1 / 2)
            ZM4 = (Rbo - self.H0) * np.exp(+1j * self.W1 / 2)
            (alpha_lim, ZM3, ZM2) = comp_flower_arc(
                abs(np.angle(ZM1) - np.angle(ZM4)), self.Rtopm, abs(ZM1) + self.H1
            )
            ZM0 = Rbo - self.H0 + self.H1
            Zc = ZM0 - self.Rtopm

        point_dict = dict()
        point_dict["Z1"] = Z1
        point_dict["Z2"] = Z2
        point_dict["ZM1"] = ZM1
        point_dict["ZM2"] = ZM2
        point_dict["ZM0"] = ZM0
        point_dict["Zc"] = Zc
        # symetry
        point_dict["Z3"] = Z3
        point_dict["Z4"] = Z4
        point_dict["ZM3"] = ZM3
        point_dict["ZM4"] = ZM4

        return point_dict

    # cf Methods.Slot.SlotM14.build_geometry
    def build_geometry(self):
        """Compute the curve (Line) needed to plot the Slot.
        The ending point of a curve is the starting point of the next curve in
        the list

        Parameters
        ----------
        self : SlotM14
            A SlotM14 object

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

    # cf Methods.Slot.SlotM14.check
    def check(self):
        """Check that the SlotM11 object is correct

        Parameters
        ----------
        self : SlotM14
            A SlotM14 object

        Returns
        -------
        None
        """
        if self.W0 < self.W1:
            raise SlotCheckError("You must have W1 <= W0")

    # cf Methods.Slot.SlotM14.comp_angle_opening
    def comp_angle_opening(self):
        """Compute the average opening angle of the Slot

        Parameters
        ----------
        self : SlotM14
            A SlotM14 object

        Returns
        -------
        alpha: float
            Average opening angle of the slot [rad]

        """

        return self.W0

    # cf Methods.Slot.SlotM14.comp_height
    def comp_height(self):
        """Compute the height of the Slot.
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotM14
            A SlotM14 object

        Returns
        -------
        Htot: float
            Height of the slot [m]

        """

        return self.H0

    # cf Methods.Slot.SlotM14.comp_height_active
    def comp_height_active(self):
        """Compute the height of the active area

        Parameters
        ----------
        self : SlotM14
            A SlotM14 object

        Returns
        -------
        Hwind: float
            Height of the active area [m]

        """

        return self.H1

    # cf Methods.Slot.SlotM14.comp_surface
    def comp_surface(self):
        """Compute the Slot total surface (by analytical computation).
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotM14
            A SlotM14 object

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

        S1 = np.pi * R1**2 * (self.W0 / (2 * np.pi))
        S2 = np.pi * R2**2 * (self.W0 / (2 * np.pi))

        return abs(S1 - S2)

    # cf Methods.Slot.SlotM14.comp_surface_active
    def comp_surface_active(self):
        """Compute the Slot inner active surface (by analytical computation)

        Parameters
        ----------
        self : SlotM14
            A SlotM14 object

        Returns
        -------
        Swind: float
            Slot inner active surface [m**2]

        """

        point_dict = self._comp_point_coordinate()
        ZM1 = point_dict["ZM1"]
        ZM2 = point_dict["ZM2"]

        R1 = abs(ZM1)
        R2 = abs(ZM2)

        S1 = np.pi * R1**2 * (self.W1 / (2 * np.pi))
        S2 = np.pi * R2**2 * (self.W1 / (2 * np.pi))

        # Arc (Zm1,0,Zm2)
        alpha = -2 * np.angle(ZM2)
        Sarc1 = (R2**2.0) / 2.0 * (alpha - np.sin(alpha))

        # Arc (ZM1, Zc, ZM2)
        alpha = 2 * float(np.arcsin(-ZM2.imag / self.Rtopm))
        Sarc2 = (self.Rtopm**2.0) / 2.0 * (alpha - np.sin(alpha))

        return abs(S1 - S2) - Sarc1 + Sarc2

    # cf Methods.Slot.SlotM14.get_surface_active
    def get_surface_active(self, alpha=0, delta=0):
        """Return the full active surface

        Parameters
        ----------
        self : SlotM14
            A SlotM14 object
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
        Rbo = self.get_Rbo()

        point_dict = self._comp_point_coordinate()
        ZM1 = point_dict["ZM1"]
        ZM2 = point_dict["ZM2"]
        ZM3 = point_dict["ZM3"]
        ZM4 = point_dict["ZM4"]
        Z1 = point_dict["Z1"]
        Z4 = point_dict["Z4"]

        curve_list = list()
        # Case Z2-Z1 overlapping with ZM1-ZM2
        if self.H0 != 0 and self.H0 < self.H1 and self.W0 == self.W1:
            curve_list.append(Segment(ZM1, Z1))
            curve_list.append(Segment(Z1, ZM2))
        else:
            curve_list.append(Segment(ZM1, ZM2))

        if self.is_outwards():
            curve_list.append(Arc1(ZM2, ZM3, self.Rtopm, is_trigo_direction=True))
        else:
            curve_list.append(Arc1(ZM2, ZM3, self.Rtopm, is_trigo_direction=True))

        # Case Z3-Z4 overlapping with ZM3-ZM4
        if self.H0 != 0 and self.H0 < self.H1 and self.W0 == self.W1:
            curve_list.append(Segment(ZM3, Z4))
            curve_list.append(Segment(Z4, ZM4))
        else:
            curve_list.append(Segment(ZM3, ZM4))

        if self.is_outwards():
            curve_list.append(Arc1(ZM4, ZM1, -Rbo - self.H0, is_trigo_direction=False))
        else:
            curve_list.append(Arc1(ZM4, ZM1, -Rbo + self.H0, is_trigo_direction=False))

        Zmid = (abs(ZM1) + abs(ZM3)) / 2  # ref. point on x-axis with respective radius

        surface = SurfLine(
            line_list=curve_list, label="Wind_" + st + "_R0_T0_S0", point_ref=Zmid
        )

        # Apply transformation
        surface.rotate(alpha)
        surface.translate(delta)

        return surface

    # cf Methods.Slot.SlotM14.is_airgap_active
    def is_airgap_active(self):
        """Return True if a part or the full active surface is in the airgap

        Parameters
        ----------
        self : SlotM14
            A SlotM14 object

        Returns
        -------
        is_airgap_active : bool
            True if a part or the full active surface is in the airgap
        """

        return self.comp_height_active() > self.H0

    # cf Methods.Slot.SlotM14.is_full_pitch_active
    def is_full_pitch_active(self):
        """Returns True if the active surface angular width
        matches the slot pitch (like SlotM17 or SlotM18)
        (used to set Boundary conditions in FEMM airgap)

        Parameters
        ----------
        self : SlotM14
            A SlotM14 object

        Returns
        -------
        is_full_pitch_active : bool
            True if the active surface angular width matches the slot pitch
        """

        return self.W1 == 2 * np.pi / self.Zs

    # cf Methods.Slot.SlotM14.plot_schematics
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
        self : SlotM14
            A SlotM14 object
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
            slot = type(self)(
                Zs=4, W0=np.pi / 8, H0=0.02, H1=0.02, W1=np.pi / 8 * 0.75, Rtopm=0.06
            )
            lam = LamSlot(
                Rint=0.1, Rext=0.135, is_internal=True, is_stator=False, slot=slot
            )
            if is_return_default:
                return lam
            else:
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
                alpha=np.pi / self.Zs, is_show_fig=False, fig=fig, ax=ax
            )  # center slot on Ox axis
            point_dict = self._comp_point_coordinate()
            if self.is_outwards():
                sign = +1
            else:
                sign = -1
            Rbo = self.get_Rbo()

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
                R = Rbo + sign * self.H0 * 1.1
                line = Arc1(
                    begin=R * np.exp(-1j * self.W0 / 2),
                    end=R * np.exp(1j * self.W0 / 2),
                    radius=R,
                    is_trigo_direction=True,
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="W0",
                    offset_label=-1 * sign * self.H0 * 0.3
                    + 1j * point_dict["ZM4"].imag * 0.3,
                    fontsize=SC_FONT_SIZE,
                )
                # W1
                R = self.get_Rbo() + sign * (self.H0 - self.H1 * 1.5)
                line = Arc1(
                    begin=R * np.exp(-1j * self.W1 / 2),
                    end=R * np.exp(1j * self.W1 / 2),
                    radius=R,
                    is_trigo_direction=True,
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="W1",
                    offset_label=-1 * sign * self.H0 * 0.2,
                    fontsize=SC_FONT_SIZE,
                )
                # H0
                line = Segment(point_dict["Z1"], point_dict["Z2"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="H0",
                    offset_label=1j * point_dict["Z4"].imag * 0.1,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # H1
                line = Segment(point_dict["ZM3"], point_dict["ZM4"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="H1",
                    offset_label=1j * point_dict["Z4"].imag * 0.2,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # Rtopm
                line = Segment(point_dict["Zc"], point_dict["ZM0"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="Rtopm",
                    offset_label=sign * self.Rtopm * 0.4
                    + 1j * point_dict["ZM4"].imag * 0.3,
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
                # Z1 Line
                line = Segment(0, Rbo * 2 * np.exp(-1j * self.W0 / 2))
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # Z2 Line
                line = Segment(0, Rbo * 2 * np.exp(1j * self.W0 / 2))
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # ZM1 Line
                line = Segment(0, Rbo * 2 * np.exp(-1j * self.W1 / 2))
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # ZM2 Line
                line = Segment(0, Rbo * 2 * np.exp(1j * self.W1 / 2))
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # Top arc
                line = Arc1(
                    begin=point_dict["Z1"],
                    end=point_dict["Z4"],
                    radius=self.get_Rbo(),
                    is_trigo_direction=True,
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # Magnet Arc
                line = Segment(point_dict["Zc"], point_dict["ZM2"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                line = Segment(point_dict["Zc"], point_dict["ZM3"])
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
            W = point_dict["Z4"].imag * 1.2
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
        super(SlotM14, self).__init__(Zs=Zs, wedge_mat=wedge_mat, is_bore=is_bore)
        # The class is frozen (in Slot init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        SlotM14_str = ""
        # Get the properties inherited from Slot
        SlotM14_str += super(SlotM14, self).__str__()
        SlotM14_str += "W0 = " + str(self.W0) + linesep
        SlotM14_str += "H0 = " + str(self.H0) + linesep
        SlotM14_str += "W1 = " + str(self.W1) + linesep
        SlotM14_str += "H1 = " + str(self.H1) + linesep
        SlotM14_str += "Rtopm = " + str(self.Rtopm) + linesep
        return SlotM14_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from Slot
        if not super(SlotM14, self).__eq__(other):
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
            super(SlotM14, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
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
            other._Rtopm is not None
            and self._Rtopm is not None
            and np.isnan(other._Rtopm)
            and np.isnan(self._Rtopm)
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
        S += super(SlotM14, self).__sizeof__()
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
        SlotM14_dict = super(SlotM14, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        SlotM14_dict["W0"] = self.W0
        SlotM14_dict["H0"] = self.H0
        SlotM14_dict["W1"] = self.W1
        SlotM14_dict["H1"] = self.H1
        SlotM14_dict["Rtopm"] = self.Rtopm
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        SlotM14_dict["__class__"] = "SlotM14"
        return SlotM14_dict

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
        super(SlotM14, self)._set_None()

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
        doc="""Magnet angular width

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
