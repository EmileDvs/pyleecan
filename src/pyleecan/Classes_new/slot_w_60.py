# Experimental dataclass generated from Generator/ClassesRef/Slot/SlotW60.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass
from typing import ClassVar

import matplotlib.pyplot as plt
import numpy as np

from . import ParentMissingError
from ..definitions import config_dict
from ..Functions.labels import DRAW_PROP_LAB, SOP_LAB, WIND_LAB
from ..Functions.Plot import (
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
from .arc_1 import Arc1
from .lam_slot import LamSlot
from .segment import Segment
from .slot import Slot
from .surf_line import SurfLine


@dataclass(eq=False)
class SlotW60(Slot):
    """SlotW60

    Attributes
    ----------
    W1 : float
        Pole top width
        Unit: m; Default: 0.02; Minimum: 0
    W2 : float
        Pole bottom width
        Unit: m; Default: 0.03; Minimum: 0
    H1 : float
        Pole top height
        Unit: m; Default: 0.05; Minimum: 0
    H2 : float
        Pole bottom height
        Unit: m; Default: 0.15; Minimum: 0
    R1 : float
        Pole top radius
        Unit: m; Default: 0.03; Minimum: 0
    H3 : float
        Top Distance Ploe-coil
        Unit: m; Default: 0; Minimum: 0
    H4 : float
        Bottom Distance Ploe-coil
        Unit: m; Default: 0; Minimum: 0
    W3 : float
        Edge Distance Ploe-coil
        Unit: m; Default: 0; Minimum: 0
    """

    IS_SYMMETRICAL: ClassVar = 0
    MAGNET_COLOR = config_dict["PLOT"]["COLOR_DICT"]["MAGNET_COLOR"]
    W1: float = 0.02
    """Pole top width"""
    W2: float = 0.03
    """Pole bottom width"""
    H1: float = 0.05
    """Pole top height"""
    H2: float = 0.15
    """Pole bottom height"""
    R1: float = 0.03
    """Pole top radius"""
    H3: float = 0
    """Top Distance Ploe-coil """
    H4: float = 0
    """Bottom Distance Ploe-coil """
    W3: float = 0
    """Edge Distance Ploe-coil """

    # Inlined from Methods.Slot.SlotW60._comp_line_dict
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
        line_dict = {}
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

    # Inlined from Methods.Slot.SlotW60._comp_point_coordinate
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

        point_dict = {}
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

    # Inlined from Methods.Slot.SlotW60.build_geometry
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

    # Inlined from Methods.Slot.SlotW60.build_geometry_active
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

        surf_list = []
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

    # Inlined from Methods.Slot.SlotW60.check
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

    # Inlined from Methods.Slot.SlotW60.comp_angle_opening
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

    # Inlined from Methods.Slot.SlotW60.comp_height
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

    # Inlined from Methods.Slot.SlotW60.comp_height_active
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

    # Inlined from Methods.Slot.SlotW60.comp_surface
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

    # Inlined from Methods.Slot.SlotW60.comp_surface_active
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

    # Inlined from Methods.Slot.SlotW60.get_surface_active
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

    # Inlined from Methods.Slot.SlotW60.get_surface_opening
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
                curve.prop_dict = {}
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

    # Inlined from Methods.Slot.SlotW60.plot_schematics
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
            point_dict = {}
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

    class MachineCheckError(Exception):
        """ """

    class LaminationCheckError(MachineCheckError):
        """ """

    class SlotCheckError(LaminationCheckError):
        """ """

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

    class S60_W21CheckError(SlotCheckError):
        """ """

    class S60_WindWError(SlotCheckError):
        """ """

    class S60_WindHError(SlotCheckError):
        """ """

    class S60_InnerCheckError(SlotCheckError):
        """ """

    class S60_RCheckError(SlotCheckError):
        """ """


MachineCheckError = SlotW60.MachineCheckError
LaminationCheckError = SlotW60.LaminationCheckError
SlotCheckError = SlotW60.SlotCheckError
S60_WindError = SlotW60.S60_WindError
S60_W21CheckError = SlotW60.S60_W21CheckError
S60_WindWError = SlotW60.S60_WindWError
S60_WindHError = SlotW60.S60_WindHError
S60_InnerCheckError = SlotW60.S60_InnerCheckError
S60_RCheckError = SlotW60.S60_RCheckError
