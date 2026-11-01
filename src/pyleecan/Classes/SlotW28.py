# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Slot/SlotW28.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Slot/SlotW28
"""

# Inline fallback report:
# These methods remain imported because their source or imports cannot be safely moved into this class.
# - check: module uses a wildcard import whose names cannot be resolved safely

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
from pyleecan.Methods.Slot.SlotW28.check import check
from pyleecan.Classes.Segment import Segment
from pyleecan.Classes.Arc1 import Arc1
from pyleecan.Classes.Arc3 import Arc3
import numpy as np, matplotlib.pyplot as plt
from pyleecan.Functions.labels import WIND_LAB, DRAW_PROP_LAB, SOP_LAB
from pyleecan.Classes.SurfLine import SurfLine
from pyleecan.Methods.Slot.SlotW28.plot_schematics import MAGNET_COLOR
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


class SlotW28(Slot):

    VERSION = 1
    IS_SYMMETRICAL = 1

    # cf Methods.Slot.SlotW28._comp_line_dict
    def _comp_line_dict(self):
        """Define a dictionnary of the lines to draw the slot
        If a line has begin==end, it is replaced by "None" (dict has always the same number of keys)

        Parameters
        ----------
        self : SlotW28
            A SlotW28 object

        Returns
        -------
        line_dict: dict
            Dictionnary of the slot lines (key: line name, value: line object)
        """

        if self.is_outwards():
            rot_sign = 1  # Rotation direction for Arc1
        else:  # inward slot
            rot_sign = -1  # Rotation direction for Arc1
        point_dict = self._comp_point_coordinate()
        Z1 = point_dict["Z1"]
        Z2 = point_dict["Z2"]
        Z3 = point_dict["Z3"]
        Z4 = point_dict["Z4"]
        Z5 = point_dict["Z5"]
        Z6 = point_dict["Z6"]
        Z7 = point_dict["Z7"]
        Z8 = point_dict["Z8"]

        # Creation of curve
        line_dict = dict()
        if self.H0 > 0:
            line_dict["1-2"] = Segment(Z1, Z2)
        else:
            line_dict["1-2"] = None
        line_dict["2-3"] = Arc1(Z2, Z3, rot_sign * self.R1, self.is_outwards())
        line_dict["3-4"] = Segment(Z3, Z4)
        line_dict["4-5"] = Arc3(Z4, Z5, self.is_outwards())
        line_dict["5-6"] = Segment(Z5, Z6)
        line_dict["6-7"] = Arc1(Z6, Z7, rot_sign * self.R1, self.is_outwards())
        if self.H0 > 0:
            line_dict["7-8"] = Segment(Z7, Z8)
        else:
            line_dict["7-8"] = None

        # Closing Arc (Rbo)
        line_dict["8-1"] = Arc1(Z8, Z1, -self.get_Rbo(), is_trigo_direction=False)

        # Closing Active part
        line_dict["2-7"] = Segment(Z2, Z7)
        line_dict["7-2"] = Segment(Z7, Z2)

        return line_dict

    # cf Methods.Slot.SlotW28._comp_point_coordinate
    def _comp_point_coordinate(self):
        """Compute the point coordinates needed to plot the Slot.

        Parameters
        ----------
        self : SlotW28
            A SlotW28 object

        Returns
        -------
        point_dict: dict
            A dict of the slot point coordinates
        """
        Rbo = self.get_Rbo()

        # alpha is the angle to rotate Z0 so ||Z1,Z8|| = W0
        alpha = float(np.arcsin(self.W0 / (2 * Rbo)))
        slot_pitch = 2 * np.pi / self.Zs

        # comp point coordinate (in complex)
        Z0 = Rbo * np.exp(1j * 0)
        Z8 = Z0 * np.exp(-1j * alpha)

        if self.is_outwards():
            Z7 = Z8 + self.H0
            # Rotation to get the tooth on X axis
            Z7 = Z7 * np.exp(1j * slot_pitch / 2)
            Z8 = Z8 * np.exp(1j * slot_pitch / 2)
            # Z7 = x7 + 1j*y7
            # Z6 = x + 1j * W3/2
            # C2,Z6 _|_ Z6,Z5 => Re(C2) = Re(Z6)
            # ||Z6,zc2|| = R1 => Zc2 = x + 1j*(W3/2+R1)
            # ||Z7,zc2||² = R1² => (x7-x)²+ (y7-(W3/2+R1))² = R1²

            # x² - 2*x7 x + (x7²+(y7-(W3/2+R1))²-R1²) = 0
            # D = 4*x7² - 4*(x7²+(y7-(W3/2+R1))²-R1²) = -4((y7-(W3/2+R1))²-R1²)
            # x = x7 + sqrt(-4((y7-(W3/2+R1))²-R1²))/2
            Z6 = (
                Z7.real
                + np.sqrt(
                    -4 * ((Z7.imag - (self.W3 / 2.0 + self.R1)) ** 2 - self.R1**2)
                )
                / 2
                + 1j * self.W3 / 2.0
            )
            Z5 = Z6 + self.H3
            rot_sign = 1
        else:  # inward slot
            Z7 = Z8 - self.H0
            # Rotation to get the tooth on X axis
            Z7 = Z7 * np.exp(1j * slot_pitch / 2)
            Z8 = Z8 * np.exp(1j * slot_pitch / 2)
            Z6 = (
                Z7.real
                - np.sqrt(
                    -4 * ((Z7.imag - (self.W3 / 2.0 + self.R1)) ** 2 - self.R1**2)
                )
                / 2
                + 1j * self.W3 / 2.0
            )
            Z5 = Z6 - self.H3
            rot_sign = -1

        # Tooth ref to slot
        Z1, Z2, Z3, Z4 = (
            Z8 * np.exp(-1j * slot_pitch / 2),
            Z7 * np.exp(-1j * slot_pitch / 2),
            Z6 * np.exp(-1j * slot_pitch / 2),
            Z5 * np.exp(-1j * slot_pitch / 2),
        )

        point_dict = dict()
        point_dict["Z1"] = Z1
        point_dict["Z2"] = Z2
        point_dict["Z3"] = Z3
        point_dict["Z4"] = Z4
        # symetry
        point_dict["Z5"] = Z4.conjugate()
        point_dict["Z6"] = Z3.conjugate()
        point_dict["Z7"] = Z2.conjugate()
        point_dict["Z8"] = Z1.conjugate()
        # Center
        A = Arc1(Z2, Z3, rot_sign * self.R1, self.is_outwards())
        point_dict["Zc1"] = A.get_center()
        point_dict["Zc2"] = (point_dict["Z4"] + point_dict["Z5"]) / 2
        point_dict["Zc3"] = point_dict["Zc1"].conjugate()
        return point_dict

    # cf Methods.Slot.SlotW28.build_geometry
    def build_geometry(self):
        """Compute the curve (Line) needed to plot the object.
        The ending point of a curve is the starting point of the next curve in
        the list

        Parameters
        ----------
        self : SlotW28
            A SlotW28 object

        Returns
        -------
        curve_list: list
            A list of 4 Segment and 3 Arc1

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

    # cf Methods.Slot.SlotW28.check
    check = check

    # cf Methods.Slot.SlotW28.comp_angle_opening
    def comp_angle_opening(self):
        """Compute the average opening angle of the Slot

        Parameters
        ----------
        self : SlotW28
            A SlotW28 object

        Returns
        -------
        alpha: float
            Average opening angle of the slot [rad]

        """
        Rbo = self.get_Rbo()

        return float(2 * np.arcsin(self.W0 / (2 * Rbo)))

    # cf Methods.Slot.SlotW28.comp_height
    def comp_height(self):
        """Compute the height of the Slot.
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotW28
            A SlotW28 object

        Returns
        -------
        Htot: float
            Height of the slot [m]

        """
        Rbo = self.get_Rbo()

        point_dict = self._comp_point_coordinate()
        Z5 = point_dict["Z5"]
        if self.is_outwards():
            Ztan2 = Z5 + Z5.imag * (1 - 1j)
            return Ztan2.real - Rbo
        else:
            Ztan2 = Z5 + Z5.imag * (-1 - 1j)
            return Rbo - Ztan2.real

    # cf Methods.Slot.SlotW28.comp_height_active
    def comp_height_active(self):
        """Compute the height of the winding area

        Parameters
        ----------
        self : SlotW28
            A SlotW28 object

        Returns
        -------
        Hwind: float
            Height of the winding area [m]

        """

        point_dict = self._comp_point_coordinate()
        Z2 = point_dict["Z2"]
        Z5 = point_dict["Z5"]
        Z7 = point_dict["Z7"]
        if self.is_outwards():
            Ztan2 = Z5 + Z5.imag * (-1 - 1j)
        else:
            Ztan2 = Z5 + Z5.imag * (+1 - 1j)
        Ztan1 = (Z2 + Z7) / 2.0

        return abs(Ztan2 - Ztan1)

    # cf Methods.Slot.SlotW28.comp_surface
    def comp_surface(self):
        """Compute the Slot total surface (by analytical computation).
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotW28
            A SlotW28 object

        Returns
        -------
        S: float
            Slot total surface [m**2]

        """
        return self.comp_surface_active() + self.comp_surface_opening()

    # cf Methods.Slot.SlotW28.comp_surface_opening
    def comp_surface_opening(self):
        """Compute the Slot total surface (by analytical computation).
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotW28
            A SlotW28 object

        Returns
        -------
        S: float
            Slot total surface [m**2]

        """
        Rbo = self.get_Rbo()

        S1 = self.H0 * self.W0

        # The bottom is an arc
        alpha = self.comp_angle_opening()
        Sarc = (Rbo**2.0) / 2.0 * (alpha - np.sin(alpha))

        # Because Slamination = S - Zs * Sslot
        if self.is_outwards():
            return S1 - Sarc
        else:
            return S1 + Sarc

    # cf Methods.Slot.SlotW28.get_surface_active
    def get_surface_active(self, alpha=0, delta=0):
        """Return the full winding surface

        Parameters
        ----------
        self : SlotW28
            A SlotW28 object
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
        if self.is_outwards():
            Zmid = self.get_Rbo() + self.H0 + self.R1 + self.H3 / 2
        else:
            Zmid = self.get_Rbo() - self.H0 - self.R1 - self.H3 / 2
        label = self.parent.get_label() + "_" + WIND_LAB + "_R0-T0-S0"
        surface = SurfLine(line_list=curve_list, label=label, point_ref=Zmid)

        # Apply transformation
        surface.rotate(alpha)
        surface.translate(delta)

        return surface

    # cf Methods.Slot.SlotW28.get_surface_opening
    def get_surface_opening(self, alpha=0, delta=0):
        """Return the list of surfaces defining the opening area of the Slot

        Parameters
        ----------
        self : SlotW28
            A SlotW28 object
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

    # cf Methods.Slot.SlotW28.plot_schematics
    def plot_schematics(
        self,
        is_default=False,
        is_return_default=False,
        is_add_point_label=False,
        is_add_schematics=True,
        is_add_main_line=True,
        type_add_active=1,
        save_path=None,
        is_show_fig=True,
        fig=None,
        ax=None,
    ):
        """Plot the schematics of the slot

        Parameters
        ----------
        self : SlotW28
            A SlotW28 object
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
            0: No active surface, 1: active surface as winding, 2: active surface as magnet, 3: active surface as winding + wedges
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
            slot = type(self)(Zs=16, H0=10e-3, W0=20e-3, R1=10e-3, H3=60e-3, W3=20e-3)
            lam = LamSlot(
                Rint=0.135, Rext=0.3, is_internal=False, is_stator=True, slot=slot
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
                sign = 1
            else:
                sign = -1
            Rbo = self.get_Rbo()
            sp = 2 * np.pi / self.Zs  # Slot pitch
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
                line = Segment(point_dict["Z1"], point_dict["Z8"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="W0",
                    offset_label=-self.H0 * 1.3,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # H0
                line = Segment(
                    point_dict["Z1"] * np.exp(1j * sp),
                    point_dict["Z2"] * np.exp(1j * sp),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="H0",
                    offset_label=-1j * self.H0 * 0.8,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # W3
                line = Segment(
                    (point_dict["Z5"] + point_dict["Z6"]) / 2,
                    (
                        point_dict["Z4"] * np.exp(1j * sp)
                        + point_dict["Z3"] * np.exp(1j * sp)
                    )
                    / 2,
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="W3",
                    offset_label=self.H0 * 0.4,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # H3
                line = Segment(point_dict["Z3"], point_dict["Z4"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    label="H3",
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    offset_label=1j * self.W0 * 0.3,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # R1
                line = Segment(point_dict["Zc3"], point_dict["Z7"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    label="R1",
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    offset_label=self.H0 * 0.8,
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
                # Top arc
                line = Arc1(
                    begin=point_dict["Z1"],
                    end=point_dict["Z8"],
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
                # Tooth axis
                line = Segment(0, lam.Rext * 1.5 * np.exp(1j * sp / 2))
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                line = Segment(0, lam.Rext * 1.5 * np.exp(-1j * sp / 2))
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # Radius lines
                line = Segment(point_dict["Z4"], point_dict["Z5"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                line = Segment(point_dict["Zc1"], point_dict["Z2"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                line = Segment(point_dict["Zc1"], point_dict["Z3"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                line = Segment(point_dict["Zc3"], point_dict["Z6"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                line = Segment(point_dict["Zc3"], point_dict["Z7"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )

            if type_add_active in [1, 3]:  # Wind and Wedge
                is_add_wedge = type_add_active == 3
                self.plot_active(
                    fig=fig, ax=ax, is_show_fig=False, is_add_wedge=is_add_wedge
                )
            elif type_add_active == 2:  # Magnet
                self.plot_active(
                    fig=fig,
                    ax=ax,
                    is_show_fig=False,
                    enforced_default_color=MAGNET_COLOR,
                )

            # Zooming and cleaning
            W = (point_dict["Z4"] * np.exp(1j * sp)).imag * 1.2
            Rint = min(point_dict["Z5"].real, point_dict["Z1"].real)
            Rext = max(point_dict["Z5"].real, point_dict["Z1"].real)

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
        R1=0.003,
        W3=0.005,
        H3=0.003,
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
            if "R1" in list(init_dict.keys()):
                R1 = init_dict["R1"]
            if "W3" in list(init_dict.keys()):
                W3 = init_dict["W3"]
            if "H3" in list(init_dict.keys()):
                H3 = init_dict["H3"]
            if "Zs" in list(init_dict.keys()):
                Zs = init_dict["Zs"]
            if "wedge_mat" in list(init_dict.keys()):
                wedge_mat = init_dict["wedge_mat"]
            if "is_bore" in list(init_dict.keys()):
                is_bore = init_dict["is_bore"]
        # Set the properties (value check and convertion are done in setter)
        self.W0 = W0
        self.H0 = H0
        self.R1 = R1
        self.W3 = W3
        self.H3 = H3
        # Call Slot init
        super(SlotW28, self).__init__(Zs=Zs, wedge_mat=wedge_mat, is_bore=is_bore)
        # The class is frozen (in Slot init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        SlotW28_str = ""
        # Get the properties inherited from Slot
        SlotW28_str += super(SlotW28, self).__str__()
        SlotW28_str += "W0 = " + str(self.W0) + linesep
        SlotW28_str += "H0 = " + str(self.H0) + linesep
        SlotW28_str += "R1 = " + str(self.R1) + linesep
        SlotW28_str += "W3 = " + str(self.W3) + linesep
        SlotW28_str += "H3 = " + str(self.H3) + linesep
        return SlotW28_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from Slot
        if not super(SlotW28, self).__eq__(other):
            return False
        if other.W0 != self.W0:
            return False
        if other.H0 != self.H0:
            return False
        if other.R1 != self.R1:
            return False
        if other.W3 != self.W3:
            return False
        if other.H3 != self.H3:
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
            super(SlotW28, self).compare(
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
        if (
            other._W3 is not None
            and self._W3 is not None
            and np.isnan(other._W3)
            and np.isnan(self._W3)
        ):
            pass
        elif other._W3 != self._W3:
            if is_add_value:
                val_str = " (self=" + str(self._W3) + ", other=" + str(other._W3) + ")"
                diff_list.append(name + ".W3" + val_str)
            else:
                diff_list.append(name + ".W3")
        if (
            other._H3 is not None
            and self._H3 is not None
            and np.isnan(other._H3)
            and np.isnan(self._H3)
        ):
            pass
        elif other._H3 != self._H3:
            if is_add_value:
                val_str = " (self=" + str(self._H3) + ", other=" + str(other._H3) + ")"
                diff_list.append(name + ".H3" + val_str)
            else:
                diff_list.append(name + ".H3")
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from Slot
        S += super(SlotW28, self).__sizeof__()
        S += getsizeof(self.W0)
        S += getsizeof(self.H0)
        S += getsizeof(self.R1)
        S += getsizeof(self.W3)
        S += getsizeof(self.H3)
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
        SlotW28_dict = super(SlotW28, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        SlotW28_dict["W0"] = self.W0
        SlotW28_dict["H0"] = self.H0
        SlotW28_dict["R1"] = self.R1
        SlotW28_dict["W3"] = self.W3
        SlotW28_dict["H3"] = self.H3
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        SlotW28_dict["__class__"] = "SlotW28"
        return SlotW28_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        W0_val = self.W0
        H0_val = self.H0
        R1_val = self.R1
        W3_val = self.W3
        H3_val = self.H3
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
            R1=R1_val,
            W3=W3_val,
            H3=H3_val,
            Zs=Zs_val,
            wedge_mat=wedge_mat_val,
            is_bore=is_bore_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.W0 = None
        self.H0 = None
        self.R1 = None
        self.W3 = None
        self.H3 = None
        # Set to None the properties inherited from Slot
        super(SlotW28, self)._set_None()

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
        doc="""Slot isthmus width.

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
        doc="""Slot edge radius

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

    def _get_H3(self):
        """getter of H3"""
        return self._H3

    def _set_H3(self, value):
        """setter of H3"""
        check_var("H3", value, "float", Vmin=0)
        self._H3 = value

    H3 = property(
        fget=_get_H3,
        fset=_set_H3,
        doc="""Tooth height

        :Type: float
        :min: 0
        """,
    )
