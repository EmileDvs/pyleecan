# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Slot/SlotW60.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Slot/SlotW60
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
from pyleecan.Classes.Segment import Segment
from pyleecan.Classes.Arc1 import Arc1
import numpy as np, matplotlib.pyplot as plt
from pyleecan.Classes.SurfLine import SurfLine
from pyleecan.Functions.labels import WIND_LAB, SOP_LAB, DRAW_PROP_LAB
from pyleecan.Classes.LamSlot import LamSlot
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
    plot_quote,
)
from pyleecan.Classes import ParentMissingError


from pyleecan.Classes._check import InitUnKnowClassError


class SlotW60(Slot):

    VERSION = 1
    IS_SYMMETRICAL = 0
    MAGNET_COLOR = config_dict["PLOT"]["COLOR_DICT"]["MAGNET_COLOR"]

    # cf Methods.Slot.SlotW60._comp_line_dict
    def _comp_line_dict(self):
        """Define a dictionnary of the lines to draw the slot
        If a line has begin==end, it is replaced by "None" (dict has always the same number of keys)

        Parameters
        ----------
        self : SlotW60
            A SlotW60 object

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
        Z10 = point_dict["Z10"]
        Z11 = point_dict["Z11"]
        Zw1 = point_dict["Zw1"]
        Zw2 = point_dict["Zw2"]
        Zw3 = point_dict["Zw3"]
        Zw4 = point_dict["Zw4"]
        Zw1s = point_dict["Zw1s"]
        Zw2s = point_dict["Zw2s"]
        Zw3s = point_dict["Zw3s"]
        Zw4s = point_dict["Zw4s"]

        # Creation of curve
        line_dict = dict()
        line_dict["1-2"] = Arc1(Z1, Z2, self.R1)
        line_dict["2-3"] = Segment(Z2, Z3)
        line_dict["3-4"] = Segment(Z3, Z4)
        line_dict["4-5"] = Segment(Z4, Z5)
        line_dict["5-6"] = Segment(Z5, Z6)
        line_dict["6-7"] = Segment(Z6, Z7)
        line_dict["7-8"] = Segment(Z7, Z8)
        line_dict["8-9"] = Segment(Z8, Z9)
        line_dict["9-10"] = Segment(Z9, Z10)
        line_dict["10-11"] = Arc1(Z10, Z11, self.R1)
        line_dict["11-1"] = Arc1(Z11, Z1, -self.get_Rbo(), is_trigo_direction=False)
        # Winding lines
        line_dict["w3-w4"] = Segment(Zw3, Zw4)
        line_dict["w4-w1"] = Segment(Zw4, Zw1)
        line_dict["w1-w2"] = Segment(Zw1, Zw2)
        line_dict["w2-w3"] = Segment(Zw2, Zw3)

        line_dict["w3s-w4s"] = Segment(Zw3s, Zw4s)
        line_dict["w4s-w1s"] = Segment(Zw4s, Zw1s)
        line_dict["w1s-w2s"] = Segment(Zw1s, Zw2s)
        line_dict["w2s-w3s"] = Segment(Zw2s, Zw3s)
        # For opening surface (first winding)
        line_dict["4-w1"] = Segment(Z4, Zw1)
        line_dict["w2-5"] = Segment(Zw2, Z5)
        line_dict["3-w4"] = Segment(Z3, Zw4)
        line_dict["w3-6"] = Segment(Zw3, Z6)
        line_dict["w1-w4"] = Segment(Zw1, Zw4)
        line_dict["w4-w3"] = Segment(Zw4, Zw3)
        line_dict["w3-w2"] = Segment(Zw3, Zw2)
        # For opening surface (first winding)
        line_dict["7-w2s"] = Segment(Z7, Zw2s)
        line_dict["w1s-8"] = Segment(Zw1s, Z8)
        line_dict["6-w3s"] = Segment(Z6, Zw3s)
        line_dict["w4s-9"] = Segment(Zw4s, Z9)
        return line_dict

    # cf Methods.Slot.SlotW60._comp_point_coordinate
    def _comp_point_coordinate(self):
        """Compute the point coordinate needed to plot the Slot.

        Parameters
        ----------
        self : SlotW60
            A SlotW60 object

        Returns
        -------
        point_dict: dict
            A dict of the slot point coordinates

        """

        Rbo = self.get_Rbo()
        hsp = np.pi / self.Zs

        # Zxt => In the tooth ref (Ox as the sym axis of the tooth)
        Z1t = Rbo

        # Height of the arc (Z2t, Rbo-R1, Z2t.conjugate())
        alpha = np.arcsin(self.W1 / (2 * self.R1))
        Harc = float(self.R1 * (1 - np.cos(alpha)))

        Z2t = Rbo - Harc + 1j * self.W1 / 2
        Z3t = Z2t - self.H1
        Z4t = Z3t.real + 1j * self.W2 / 2
        Z5t = Z4t - self.H2
        Z6t = (Z5t.real / np.cos(hsp)) * np.exp(1j * hsp)

        # Go to the slot ref
        Z1 = Z1t * np.exp(-1j * hsp)
        Z2 = Z2t * np.exp(-1j * hsp)
        Z3 = Z3t * np.exp(-1j * hsp)
        Z4 = Z4t * np.exp(-1j * hsp)
        Z5 = Z5t * np.exp(-1j * hsp)
        Z6 = Z6t * np.exp(-1j * hsp)
        Z7 = Z5.conjugate()
        Z8 = Z4.conjugate()
        Z9 = Z3.conjugate()
        Z10 = Z2.conjugate()
        Z11 = Z1.conjugate()

        # Compute the point in the tooth ref
        Z4t = Z4 * np.exp(1j * hsp)
        Z5t = Z5 * np.exp(1j * hsp)
        Zw1t = Z4t - self.H3
        Zw2t = Z5t + self.H4
        Zw3t = Zw2t + 1j * ((self.W1 - self.W2) / 2 - self.W3)
        Zw4t = Zw1t + 1j * ((self.W1 - self.W2) / 2 - self.W3)

        # Go back to slot ref
        Zw1 = Zw1t * np.exp(1j * -hsp)
        Zw2 = Zw2t * np.exp(1j * -hsp)
        Zw3 = Zw3t * np.exp(1j * -hsp)
        Zw4 = Zw4t * np.exp(1j * -hsp)
        Zw1s = Zw1.conjugate()
        Zw2s = Zw2.conjugate()
        Zw3s = Zw3.conjugate()
        Zw4s = Zw4.conjugate()

        point_dict = dict()
        # symetry
        point_dict["Z1"] = Z1
        point_dict["Z2"] = Z2
        point_dict["Z3"] = Z3
        point_dict["Z4"] = Z4
        point_dict["Z5"] = Z5
        point_dict["Z6"] = Z6
        point_dict["Z7"] = Z7
        point_dict["Z8"] = Z8
        point_dict["Z9"] = Z9
        point_dict["Z10"] = Z10
        point_dict["Z11"] = Z11
        point_dict["Zc"] = (Rbo - self.R1) * np.exp(1j * (np.pi / self.Zs))
        point_dict["Zw5"] = (Z3t - self.H2) * np.exp(-1j * hsp)
        point_dict["Zw5s"] = point_dict["Zw5"].conjugate()
        point_dict["Zw1"] = Zw1
        point_dict["Zw2"] = Zw2
        point_dict["Zw3"] = Zw3
        point_dict["Zw4"] = Zw4
        point_dict["Zw1s"] = Zw1s
        point_dict["Zw2s"] = Zw2s
        point_dict["Zw3s"] = Zw3s
        point_dict["Zw4s"] = Zw4s

        return point_dict

    # cf Methods.Slot.SlotW60.build_geometry
    def build_geometry(self):
        """Compute the curve (Line) needed to plot the Slot.
        The ending point of a curve is the starting point of the next curve in
        the list

        Parameters
        ----------
        self : SlotW60
            A SlotW60 object

        Returns
        -------
        curve_list: list
            A list of 8 Segment and 2 Arc1

        """

        line_dict = self._comp_line_dict()

        # Creation of curve
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
            line_dict["10-11"],
        ]
        return [line for line in curve_list if line is not None]

    # cf Methods.Slot.SlotW60.build_geometry_active
    def build_geometry_active(self, Nrad, Ntan, is_simplified=False, alpha=0, delta=0):
        """Split the slot winding area in several zone

        Parameters
        ----------
        self : SlotW60
            A SlotW60 object
        Nrad : int
            Number of radial layer
        Ntan : int
            Number of tangentiel layer
        is_simplified : bool
            boolean to specify if the coincident lines are considered as one
             or different lines (Default value = False)
        alpha : float
            Angle for rotation (Default value = 0) [rad]
        delta : complex
            complex for translation (Default value = 0)

        Returns
        -------
        surf_list: list
            List of surface delimiting the winding zone

        Raises
        -------
        S60_WindError
            Slot 60 can use only for winding with Nrad=1 and Ntan=2

        """

        if Nrad != 1 or Ntan != 2:
            raise S60_WindError(
                "Slot 60 can use only for winding with Nrad=1 and Ntan=2"
            )
        self.check()

        # get the name of the lamination
        lam_label = self.parent.get_label()

        line_dict = self._comp_line_dict()

        Ref1 = (line_dict["w3-w4"].get_begin() + line_dict["w1-w2"].get_begin()) / 2
        Ref2 = (line_dict["w3s-w4s"].get_begin() + line_dict["w1s-w2s"].get_begin()) / 2

        # Create the surfaces
        wind1_lines = [
            line_dict["w3-w4"],
            line_dict["w4-w1"],
            line_dict["w1-w2"],
            line_dict["w2-w3"],
        ]

        wind2_lines = [
            line_dict["w3s-w4s"],
            line_dict["w4s-w1s"],
            line_dict["w1s-w2s"],
            line_dict["w2s-w3s"],
        ]

        surf_list = list()
        surf_list.append(
            SurfLine(
                line_list=wind1_lines,
                label=lam_label + "_" + WIND_LAB + "_R0-T0-S0",
                point_ref=Ref1,
            )
        )
        surf_list.append(
            SurfLine(
                line_list=wind2_lines,
                label=lam_label + "_" + WIND_LAB + "_R0-T1-S0",
                point_ref=Ref2,
            )
        )

        # Rotate and translate the surfaces
        for surf in surf_list:
            surf.rotate(alpha)
            surf.translate(delta)

        return surf_list

    # cf Methods.Slot.SlotW60.check
    def check(self):
        """Check that the SlotW60 object is correct

        Parameters
        ----------
        self : SlotW60
            A SlotW60 object

        Returns
        -------
        None

        Raises
        -------
        S60_InnerCheckError
           Slot 60 is for inner lamination only
        S60_W21CheckError
            You must have W2 < W1
        S60_RCheckError
            You must have R1 <= Rbo
        S60_WindHError
            You must have W3+W4 < H2
        S60_WindWError
            You must have W3 < (W1-W2)/2

        """

        if self.is_outwards():
            raise S60_InnerCheckError("Slot 60 is for inner lamination only")

        if self.W1 <= self.W2:
            raise S60_W21CheckError("You must have W2 < W1")

        if self.R1 > self.get_Rbo():
            raise S60_RCheckError("You must have R1 <= Rbo")

        if self.H3 + self.H4 >= self.H2:
            raise S60_WindHError("You must have W3+W4 < H2")

        if self.W3 >= (self.W1 - self.W2) / 2:
            raise S60_WindWError("You must have W3 < (W1-W2)/2")

    # cf Methods.Slot.SlotW60.comp_angle_opening
    def comp_angle_opening(self):
        """Compute the average opening angle of the Slot

        Parameters
        ----------
        self : SlotW60
            A SlotW60 object

        Returns
        -------
        alpha: float
            Average opening angle of the slot [rad]

        """

        return 2 * np.pi / self.Zs

    # cf Methods.Slot.SlotW60.comp_height
    def comp_height(self):
        """Compute the height of the Slot.
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotW60
            A SlotW60 object

        Returns
        -------
        Htot: float
            Height of the slot [m]

        """

        Rbo = self.get_Rbo()

        point_dict = self._comp_point_coordinate()
        Z5 = point_dict["Z5"]

        return Rbo - abs(Z5)

    # cf Methods.Slot.SlotW60.comp_height_active
    def comp_height_active(self):
        """Compute the height of the winding area

        Parameters
        ----------
        self : SlotW60
            A SlotW60 object

        Returns
        -------
        Hwind: float
            Height of the winding area [m]

        """

        point_dict = self._comp_point_coordinate()
        Z4 = point_dict["Z4"]
        Z5 = point_dict["Z5"]

        # Compute the point in the tooth ref
        hsp = np.pi / self.Zs
        Z4t = Z4 * np.exp(1j * hsp)
        Zw4t = Z4t - self.H3 + 1j * ((self.W1 - self.W2) / 2 - self.W3)

        return abs(Zw4t) - abs(Z5)

    # cf Methods.Slot.SlotW60.comp_surface
    def comp_surface(self):
        """Compute the Slot total surface (by analytical computation).
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotW60
            A SlotW60 object

        Returns
        -------
        S: float
            Slot total surface [m**2]

        """

        point_dict = self._comp_point_coordinate()
        Z5 = point_dict["Z5"]
        Z6 = point_dict["Z6"]
        Z7 = point_dict["Z7"]

        Rext = self.get_Rbo()
        Rint = abs(Z5)

        # Surface of a slot pitch
        Sring = (np.pi * Rext**2 - np.pi * Rint**2) * 1 / self.Zs

        # Surface of the isocele triangle Z5 Z6 Z7
        D75 = abs(Z7 - Z5)
        Zmid = (Z5 + Z7) / 2
        H = abs(Z6 - Zmid)
        Stri = H * D75 / 2

        # Tooth surface
        St = self.H1 * self.W1 + self.H2 * self.W2

        alpha_top = 2 * np.arcsin(self.W1 / (2 * self.R1))
        Sarc_top = (self.R1**2.0) / 2.0 * (alpha_top - np.sin(alpha_top))

        alpha_bot1 = 2 * np.arcsin(self.W2 / (2 * Rint))
        Sarc_bot1 = (Rint**2.0) / 2.0 * (alpha_bot1 - np.sin(alpha_bot1))

        alpha_bot2 = 2 * np.arcsin(D75 / (2 * Rint))
        Sarc_bot2 = (Rint**2.0) / 2.0 * (alpha_bot2 - np.sin(alpha_bot2))

        return Sring - (St + Sarc_top + Stri - Sarc_bot1 - Sarc_bot2)

    # cf Methods.Slot.SlotW60.comp_surface_active
    def comp_surface_active(self):
        """Compute the Slot inner surface for winding

        Parameters
        ----------
        self : SlotW60
            A SlotW60 object

        Returns
        -------
        Swind: float
            Slot inner surface for winding [m**2]

        """

        return 2 * (self.H2 - self.H3 - self.H4) * ((self.W1 - self.W2) / 2 - self.W3)

    # cf Methods.Slot.SlotW60.get_surface_active
    def get_surface_active(self, alpha=0, delta=0):
        """Return the full winding surface

        Parameters
        ----------
        self : SlotW60
            A SlotW60 object
        alpha : float
            float number for rotation (Default value = 0) [rad]
        delta : complex
            complex number for translation (Default value = 0)

        Returns
        -------
        surf_wind: Surface
            Surface corresponding to the Winding Area
        """

        raise Exception("get_surface_active not available for SlotW60")

    # cf Methods.Slot.SlotW60.get_surface_opening
    def get_surface_opening(self, alpha=0, delta=0):
        """Return the list of surfaces defining the opening area of the Slot

        Parameters
        ----------
        self : SlotW60
            A SlotW60 object
        alpha : float
            float number for rotation (Default value = 0) [rad]
        delta : complex
            complex number for translation (Default value = 0)

        Returns
        -------
        surf_list : list
            list of surfaces objects
        """

        # Create curve list
        line_dict = self._comp_line_dict()
        curve_list = [
            line_dict["1-2"],
            line_dict["2-3"],
        ]
        if self.H3 > 0:
            curve_list.extend([line_dict["3-4"], line_dict["4-w1"], line_dict["w1-w4"]])
        elif self.W3 > 0:
            curve_list.append(line_dict["3-w4"])
        curve_list.append(line_dict["w4-w3"])
        if self.H4 > 0:
            curve_list.extend([line_dict["w3-w2"], line_dict["w2-5"], line_dict["5-6"]])
        else:
            curve_list.append(line_dict["w3-6"])
        #  second winding
        if self.H4 > 0:
            curve_list.extend(
                [line_dict["6-7"], line_dict["7-w2s"], line_dict["w2s-w3s"]]
            )
        else:
            curve_list.append(line_dict["6-w3s"])
        curve_list.append(line_dict["w3s-w4s"])
        if self.H3 > 0:
            curve_list.extend(
                [line_dict["w4s-w1s"], line_dict["w1s-8"], line_dict["8-9"]]
            )
        elif self.W3 > 0:
            curve_list.append(line_dict["w4s-9"])
        curve_list.extend([line_dict["9-10"], line_dict["10-11"], line_dict["11-1"]])

        curve_list = [line for line in curve_list if line is not None]

        # Only the closing arc (11-1) needs to be drawn (in FEMM)
        for curve in curve_list[:-1]:
            if curve.prop_dict is None:
                curve.prop_dict = dict()
            curve.prop_dict.update({DRAW_PROP_LAB: False})

        # Create surface
        Z10 = line_dict["10-11"].get_begin()
        Z2 = line_dict["1-2"].get_end()
        Zmid = (Z10 + Z2) / 2
        label = self.parent.get_label() + "_" + SOP_LAB + "_R0-T0-S0"
        surface = SurfLine(line_list=curve_list, label=label, point_ref=Zmid)

        # Apply transformation
        if alpha != 0:
            surface.rotate(alpha)
        if delta != 0:
            surface.translate(delta)

        return [surface]

    # cf Methods.Slot.SlotW60.plot_schematics
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
        self : SlotW60
            A SlotW60 object
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
            slot = type(self)(
                Zs=12,
                H1=20e-3,
                H2=65e-3,
                W1=100e-3,
                W2=40e-3,
                R1=100e-3,
                W3=17e-3,
                H3=17e-3,
                H4=17e-3,
            )
            lam = LamSlot(
                Rint=0.135, Rext=0.3, is_internal=True, is_stator=False, slot=slot
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
                is_show_fig=False, fig=fig, ax=ax
            )  # center slot on Ox axis
            point_dict = dict()
            point_dict_temp = self._comp_point_coordinate()
            for key in point_dict_temp:
                point_dict[key] = point_dict_temp[key] * np.exp(
                    1j * (np.pi / self.Zs + 4 * np.pi / self.Zs)
                )
                point_dict[key + "d"] = point_dict[key] * np.exp(
                    1j * (2 * np.pi / self.Zs)
                )
                point_dict[key + "dd"] = point_dict[key + "d"] * np.exp(
                    1j * (2 * np.pi / self.Zs)
                )

            if self.is_outwards():
                sign = 1
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
                # W1
                line = Segment(
                    (point_dict["Z2d"] + point_dict["Z3d"]) / 2,
                    (point_dict["Z9"] + point_dict["Z10"]) / 2,
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    label="W1",
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    offset_label=0.9j * self.W1 * 0.1 - (0.007 + 0j),
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # H1
                Zlim1 = point_dict["Z2d"]
                Zlim2 = point_dict["Z3d"]
                plot_quote(
                    point_dict["Z2d"],
                    Zlim1 - (0.006 + 0j),
                    Zlim2 - (0.006 + 0j),
                    point_dict["Z3d"],
                    offset_label=self.H1 * -1.0 - 0.6j * self.W1 * 0.05,
                    fig=fig,
                    ax=ax,
                    label="H1",
                )
                # H2
                Zlim1 = point_dict["Z8"]
                Zlim2 = point_dict["Z7"]
                plot_quote(
                    point_dict["Z8"],
                    Zlim1 + (0.035 + 0j),
                    Zlim2 + (0.035 + 0j),
                    point_dict["Z7"],
                    offset_label=self.H1 * 0.3 + 2j * self.W1 * 0.05,
                    fig=fig,
                    ax=ax,
                    label="H2",
                )
                # W2
                line = Segment(
                    (point_dict["Z4d"] + point_dict["Z5d"]) / 2,
                    (point_dict["Z8"] + point_dict["Z7"]) / 2,
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    label="W2",
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    offset_label=-1.6j * self.W1 * 0.1 - (0.007 + 0j),
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # R1
                Zlim1 = point_dict["Z2dd"]
                Zlim2 = point_dict["Zcd"]
                plot_quote(
                    point_dict["Zcd"],
                    Zlim1,
                    Zlim2,
                    point_dict["Z10d"],
                    offset_label=0.009 * self.W1 + 0.010j,
                    fig=fig,
                    ax=ax,
                    label="R1",
                )

                # W5d
                Zlim1 = point_dict["Zw5d"]
                Zlim2 = point_dict["Zw5d"]
                plot_quote(
                    point_dict["Z3d"],
                    Zlim1,
                    Zlim2,
                    point_dict["Z5d"],
                    offset_label=0,
                    fig=fig,
                    ax=ax,
                    label=None,
                )
                # W5
                Zlim1 = point_dict["Zw5"]
                Zlim2 = point_dict["Zw5"]
                plot_quote(
                    point_dict["Z3"],
                    Zlim1,
                    Zlim2,
                    point_dict["Z5"],
                    offset_label=0,
                    fig=fig,
                    ax=ax,
                    label=None,
                )
                if type_add_active != 0:
                    # H3
                    line = Segment(
                        ((point_dict["Z3d"] + point_dict["Z4d"]) / 2) + (0.008 + 0j),
                        ((point_dict["Zw4d"] + point_dict["Zw1d"]) / 2),
                    )
                    line.plot(
                        fig=fig,
                        ax=ax,
                        label="H3",
                        color=ARROW_COLOR,
                        linewidth=ARROW_WIDTH,
                        offset_label=(-0.2j * self.W1 * 0.1) - (0.020 + 0j),
                        is_arrow=True,
                        fontsize=SC_FONT_SIZE,
                    )
                    # H4
                    line = Segment(
                        ((point_dict["Z5d"] + point_dict["Zw5d"]) / 2) + (0.008 + 0j),
                        ((point_dict["Zw2d"] + point_dict["Zw3d"]) / 2),
                    )
                    line.plot(
                        fig=fig,
                        ax=ax,
                        label="H4",
                        color=ARROW_COLOR,
                        linewidth=ARROW_WIDTH,
                        offset_label=(-0.2j * self.W1 * 0.1) - (0.020 + 0j),
                        is_arrow=True,
                        fontsize=SC_FONT_SIZE,
                    )
                    # W3
                    line = Segment(
                        ((point_dict["Zw5"] + point_dict["Z3"]) / 2),
                        ((point_dict["Zw4"] + point_dict["Zw3"]) / 2),
                    )
                    line.plot(
                        fig=fig,
                        ax=ax,
                        label="W3",
                        color=ARROW_COLOR,
                        linewidth=ARROW_WIDTH,
                        offset_label=(-1.8j * self.W1 * 0.1) - (0.007 + 0j),
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
                    begin=self.get_Rbo(),
                    end=-self.get_Rbo(),
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

            if type_add_active in [1, 3]:  # Wind and Wedge
                is_add_wedge = False  # No wedge for this false
                self.plot_active(
                    fig=fig,
                    ax=ax,
                    is_show_fig=False,
                    is_add_wedge=is_add_wedge,
                    wind_mat=np.ones((1, 2, self.Zs, 1)),
                    alpha=np.pi / self.Zs + 2 * np.pi / self.Zs,
                )
                self.plot_active(
                    fig=fig,
                    ax=ax,
                    is_show_fig=False,
                    is_add_wedge=is_add_wedge,
                    wind_mat=np.ones((1, 2, self.Zs, 1)),
                    alpha=np.pi / self.Zs + 4 * np.pi / self.Zs,
                )
                self.plot_active(
                    fig=fig,
                    ax=ax,
                    is_show_fig=False,
                    is_add_wedge=is_add_wedge,
                    wind_mat=np.ones((1, 2, self.Zs, 1)),
                    alpha=np.pi / self.Zs + 6 * np.pi / self.Zs,
                )
                self.plot_active(
                    fig=fig,
                    ax=ax,
                    is_show_fig=False,
                    is_add_wedge=is_add_wedge,
                    wind_mat=np.ones((1, 2, self.Zs, 1)),
                    alpha=np.pi / self.Zs + 8 * np.pi / self.Zs,
                )

            elif type_add_active == 2:  # Magnet
                self.plot_active(
                    fig=fig,
                    is_show_fig=False,
                    enforced_default_color=self.MAGNET_COLOR,
                )

            # Zooming and cleaning
            ax.axis("equal")
            ax.set_ylim(abs(point_dict["Z1"]) * 0.5, abs(point_dict["Z1"]) * 1.2)
            ax.set_xlim(self.W1 * -0.5, self.W1 * 0.5)
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
        W1=0.02,
        W2=0.03,
        H1=0.05,
        H2=0.15,
        R1=0.03,
        H3=0,
        H4=0,
        W3=0,
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
            if "W1" in list(init_dict.keys()):
                W1 = init_dict["W1"]
            if "W2" in list(init_dict.keys()):
                W2 = init_dict["W2"]
            if "H1" in list(init_dict.keys()):
                H1 = init_dict["H1"]
            if "H2" in list(init_dict.keys()):
                H2 = init_dict["H2"]
            if "R1" in list(init_dict.keys()):
                R1 = init_dict["R1"]
            if "H3" in list(init_dict.keys()):
                H3 = init_dict["H3"]
            if "H4" in list(init_dict.keys()):
                H4 = init_dict["H4"]
            if "W3" in list(init_dict.keys()):
                W3 = init_dict["W3"]
            if "Zs" in list(init_dict.keys()):
                Zs = init_dict["Zs"]
            if "wedge_mat" in list(init_dict.keys()):
                wedge_mat = init_dict["wedge_mat"]
            if "is_bore" in list(init_dict.keys()):
                is_bore = init_dict["is_bore"]
        # Set the properties (value check and convertion are done in setter)
        self.W1 = W1
        self.W2 = W2
        self.H1 = H1
        self.H2 = H2
        self.R1 = R1
        self.H3 = H3
        self.H4 = H4
        self.W3 = W3
        # Call Slot init
        super(SlotW60, self).__init__(Zs=Zs, wedge_mat=wedge_mat, is_bore=is_bore)
        # The class is frozen (in Slot init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        SlotW60_str = ""
        # Get the properties inherited from Slot
        SlotW60_str += super(SlotW60, self).__str__()
        SlotW60_str += "W1 = " + str(self.W1) + linesep
        SlotW60_str += "W2 = " + str(self.W2) + linesep
        SlotW60_str += "H1 = " + str(self.H1) + linesep
        SlotW60_str += "H2 = " + str(self.H2) + linesep
        SlotW60_str += "R1 = " + str(self.R1) + linesep
        SlotW60_str += "H3 = " + str(self.H3) + linesep
        SlotW60_str += "H4 = " + str(self.H4) + linesep
        SlotW60_str += "W3 = " + str(self.W3) + linesep
        return SlotW60_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from Slot
        if not super(SlotW60, self).__eq__(other):
            return False
        if other.W1 != self.W1:
            return False
        if other.W2 != self.W2:
            return False
        if other.H1 != self.H1:
            return False
        if other.H2 != self.H2:
            return False
        if other.R1 != self.R1:
            return False
        if other.H3 != self.H3:
            return False
        if other.H4 != self.H4:
            return False
        if other.W3 != self.W3:
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
            super(SlotW60, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
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
            other._W2 is not None
            and self._W2 is not None
            and np.isnan(other._W2)
            and np.isnan(self._W2)
        ):
            pass
        elif other._W2 != self._W2:
            if is_add_value:
                val_str = " (self=" + str(self._W2) + ", other=" + str(other._W2) + ")"
                diff_list.append(name + ".W2" + val_str)
            else:
                diff_list.append(name + ".W2")
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
            other._H2 is not None
            and self._H2 is not None
            and np.isnan(other._H2)
            and np.isnan(self._H2)
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
        if (
            other._H4 is not None
            and self._H4 is not None
            and np.isnan(other._H4)
            and np.isnan(self._H4)
        ):
            pass
        elif other._H4 != self._H4:
            if is_add_value:
                val_str = " (self=" + str(self._H4) + ", other=" + str(other._H4) + ")"
                diff_list.append(name + ".H4" + val_str)
            else:
                diff_list.append(name + ".H4")
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
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from Slot
        S += super(SlotW60, self).__sizeof__()
        S += getsizeof(self.W1)
        S += getsizeof(self.W2)
        S += getsizeof(self.H1)
        S += getsizeof(self.H2)
        S += getsizeof(self.R1)
        S += getsizeof(self.H3)
        S += getsizeof(self.H4)
        S += getsizeof(self.W3)
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
        SlotW60_dict = super(SlotW60, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        SlotW60_dict["W1"] = self.W1
        SlotW60_dict["W2"] = self.W2
        SlotW60_dict["H1"] = self.H1
        SlotW60_dict["H2"] = self.H2
        SlotW60_dict["R1"] = self.R1
        SlotW60_dict["H3"] = self.H3
        SlotW60_dict["H4"] = self.H4
        SlotW60_dict["W3"] = self.W3
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        SlotW60_dict["__class__"] = "SlotW60"
        return SlotW60_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        W1_val = self.W1
        W2_val = self.W2
        H1_val = self.H1
        H2_val = self.H2
        R1_val = self.R1
        H3_val = self.H3
        H4_val = self.H4
        W3_val = self.W3
        Zs_val = self.Zs
        if self.wedge_mat is None:
            wedge_mat_val = None
        else:
            wedge_mat_val = self.wedge_mat.copy()
        is_bore_val = self.is_bore
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(
            W1=W1_val,
            W2=W2_val,
            H1=H1_val,
            H2=H2_val,
            R1=R1_val,
            H3=H3_val,
            H4=H4_val,
            W3=W3_val,
            Zs=Zs_val,
            wedge_mat=wedge_mat_val,
            is_bore=is_bore_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.W1 = None
        self.W2 = None
        self.H1 = None
        self.H2 = None
        self.R1 = None
        self.H3 = None
        self.H4 = None
        self.W3 = None
        # Set to None the properties inherited from Slot
        super(SlotW60, self)._set_None()

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
        doc="""Pole top width

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
        doc="""Pole bottom width

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
        doc="""Pole top height

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
        doc="""Pole bottom height

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
        doc="""Pole top radius

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
        doc="""Top Distance Ploe-coil 

        :Type: float
        :min: 0
        """,
    )

    def _get_H4(self):
        """getter of H4"""
        return self._H4

    def _set_H4(self, value):
        """setter of H4"""
        check_var("H4", value, "float", Vmin=0)
        self._H4 = value

    H4 = property(
        fget=_get_H4,
        fset=_set_H4,
        doc="""Bottom Distance Ploe-coil 

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
        doc="""Edge Distance Ploe-coil 

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

    class S60_WindError(SlotCheckError):
        """

        Parameters
        ----------

        Returns
        -------

        Raises
        ------
        winding


        """

        pass

    class S60_WindWError(SlotCheckError):
        """ """

        pass

    class S60_W21CheckError(SlotCheckError):
        """ """

        pass

    class S60_RCheckError(SlotCheckError):
        """ """

        pass

    class S60_WindHError(SlotCheckError):
        """ """

        pass

    class S60_InnerCheckError(SlotCheckError):
        """ """

        pass


MachineCheckError = SlotW60.MachineCheckError

LaminationCheckError = SlotW60.LaminationCheckError

SlotCheckError = SlotW60.SlotCheckError

S60_WindError = SlotW60.S60_WindError

S60_WindWError = SlotW60.S60_WindWError

S60_W21CheckError = SlotW60.S60_W21CheckError

S60_RCheckError = SlotW60.S60_RCheckError

S60_WindHError = SlotW60.S60_WindHError

S60_InnerCheckError = SlotW60.S60_InnerCheckError
