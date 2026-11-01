# File generated according to Generator/ClassesRef/Slot/SlotW14.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Slot/SlotW14"""

from os import linesep
from sys import getsizeof

import matplotlib.pyplot as plt
import numpy as np
from pyleecan.Classes.SurfLine import SurfLine

from pyleecan.Classes import ParentMissingError
from pyleecan.Classes._check import check_var
from pyleecan.Classes.Arc1 import Arc1
from pyleecan.Classes.LamSlot import LamSlot
from pyleecan.Classes.Segment import Segment
from pyleecan.Classes.Slot import Slot
from pyleecan.definitions import config_dict
from pyleecan.Functions.Geometry.inter_line_line import inter_line_line
from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.labels import DRAW_PROP_LAB, SOP_LAB, WIND_LAB
from pyleecan.Functions.load import load_init_dict
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
from pyleecan.Functions.save import save


class SlotW14(Slot):

    VERSION = 1
    IS_SYMMETRICAL = 1
    MAGNET_COLOR = config_dict["PLOT"]["COLOR_DICT"]["MAGNET_COLOR"]

    # cf Methods.Slot.SlotW14._comp_line_dict
    def _comp_line_dict(self):
        """Define a dictionnary of the lines to draw the slot
        If a line has begin==end, it is replaced by "None" (dict has always the same number of keys)

        Parameters
        ----------
        self : SlotW14
            A SlotW14 object

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
        Z9 = point_dict["Z9"]

        # Creation of curve
        line_dict = dict()
        if self.H0 > 0:
            line_dict["1-2"] = Segment(Z1, Z2)
        else:
            line_dict["1-2"] = None

        line_dict["2-3"] = Segment(Z2, Z3)
        line_dict["3-4"] = Segment(Z3, Z4)
        line_dict["4-5"] = Segment(Z4, Z5)
        line_dict["5-6"] = Segment(Z5, Z6)
        line_dict["6-7"] = Segment(Z6, Z7)
        line_dict["7-8"] = Segment(Z7, Z8)
        if self.H0 > 0:
            line_dict["8-9"] = Segment(Z8, Z9)
        else:
            line_dict["8-9"] = None

        # Closing Arc (Rbo)
        line_dict["9-1"] = Arc1(Z9, Z1, -self.get_Rbo(), is_trigo_direction=False)

        # Closing Active part
        line_dict["3-7"] = Segment(Z3, Z7)
        line_dict["7-3"] = Segment(Z7, Z3)
        line_dict["8-2"] = Segment(Z8, Z2)

        # closing wedge
        line_dict["8-2"] = Segment(Z8, Z2)
        line_dict["2-8"] = Segment(Z2, Z8)

        return line_dict

    # cf Methods.Slot.SlotW14._comp_point_coordinate
    def _comp_point_coordinate(self):
        """Compute the point coordinates needed to plot the Slot.

        Parameters
        ----------
        self : SlotW14
            A SlotW14 object

        Returns
        -------
        point_dict: dict
            A dict of the slot point coordinates
        """
        Rbo = self.get_Rbo()
        hssp = np.pi / self.Zs

        # alpha is the angle to rotate P0 so ||P1,P9|| = W0
        alpha = np.arcsin(self.W0 / (2 * Rbo))
        Harc = float(Rbo * (1 - np.cos(alpha)))
        H1 = self.get_H1()

        Z1 = Rbo * np.exp(-1j * alpha)
        if self.is_outwards():
            R1 = Rbo - Harc + self.H0 + H1
            Z2 = Z1 + self.H0
        else:
            R1 = Rbo - Harc - self.H0 - H1
            Z2 = Z1 - self.H0
        # In the slot ref: Z3=x7+j*y7 with x7 = R1
        # In the tooth ref: Zt7 = xt7 + j*yt7 with yt7 = W3/2
        # Zt7 = Z3 * exp(1j*hsp) = (x7+jy7)*(cos(hsp)+1j*sin(hsp))
        # yt7 = W3/2 = x7*sin(hsp)+y7*cos(hsp)
        Z3 = R1 + 1j * (self.W3 / 2 - R1 * np.sin(hssp)) / np.cos(hssp)

        # Z3t is Z3 in tooth ref
        Z3t = Z3 * np.exp(1j * hssp)
        if self.is_outwards():
            Z4t = Z3t + self.H3
        else:
            Z4t = Z3t - self.H3
        # In the slot ref: Z5=x5+j*y5 with y5 = 0
        # In the tooth ref: Zt5 = xt5 + j*yt5 with xt5 = xt6
        # Zt5 = Z5 * exp(1j*hsp) = x5*cos(hsp)+1j*x5*sin(hsp)
        # x5 = real(Z4t)/cos(hsp)

        Z5 = Z4t.real / np.cos(hssp)
        Z4 = Z4t * np.exp(-1j * hssp)

        point_dict = dict()
        # symetry
        point_dict["Z1"] = Z1
        point_dict["Z2"] = Z2
        point_dict["Z3"] = Z3
        point_dict["Z4"] = Z4
        point_dict["Z5"] = Z5
        point_dict["Z6"] = Z4.conjugate()
        point_dict["Z7"] = Z3.conjugate()
        point_dict["Z8"] = Z2.conjugate()
        point_dict["Z9"] = Z1.conjugate()

        return point_dict

    # cf Methods.Slot.SlotW14.build_geometry
    def build_geometry(self):
        """Compute the curve (Segment) needed to plot the Slot.
        The ending point of a curve is the starting point of the next curve in
        the list

        Parameters
        ----------
        self : SlotW14
            A SlotW14 object

        Returns
        -------
        curve_list: list
            A list of 8 Segment

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
        ]
        return [line for line in curve_list if line is not None]

    # cf Methods.Slot.SlotW14.check
    def check(self):
        """Check that the SlotW14 object is correct

        Parameters
        ----------
        self : SlotW14
            A SlotW14 object

        Returns
        -------
        None

        Raises
        -------
        S14_Rbo0CheckError
            You must have W0/2 < Rbo
        S14_Rbo1CheckError
            W3 is too high comparing to the lamination bore radius (Rbo)
        """

        Rbo = self.get_Rbo()
        H1 = self.get_H1()

        if self.W0 * 0.5 / Rbo >= 1:
            raise S14_Rbo0CheckError("You must have W0/2 < Rbo")

        if self.is_outwards():
            R1 = Rbo + self.H0 + H1
        else:
            R1 = Rbo - self.H0 - H1

        if self.W3 * 0.5 / R1 >= 1:
            raise S14_Rbo1CheckError(
                "W3 is too high comparing to the lamination bore radius (Rbo)"
            )

    # cf Methods.Slot.SlotW14.comp_angle_opening
    def comp_angle_opening(self):
        """Compute the average opening angle of the Slot

        Parameters
        ----------
        self : SlotW14
            A SlotW14 object

        Returns
        -------
        alpha: float
            Average opening angle of the slot [rad]

        """

        Rbo = self.get_Rbo()

        return float(2 * np.arcsin(self.W0 / (2 * Rbo)))

    # cf Methods.Slot.SlotW14.comp_height
    def comp_height(self):
        """Compute the height of the Slot.
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotW14
            A SlotW14 object

        Returns
        -------
        Htot: float
            Height of the slot [m]

        """

        Rbo = self.get_Rbo()

        point_dict = self._comp_point_coordinate()
        Z4 = point_dict["Z4"]
        Z5 = point_dict["Z5"]

        if self.is_outwards():
            return abs(Z5) - Rbo
        else:
            return Rbo - abs(Z4)

    # cf Methods.Slot.SlotW14.comp_height_active
    def comp_height_active(self):
        """Compute the height of the winding area

        Parameters
        ----------
        self : SlotW14
            A SlotW14 object

        Returns
        -------
        Hwind: float
            Height of the winding area [m]

        """
        H1 = self.get_H1()
        Rbo = self.get_Rbo()

        # alpha is the angle to rotate P0 so ||P1,P10|| = W0
        alpha = np.arcsin(self.W0 / (2 * Rbo))

        # Compute W1 to have tooth width at W3
        Harc = Rbo * (1 - np.cos(alpha / 2))

        if self.is_outwards():
            R1 = Rbo - Harc + self.H0 + H1
        else:
            R1 = Rbo + Harc - self.H0 - H1

        theta1 = np.arcsin(self.W3 * 0.5 / R1) * 2
        hsp = np.pi / self.Zs
        W1 = np.sin((hsp * 2 - theta1) * 0.5) * R1 * 2

        Z9 = Rbo * np.exp(-1j * alpha)

        if self.is_outwards():
            Z8 = Z9 + self.H0
            Z7 = Z8 + H1 - (W1 - self.W0) * 1j / 2
        else:
            Z8 = Z9 - self.H0
            Z7 = Z8 - H1 - (W1 - self.W0) * 1j / 2

        # Rotate Z7 to get the tooth parallel to Ox
        Z7r = Z7 * np.exp(1j * hsp)
        if self.is_outwards():
            Z6r = Z7r + self.H3
        else:
            Z6r = Z7r - self.H3

        W2 = np.tan(hsp) * Z6r.real
        Z5r = Z6r.real + 1j * W2
        Z5 = Z5r * np.exp(-1j * hsp)
        Z3 = Z7.conjugate()

        Ztan1 = (Z3 + Z7) / 2.0
        Ztan2 = Z5

        return abs(Ztan1 - Ztan2)

    # cf Methods.Slot.SlotW14.comp_surface
    def comp_surface(self):
        """Compute the Slot total surface (by analytical computation).
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotW14
            A SlotW14 object

        Returns
        -------
        S: float
            Slot total surface [m**2]

        """

        if self.wedge_type == 1:
            return (
                self.comp_surface_active()
                + self.comp_surface_opening()
                + self.comp_surface_wedge()
            )

        return self.comp_surface_active() + self.comp_surface_opening()

    # cf Methods.Slot.SlotW14.comp_surface_active
    def comp_surface_active(self):
        """Compute the Slot inner surface for winding (by analytical computation)

        Parameters
        ----------
        self : SlotW14
            A SlotW14 object

        Returns
        -------
        Swind: float
            Slot inner surface for winding [m**2]

        """

        point_dict = self._comp_point_coordinate()
        Z4 = point_dict["Z4"]
        Z5 = point_dict["Z5"]
        Z6 = point_dict["Z6"]
        Z7 = point_dict["Z7"]

        # Compute area of triangle Z5,Z6
        S1 = abs(Z6.imag) * abs(Z5.real - Z4.real) / 2
        S2 = (abs(Z6.imag) + abs(Z7.imag)) * abs(Z7.real - Z6.real) / 2

        if self.is_outwards():
            return (S1 + S2) * 2
        else:
            return (S2 - S1) * 2

    # cf Methods.Slot.SlotW14.comp_surface_opening
    def comp_surface_opening(self):
        """Compute the Slot opening surface (by analytical computation).
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotW14
            A SlotW14 object

        Returns
        -------
        S: float
            Slot opening surface [m**2]

        """
        H1 = self.get_H1()
        Rbo = self.get_Rbo()
        point_dict = self._comp_point_coordinate()
        Z7 = point_dict["Z7"]
        W1 = abs(Z7.imag) * 2

        S1 = (W1 + self.W0) * H1 / 2
        S0 = self.W0 * self.H0

        # The bottom is an arc
        alpha = self.comp_angle_opening()
        Sarc = (Rbo**2.0) / 2.0 * (alpha - np.sin(alpha))

        # Selection type Wedge
        if self.wedge_type == 0:
            if self.is_outwards():
                return S1 + S0 - Sarc
            else:
                return S1 + S0 + Sarc

        if self.wedge_type == 1:
            if self.is_outwards():
                return S0 - Sarc
            else:
                return S0 + Sarc

    # cf Methods.Slot.SlotW14.comp_surface_wedge
    def comp_surface_wedge(self):
        """Compute the Slot wedge surface (by analytical computation).
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotW14
            A SlotW14 object

        Returns
        -------
        S: float
            Slot wedge surface [m**2]

        """
        # Selection type Wedge
        if self.wedge_type == 0:
            return self.comp_surface_opening()

        if self.wedge_type == 1:
            H1 = self.get_H1()
            point_dict = self._comp_point_coordinate()
            Z7 = point_dict["Z7"]
            W1 = abs(Z7.imag) * 2

            return (W1 + self.W0) * H1 / 2

    # cf Methods.Slot.SlotW14.get_H1
    def get_H1(self):
        """Return H1 in [m]

        Parameters
        ----------
        self : SlotW14
            A SlotW14 object

        Returns
        -------
        H1: float
            H1 in [m]

        """

        # H1 in rad
        if self.H1_is_rad:
            Rbo = self.get_Rbo()
            hssp = np.pi / self.Zs

            # alpha is the angle to rotate P0 so ||P1,P9|| = W0
            alpha = np.arcsin(self.W0 / (2 * Rbo))
            Harc = float(Rbo * (1 - np.cos(alpha)))

            Z1 = Rbo * np.exp(-1j * alpha)
            if self.is_outwards():
                R1 = Rbo - Harc + self.H0
                Z2 = Z1 + self.H0
            else:
                R1 = Rbo - Harc - self.H0
                Z2 = Z1 - self.H0

            Z3 = R1 + 1j * (self.W3 / 2 - R1 * np.sin(hssp)) / np.cos(hssp)

            # Z3t is Z3 in tooth ref
            Z3t = Z3 * np.exp(1j * hssp)
            if self.is_outwards():
                Z4t = Z3t + self.H3
            else:
                Z4t = Z3t - self.H3

            Z4 = Z4t * np.exp(-1j * hssp)
            # ending calcul slot point

            Zop = 0.5 * np.tan(self.H1)

            if self.is_outwards():
                Zc2 = Z2 - 0.5 * 1j + Zop
            else:
                Zc2 = Z2 - 0.5 * 1j - Zop

            ZiH = inter_line_line(Z3, Z4, Z2, Zc2)
            ZiH = ZiH[0]

            if self.is_outwards():
                H1 = abs(ZiH - Z3)
            else:
                H1 = abs(Z3 - ZiH)
            return H1  # convertion to m

        else:  # H1 in m
            return self.H1

    # cf Methods.Slot.SlotW14.get_surface_active
    def get_surface_active(self, alpha=0, delta=0):
        """Return the full winding surface

        Parameters
        ----------
        self : SlotW14
            A SlotW14 object
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
        H1 = self.get_H1()
        if H1 > 1e-6:
            curve_list = [
                line_dict["3-4"],
                line_dict["4-5"],
                line_dict["5-6"],
                line_dict["6-7"],
                line_dict["7-3"],
            ]
        else:
            # Add 2-3 and 8-2 to make sure that FEMM handles all the lines
            # cf (Tests\Validation\Magnetics\test_FEMM_fast_draw.py)
            curve_list = [
                line_dict["2-3"],
                line_dict["3-4"],
                line_dict["4-5"],
                line_dict["5-6"],
                line_dict["6-7"],
                line_dict["7-8"],
                line_dict["8-2"],
            ]
        curve_list = [line for line in curve_list if line is not None]

        # Only the closing arc (7-3) needs to be drawn (in FEMM)
        for curve in curve_list[:-1]:
            if curve.prop_dict is None:
                curve.prop_dict = dict()
            curve.prop_dict.update({DRAW_PROP_LAB: False})

        # Create surface
        label = f"{self.parent.get_label()}_{WIND_LAB}_R0-T0-S0"
        if self.is_outwards():
            Zmid = self.get_Rbo() + self.H0 + H1 + self.H3 / 2
        else:
            Zmid = self.get_Rbo() - self.H0 - H1 - self.H3 / 2
        surface = SurfLine(line_list=curve_list, label=label, point_ref=Zmid)

        # Apply transformation
        surface.rotate(alpha)
        surface.translate(delta)

        return surface

    # cf Methods.Slot.SlotW14.get_surface_opening
    def get_surface_opening(self, alpha=0, delta=0):
        """Return the list of surfaces defining the opening area of the Slot

        Parameters
        ----------
        self : SlotW14
            A SlotW14 object
        alpha : float
            float number for rotation (Default value = 0) [rad]
        delta : complex
            complex number for translation (Default value = 0)

        Returns
        -------
        surf_list : list
            list of surfaces objects
        """

        H1 = self.get_H1()
        # H0=H1=0 no opening
        if self.H0 == 0 and H1 == 0:
            return []

        line_dict = self._comp_line_dict()

        # Selection type Wedge
        if self.wedge_type == 0:
            # Create curve list

            curve_list = [
                line_dict["1-2"],
                line_dict["2-3"],
                line_dict["3-7"],
                line_dict["7-8"],
                line_dict["8-9"],
                line_dict["9-1"],
            ]
            # Create surface
            if self.is_outwards():
                Zmid = self.get_Rbo() + (self.H0 + H1) / 2
            else:
                Zmid = self.get_Rbo() - (self.H0 + H1) / 2

        else:
            # Create curve list
            curve_list = [
                line_dict["1-2"],
                line_dict["2-8"],
                line_dict["8-9"],
                line_dict["9-1"],
            ]
            # Create surface
            if self.is_outwards():
                Zmid = self.get_Rbo() + self.H0 / 2
            else:
                Zmid = self.get_Rbo() - self.H0 / 2

        curve_list = [line for line in curve_list if line is not None]

        # Only the closing arc (9-1) needs to be drawn (in FEMM)
        for curve in curve_list[:-1]:
            if curve.prop_dict is None:
                curve.prop_dict = dict()
            curve.prop_dict.update({DRAW_PROP_LAB: False})

        label = self.parent.get_label() + "_" + SOP_LAB + "_R0-T0-S0"
        surface = SurfLine(line_list=curve_list, label=label, point_ref=Zmid)

        # Apply transformation
        surface.rotate(alpha)
        surface.translate(delta)

        return [surface]

    # cf Methods.Slot.SlotW14.get_surface_wedge
    def get_surface_wedge(self, alpha=0, delta=0):
        """Return the list of surfaces defining the opening area of the Slot

        Parameters
        ----------
        self : SlotW14
            A SlotW14 object
        alpha : float
            float number for rotation (Default value = 0) [rad]
        delta : complex
            complex number for translation (Default value = 0)

        Returns
        -------
        surf_list : list
            list of surfaces objects
        """
        H1 = self.get_H1()
        # H0=H1=0 no opening
        if self.H0 == 0 and H1 == 0:
            return []

        # Create curve list
        line_dict = self._comp_line_dict()
        curve_list = [
            line_dict["2-3"],
            line_dict["3-7"],
            line_dict["7-8"],
            line_dict["8-2"],
        ]
        curve_list = [line for line in curve_list if line is not None]

        # Create surface
        if self.is_outwards():
            Zmid = self.get_Rbo() + self.H0 + H1 / 2
        else:
            Zmid = self.get_Rbo() - self.H0 + H1 / 2

        label = self.parent.get_label() + "_" + SOP_LAB + "_R0-T0-S0"
        surface = SurfLine(line_list=curve_list, label=label, point_ref=Zmid)

        # Apply transformation
        surface.rotate(alpha)
        surface.translate(delta)

        return [surface]

    # cf Methods.Slot.SlotW14.plot_schematics
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
        self : SlotW14
            A SlotW14 object
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
            0: No active surface, 1: active surface as winding, 2: active surface as magnet, 3: active surface as winding + wedges, 4: 4: type_active =3 and wedge_type = 1
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

        if type_add_active == 4 and is_default:  # type_wedge = 1
            slot = type(self)(
                Zs=12,
                W0=30e-3,
                W3=35e-3,
                H0=15e-3,
                H1=15e-3,
                H3=50e-3,
                wedge_type=1,
            )
            lam = LamSlot(
                Rint=0.135, Rext=0.25, is_internal=False, is_stator=True, slot=slot
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
                    type_add_active=3,
                    save_path=save_path,
                    is_show_fig=is_show_fig,
                    fig=fig,
                    ax=ax,
                )

        # Use some default parameter
        if is_default:
            slot = type(self)(
                Zs=12,
                W0=30e-3,
                W3=35e-3,
                H0=15e-3,
                H1=15e-3,
                H3=50e-3,
                wedge_type=0,
            )
            lam = LamSlot(
                Rint=0.135, Rext=0.25, is_internal=False, is_stator=True, slot=slot
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
            hsp = np.pi / self.Zs
            sp = 2 * np.pi / self.Zs
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

                line = Segment(point_dict["Z2"], point_dict["Z8"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="W0",
                    offset_label=self.H0 * 0.3,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # W3
                line = Segment(point_dict["Z4"], point_dict["Z6"] * np.exp(-1j * sp))
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
                    offset_label=1j * self.W0 * 0.4,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # H1[m]
                Zlim1 = (
                    point_dict["Z2"].real
                    + 1j * point_dict["Z3"].imag
                    - 1j * 0.3 * self.W3
                )
                Zlim2 = point_dict["Z3"] - 1j * 0.3 * self.W3
                plot_quote(
                    point_dict["Z2"],
                    Zlim1,
                    Zlim2,
                    point_dict["Z3"],
                    offset_label=-1j * 0.45 * self.W3,
                    fig=fig,
                    ax=ax,
                    label="H1[m]",
                )
                # H1 [rad]
                line = Arc1(
                    begin=(point_dict["Z2"] + point_dict["Z3"]) / 2
                    - self.get_H1() / 2
                    - 0.007j,
                    end=(((point_dict["Z2"] + point_dict["Z3"]) / 2) + point_dict["Z3"])
                    / 2,
                    radius=(self.get_H1() / 2),
                    is_trigo_direction=True,
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="H1 [rad]",
                    offset_label=-1j * sign * self.get_H1() * 0.5 - 3 * self.get_H1(),
                    fontsize=SC_FONT_SIZE,
                )
                # H3
                line = Segment(
                    (point_dict["Z4"] * np.exp(1j * sp) + point_dict["Z6"]) / 2,
                    (point_dict["Z3"] * np.exp(1j * sp) + point_dict["Z7"]) / 2,
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="H3",
                    offset_label=1j * self.W0 * 0.4,
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
                    begin=Rbo * np.exp(-1j * np.pi / 2 * 0.9),
                    end=Rbo * np.exp(1j * np.pi / 2 * 0.9),
                    radius=Rbo,
                    is_trigo_direction=True,
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # Tooth height
                line = Segment(point_dict["Z4"] * np.exp(1j * sp), point_dict["Z6"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                line = Segment(point_dict["Z3"] * np.exp(1j * sp), point_dict["Z7"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # Isthmus
                line = Segment(point_dict["Z2"], point_dict["Z8"])
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
                    enforced_default_color=self.MAGNET_COLOR,
                )

            # Zooming and cleaning
            W = (point_dict["Z6"] * np.exp(1j * hsp)).imag
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
        H1=0,
        H3=0.0122,
        wedge_type=0,
        W3=0.0122,
        H1_is_rad=False,
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
            if "H1" in list(init_dict.keys()):
                H1 = init_dict["H1"]
            if "H3" in list(init_dict.keys()):
                H3 = init_dict["H3"]
            if "wedge_type" in list(init_dict.keys()):
                wedge_type = init_dict["wedge_type"]
            if "W3" in list(init_dict.keys()):
                W3 = init_dict["W3"]
            if "H1_is_rad" in list(init_dict.keys()):
                H1_is_rad = init_dict["H1_is_rad"]
            if "Zs" in list(init_dict.keys()):
                Zs = init_dict["Zs"]
            if "wedge_mat" in list(init_dict.keys()):
                wedge_mat = init_dict["wedge_mat"]
            if "is_bore" in list(init_dict.keys()):
                is_bore = init_dict["is_bore"]
        # Set the properties (value check and convertion are done in setter)
        self.W0 = W0
        self.H0 = H0
        self.H1 = H1
        self.H3 = H3
        self.wedge_type = wedge_type
        self.W3 = W3
        self.H1_is_rad = H1_is_rad
        # Call Slot init
        super(SlotW14, self).__init__(Zs=Zs, wedge_mat=wedge_mat, is_bore=is_bore)
        # The class is frozen (in Slot init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        SlotW14_str = ""
        # Get the properties inherited from Slot
        SlotW14_str += super(SlotW14, self).__str__()
        SlotW14_str += "W0 = " + str(self.W0) + linesep
        SlotW14_str += "H0 = " + str(self.H0) + linesep
        SlotW14_str += "H1 = " + str(self.H1) + linesep
        SlotW14_str += "H3 = " + str(self.H3) + linesep
        SlotW14_str += "wedge_type = " + str(self.wedge_type) + linesep
        SlotW14_str += "W3 = " + str(self.W3) + linesep
        SlotW14_str += "H1_is_rad = " + str(self.H1_is_rad) + linesep
        return SlotW14_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from Slot
        if not super(SlotW14, self).__eq__(other):
            return False
        if other.W0 != self.W0:
            return False
        if other.H0 != self.H0:
            return False
        if other.H1 != self.H1:
            return False
        if other.H3 != self.H3:
            return False
        if other.wedge_type != self.wedge_type:
            return False
        if other.W3 != self.W3:
            return False
        if other.H1_is_rad != self.H1_is_rad:
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
            super(SlotW14, self).compare(
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
        if other._wedge_type != self._wedge_type:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._wedge_type)
                    + ", other="
                    + str(other._wedge_type)
                    + ")"
                )
                diff_list.append(name + ".wedge_type" + val_str)
            else:
                diff_list.append(name + ".wedge_type")
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
        if other._H1_is_rad != self._H1_is_rad:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._H1_is_rad)
                    + ", other="
                    + str(other._H1_is_rad)
                    + ")"
                )
                diff_list.append(name + ".H1_is_rad" + val_str)
            else:
                diff_list.append(name + ".H1_is_rad")
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from Slot
        S += super(SlotW14, self).__sizeof__()
        S += getsizeof(self.W0)
        S += getsizeof(self.H0)
        S += getsizeof(self.H1)
        S += getsizeof(self.H3)
        S += getsizeof(self.wedge_type)
        S += getsizeof(self.W3)
        S += getsizeof(self.H1_is_rad)
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
        SlotW14_dict = super(SlotW14, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs,
        )
        SlotW14_dict["W0"] = self.W0
        SlotW14_dict["H0"] = self.H0
        SlotW14_dict["H1"] = self.H1
        SlotW14_dict["H3"] = self.H3
        SlotW14_dict["wedge_type"] = self.wedge_type
        SlotW14_dict["W3"] = self.W3
        SlotW14_dict["H1_is_rad"] = self.H1_is_rad
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        SlotW14_dict["__class__"] = "SlotW14"
        return SlotW14_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        W0_val = self.W0
        H0_val = self.H0
        H1_val = self.H1
        H3_val = self.H3
        wedge_type_val = self.wedge_type
        W3_val = self.W3
        H1_is_rad_val = self.H1_is_rad
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
            H1=H1_val,
            H3=H3_val,
            wedge_type=wedge_type_val,
            W3=W3_val,
            H1_is_rad=H1_is_rad_val,
            Zs=Zs_val,
            wedge_mat=wedge_mat_val,
            is_bore=is_bore_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.W0 = None
        self.H0 = None
        self.H1 = None
        self.H3 = None
        self.wedge_type = None
        self.W3 = None
        self.H1_is_rad = None
        # Set to None the properties inherited from Slot
        super(SlotW14, self)._set_None()

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
        doc="""height or angle (See Schematics)

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

    def _get_wedge_type(self):
        """getter of wedge_type"""
        return self._wedge_type

    def _set_wedge_type(self, value):
        """setter of wedge_type"""
        check_var("wedge_type", value, "int", Vmin=0)
        self._wedge_type = value

    wedge_type = property(
        fget=_get_wedge_type,
        fset=_set_wedge_type,
        doc="""selection type wedge

        :Type: int
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

    def _get_H1_is_rad(self):
        """getter of H1_is_rad"""
        return self._H1_is_rad

    def _set_H1_is_rad(self, value):
        """setter of H1_is_rad"""
        check_var("H1_is_rad", value, "bool")
        self._H1_is_rad = value

    H1_is_rad = property(
        fget=_get_H1_is_rad,
        fset=_set_H1_is_rad,
        doc="""H1 unit, 0 for m, 1 for rad

        :Type: bool
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

    class S14_Rbo0CheckError(SlotCheckError):
        """ """

        pass

    class S14_Rbo1CheckError(SlotCheckError):
        """ """

        pass


MachineCheckError = SlotW14.MachineCheckError

LaminationCheckError = SlotW14.LaminationCheckError

SlotCheckError = SlotW14.SlotCheckError

S14_Rbo0CheckError = SlotW14.S14_Rbo0CheckError

S14_Rbo1CheckError = SlotW14.S14_Rbo1CheckError
