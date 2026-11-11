# Experimental dataclass generated from Generator/ClassesRef/Slot/SlotW13.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass
from typing import ClassVar

import matplotlib.pyplot as plt
import numpy as np

from ..definitions import config_dict
from ..Functions_new.labels import DRAW_PROP_LAB, SOP_LAB, WIND_LAB
from ..Functions_new.Plot import (
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
from ._error import ParentMissingError, SlotCheckError
from .arc_1 import Arc1
from .lam_slot import LamSlot
from .segment import Segment
from .slot import Slot
from .surf_line import SurfLine


@dataclass(eq=False)
class SlotW13(Slot):
    """Open Rectangular or trapezoidal slot with wedge

    Attributes
    ----------
    W0 : float
        Slot isthmus width.
        Unit: m; Default: 0.0122; Minimum: 0
    H0 : float
        Slot isthmus height.
        Unit: m; Default: 0.001; Minimum: 0
    H1 : float
        Slot wedge radial height or wedge angle .
        Unit: m/rad; Default: 0.0015; Minimum: 0
    W1 : float
        Slot wedge width.
        Unit: m; Default: 0.014; Minimum: 0
    H2 : float
        Slot height below wedge
        Unit: m; Default: 0.0325; Minimum: 0
    W2 : float
        Slot width below wedge
        Unit: m; Default: 0.0122; Minimum: 0
    W3 : float
        Slot bottom width.
        Unit: m; Default: 0.0122; Minimum: 0
    H1_is_rad : bool
        H1 unit, False for m, True for rad
        Default: False
    """

    IS_SYMMETRICAL: ClassVar = 1
    MAGNET_COLOR = config_dict["PLOT"]["COLOR_DICT"]["MAGNET_COLOR"]
    W0: float = 0.0122
    """Slot isthmus width."""
    H0: float = 0.001
    """Slot isthmus height."""
    H1: float = 0.0015
    """Slot wedge radial height or wedge angle ."""
    W1: float = 0.014
    """Slot wedge width."""
    H2: float = 0.0325
    """Slot height below wedge """
    W2: float = 0.0122
    """Slot width below wedge """
    W3: float = 0.0122
    """Slot bottom width."""
    H1_is_rad: bool = False
    """H1 unit, False for m, True for rad"""

    # Inlined from Methods.Slot.SlotW13._comp_line_dict
    def _comp_line_dict(self):
        """Define a dictionnary of the lines to draw the slot
        If a line has begin==end, it is replaced by "None" (dict has always the same number of keys)

        Parameters
        ----------
        self : SlotW13
            A SlotW13 object

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

        # Creation of curve
        line_dict = {}
        if self.H0 > 0:
            line_dict["1-2"] = Segment(begin=Z1, end=Z2)
        else:
            line_dict["1-2"] = None

        if self.H1 > 0 and self.W1 > self.W0:
            line_dict["2-3"] = Segment(begin=Z2, end=Z3)
        else:
            line_dict["2-3"] = None

        if self.W1 > self.W2:
            line_dict["3-4"] = Segment(begin=Z3, end=Z4)
        else:
            line_dict["3-4"] = None

        line_dict["4-5"] = Segment(begin=Z4, end=Z5)

        if self.W2 > 0:
            line_dict["5-6"] = Segment(begin=Z5, end=Z6)
        else:
            line_dict["5-6"] = None

        line_dict["6-7"] = Segment(begin=Z6, end=Z7)

        if self.W1 > self.W2:
            line_dict["7-8"] = Segment(begin=Z7, end=Z8)
        else:
            line_dict["7-8"] = None

        if self.H1 > 0 and self.W1 > self.W0:
            line_dict["8-9"] = Segment(begin=Z8, end=Z9)
        else:
            line_dict["8-9"] = None

        if self.H0 > 0:
            line_dict["9-10"] = Segment(begin=Z9, end=Z10)
        else:
            line_dict["9-10"] = None

        # Closing Arc (Rbo)
        line_dict["10-1"] = Arc1(
            begin=Z10, end=Z1, radius=-self.get_Rbo(), is_trigo_direction=False
        )

        # Closing Active part
        line_dict["4-7"] = Segment(begin=Z4, end=Z7)
        line_dict["7-4"] = Segment(begin=Z7, end=Z4)
        return line_dict

    # Inlined from Methods.Slot.SlotW13._comp_point_coordinate
    def _comp_point_coordinate(self):
        """Compute the point coordinates needed to plot the Slot.

        Parameters
        ----------
        self : SlotW13
            A SlotW13 object

        Returns
        -------
        point_dict: dict
            A dict of the slot coordinates
        """
        Rbo = self.get_Rbo()

        H1 = self.get_H1()

        # alpha is the angle to rotate Z0 so ||Z1,Z10|| = W0
        alpha = float(np.arcsin(self.W0 / (2 * Rbo)))

        # comp point coordinate (in complex)
        Z0 = Rbo * np.exp(1j * 0)
        Z1 = Z0 * np.exp(-1j * alpha)

        if self.is_outwards():
            Z2 = Z1 + self.H0
            Z3 = Z2 + H1 - (self.W1 - self.W0) * 1j / 2.0
            Z4 = Z3 + (self.W1 - self.W2) / 2.0 * 1j
            Z5 = Z4 + self.H2 - (self.W3 - self.W2) / 2.0 * 1j
        else:  # inward slot
            Z2 = Z1 - self.H0
            Z3 = Z2 - H1 - (self.W1 - self.W0) * 1j / 2.0
            Z4 = Z3 + (self.W1 - self.W2) / 2.0 * 1j
            Z5 = Z4 - self.H2 - (self.W3 - self.W2) / 2.0 * 1j

        point_dict = {}
        # symetry
        point_dict["Z1"] = Z1
        point_dict["Z2"] = Z2
        point_dict["Z3"] = Z3
        point_dict["Z4"] = Z4
        point_dict["Z5"] = Z5
        point_dict["Z6"] = Z5.conjugate()
        point_dict["Z7"] = Z4.conjugate()
        point_dict["Z8"] = Z3.conjugate()
        point_dict["Z9"] = Z2.conjugate()
        point_dict["Z10"] = Z1.conjugate()
        return point_dict

    # Inlined from Methods.Slot.SlotW13.build_geometry
    def build_geometry(self):
        """Compute the curve (Line) needed to plot the Slot.
        The ending point of a curve is the starting point of the next curve in
        the list

        Parameters
        ----------
        self : SlotW13
            A SlotW13 object

        Returns
        -------
        curve_list: list
            A list of 9 Segment

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
            line_dict["9-10"],
        ]
        return [line for line in curve_list if line is not None]

    # Inlined from Methods.Slot.SlotW13.build_geometry_active
    def build_geometry_active(self, Nrad, Ntan, alpha=0, delta=0):
        """Split the slot winding area in several zone

        Parameters
        ----------
        self : SlotW13
            A SlotW13 object
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

        point_dict = self._comp_point_coordinate()
        Z4 = point_dict["Z4"]
        Z5 = point_dict["Z5"]
        Z6 = point_dict["Z6"]
        Z7 = point_dict["Z7"]

        X = np.linspace(Z4, Z5, Nrad + 1)
        # Nrad+1 and Ntan+1 because 3 points => 2 zones
        Z = np.zeros((Nrad + 1, Ntan + 1), dtype=complex)
        for ii in range(Nrad + 1):
            Z[ii][:] = np.linspace(X[ii], X[ii].conjugate(), Ntan + 1)

        assert Z[0][0] == Z4
        assert Z[Nrad][0] == Z5
        assert Z[0][Ntan] == Z7
        assert Z[Nrad][Ntan] == Z6

        # We go thought the surface by Rad then Tan, starting by (0,0)
        surf_list = []
        for jj in range(Ntan):  # jj from 0 to Ntan-1
            for ii in range(Nrad):  # ii from 0 to Nrad-1
                point_ref = (
                    Z[ii][jj] + Z[ii][jj + 1] + Z[ii + 1][jj + 1] + Z[ii + 1][jj]
                ) / 4  # tre reference point of the surface
                # With one zone the order would be [Z7,Z4,Z5,Z6]
                curve_list = []
                curve_list.append(Segment(begin=Z[ii][jj], end=Z[ii][jj + 1]))
                curve_list.append(
                    Segment(
                        begin=Z[ii][jj + 1],
                        end=Z[ii + 1][jj + 1],
                        prop_dict={DRAW_PROP_LAB: False},
                    )
                )
                curve_list.append(
                    Segment(
                        begin=Z[ii + 1][jj + 1],
                        end=Z[ii + 1][jj],
                        prop_dict={DRAW_PROP_LAB: False},
                    )
                )
                curve_list.append(
                    Segment(
                        begin=Z[ii + 1][jj],
                        end=Z[ii][jj],
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
                )  # surface in the winding area
                surf_list.append(surface)

        for surf in surf_list:
            surf.rotate(alpha)  # rotation of each surface
            surf.translate(delta)  # translation of each surface

        return surf_list

    # Inlined from Methods.Slot.SlotW13.check
    def check(self):
        """Check that the SlotW13 object is correct

        Parameters
        ----------
        self : SlotW13
            A SlotW13 object

        Returns
        -------
        None

        Raises
        -------
        S13_W01CheckError
            You must have W0 <= W1
        S13_W12CheckError
            You must have W2 <= W1
        S13_H1rCheckError
            With H1 in radian, you must have H1 < pi/2
        """
        if self.W1 < self.W0:
            raise self.S13_W01CheckError("You must have W0 <= W1")

        if self.W1 < self.W2:
            raise self.S13_W12CheckError("You must have W2 <= W1")

        if self.H1_is_rad and self.H1 >= np.pi / 2:
            raise self.S13_H1rCheckError("With H1 in radian, you must have H1 < pi/2")

    # Inlined from Methods.Slot.SlotW13.comp_angle_opening
    def comp_angle_opening(self):
        """Compute the average opening angle of the Slot

        Parameters
        ----------
        self : SlotW13
            A SlotW13 object

        Returns
        -------
        alpha: float
            Average opening angle of the slot [rad]

        """

        Rbo = self.get_Rbo()

        return float(2 * np.arcsin(self.W0 / (2 * Rbo)))

    # Inlined from Methods.Slot.SlotW13.comp_height
    def comp_height(self):
        """Compute the height of the Slot.
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotW13
            A SlotW13 object

        Returns
        -------
        Htot: Height of the slot [m]

        """

        Rbo = self.get_Rbo()

        H1 = self.get_H1()

        # Computation of the arc height
        alpha = self.comp_angle_opening() / 2
        Harc = float(Rbo * (1 - np.cos(alpha)))

        if self.is_outwards():
            return abs(Rbo - Harc + self.H0 + H1 + self.H2 + 1j * self.W3 / 2.0) - Rbo
        else:
            return self.H0 + H1 + self.H2 + Harc

    # Inlined from Methods.Slot.SlotW13.comp_height_active
    def comp_height_active(self):
        """Compute the height of the winding area

        Parameters
        ----------
        self : SlotW13
            A SlotW13 object

        Returns
        -------
        Hwind: float
            Height of the winding area [m]

        """

        return self.H2

    # Inlined from Methods.Slot.SlotW13.comp_surface
    def comp_surface(self):
        """Compute the Slot total surface (by analytical computation).
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotW13
            A SlotW13 object

        Returns
        -------
        S: float
            Slot total surface [m**2]

        """
        return self.comp_surface_active() + self.comp_surface_opening()

    # Inlined from Methods.Slot.SlotW13.comp_surface_active
    def comp_surface_active(self):
        """Compute the Slot inner surface for winding (by analytical computation)

        Parameters
        ----------
        self : SlotW13
            A SlotW13 object

        Returns
        -------
        Swind: float
            Slot inner surface for winding [m**2]

        """

        return 0.5 * (self.W2 + self.W3) * self.H2

    # Inlined from Methods.Slot.SlotW13.comp_surface_opening
    def comp_surface_opening(self):
        """Compute the Slot opening surface (by analytical computation).
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotW13
            A SlotW13 object

        Returns
        -------
        S: float
            Slot opening surface [m**2]

        """

        Rbo = self.get_Rbo()

        S1 = self.H0 * self.W0
        H1 = self.get_H1()
        S2 = 0.5 * (self.W0 + self.W1) * H1

        # The bottom is an arc
        alpha = self.comp_angle_opening()
        Sarc = (Rbo**2.0) / 2.0 * (alpha - np.sin(alpha))

        # Because Slamination = S - Zs * Sslot
        if self.is_outwards():
            return S1 + S2 - Sarc
        else:
            return S1 + S2 + Sarc

    # Inlined from Methods.Slot.SlotW13.get_H1
    def get_H1(self):
        """Return H1 in [m]

        Parameters
        ----------
        self : SlotW13
            A SlotW13 object

        Returns
        -------
        H1: float
            H1 in [m]

        """

        if self.H1_is_rad:  # H1 in rad
            return ((self.W1 - self.W0) / 2.0) * np.tan(self.H1)  # convertion to m
        else:  # H1 in m
            return self.H1

    # Inlined from Methods.Slot.SlotW13.get_surface_active
    def get_surface_active(self, alpha=0, delta=0):
        """Return the full winding surface

        Parameters
        ----------
        self : SlotW13
            A SlotW13 object
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
            line_dict["4-5"],
            line_dict["5-6"],
            line_dict["6-7"],
            line_dict["7-4"],
        ]
        curve_list = [line for line in curve_list if line is not None]

        # Only the closing arc (7-4) needs to be drawn (in FEMM)
        for curve in curve_list[:-1]:
            if curve.prop_dict is None:
                curve.prop_dict = {}
            curve.prop_dict.update({DRAW_PROP_LAB: False})

        # Create surface
        H1 = self.get_H1()
        if self.is_outwards():
            Zmid = self.get_Rbo() + self.H0 + H1 + self.H2 / 2
        else:
            Zmid = self.get_Rbo() - self.H0 - H1 - self.H2 / 2
        label = self.parent.get_label() + "_" + WIND_LAB + "_R0-T0-S0"
        surface = SurfLine(line_list=curve_list, label=label, point_ref=Zmid)

        # Apply transformation
        surface.rotate(alpha)
        surface.translate(delta)

        return surface

    # Inlined from Methods.Slot.SlotW13.get_surface_opening
    def get_surface_opening(self, alpha=0, delta=0):
        """Return the list of surfaces defining the opening area of the Slot

        Parameters
        ----------
        self : SlotW13
            A SlotW13 object
        alpha : float
            float number for rotation (Default value = 0) [rad]
        delta : complex
            complex number for translation (Default value = 0)

        Returns
        -------
        surf_list : list
            list of surfaces objects
        """

        # H0=H1=0 no opening
        H1 = self.get_H1()
        if self.H0 == 0 and H1 == 0:
            return []

        # Create curve list
        line_dict = self._comp_line_dict()
        curve_list = [
            line_dict["1-2"],
            line_dict["2-3"],
            line_dict["3-4"],
            line_dict["4-7"],
            line_dict["7-8"],
            line_dict["8-9"],
            line_dict["9-10"],
            line_dict["10-1"],
        ]
        curve_list = [line for line in curve_list if line is not None]

        # Only the closing arc (10-1) needs to be drawn (in FEMM)
        for curve in curve_list[:-1]:
            if curve.prop_dict is None:
                curve.prop_dict = {}
            curve.prop_dict.update({DRAW_PROP_LAB: False})

        # Create surface
        if self.is_outwards():
            Zmid = self.get_Rbo() + (self.H0 + H1) / 2
        else:
            Zmid = self.get_Rbo() - (self.H0 + H1) / 2
        label = self.parent.get_label() + "_" + SOP_LAB + "_R0-T0-S0"
        surface = SurfLine(line_list=curve_list, label=label, point_ref=Zmid)

        # Apply transformation
        surface.rotate(alpha)
        surface.translate(delta)

        return [surface]

    # Inlined from Methods.Slot.SlotW13.plot_schematics
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
        self : SlotW13
            A SlotW13 object
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
                Zs=8,
                H0=10e-3,
                W0=20e-3,
                H1=10e-3,
                H2=40e-3,
                W1=40e-3,
                W2=10e-3,
                W3=30e-3,
            )
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
                line = Segment(begin=point_dict["Z1"], end=point_dict["Z10"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="W0",
                    offset_label=self.H0 * 0.1 + 1j * self.W0 * 0.1,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # W1
                Zlim1 = point_dict["Z2"].real + 1j * point_dict["Z3"].imag
                Zlim2 = point_dict["Z9"].real + 1j * point_dict["Z8"].imag
                plot_quote(
                    point_dict["Z3"],
                    Zlim1,
                    Zlim2,
                    point_dict["Z8"],
                    offset_label=self.get_H1() * 0.1 + 1j * self.W0 * 0.1,
                    fig=fig,
                    ax=ax,
                    label="W1",
                )
                # W2
                line = Segment(begin=point_dict["Z4"], end=point_dict["Z7"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="W2",
                    offset_label=self.H0 * 0.2 + 1j * self.W0 * 0.1,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # W3
                Zlim1 = point_dict["Z5"] + sign * 0.1 * self.H2
                Zlim2 = point_dict["Z6"] + sign * 0.1 * self.H2
                plot_quote(
                    point_dict["Z5"],
                    Zlim1,
                    Zlim2,
                    point_dict["Z6"],
                    offset_label=sign * 0.05 * self.H2,
                    fig=fig,
                    ax=ax,
                    label="W3",
                )
                # H0
                line = Segment(begin=point_dict["Z10"], end=point_dict["Z9"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    label="H0",
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    offset_label=1j * self.W0 * 0.1,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # H1
                line = Segment(
                    begin=point_dict["Z9"],
                    end=point_dict["Z7"].real + 1j * point_dict["Z9"].imag,
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    label="H1",
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    offset_label=1j * self.W0 * 0.1,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # H2
                line = Segment(begin=point_dict["Z6"].real, end=point_dict["Z7"].real)
                line.plot(
                    fig=fig,
                    ax=ax,
                    label="H2",
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    offset_label=1j * self.W0 * 0.1,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )

            if is_add_main_line:
                # Ox axis
                line = Segment(begin=0, end=lam.Rext * 1.5)
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
                    end=point_dict["Z10"],
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
            W = (
                max(
                    point_dict["Z8"].imag, point_dict["Z6"].imag, point_dict["Z10"].imag
                )
                * 1.1
            )
            Rint = min(point_dict["Z6"].real, point_dict["Z1"].real)
            Rext = max(point_dict["Z6"].real, point_dict["Z1"].real)

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

    class S13_H1rCheckError(SlotCheckError):
        """ """

    class S13_W01CheckError(SlotCheckError):
        """ """

    class S13_W12CheckError(SlotCheckError):
        """ """
