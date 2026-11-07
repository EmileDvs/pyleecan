# Experimental dataclass generated from Generator/ClassesRef/Slot/SlotW22.csv
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
)
from .arc_1 import Arc1
from .arc_2 import Arc2
from .lam_slot import LamSlot
from .segment import Segment
from .slot import Slot
from .surf_line import SurfLine


@dataclass(eq=False)
class SlotW22(Slot):
    """semi-closed orthoradial without fillet without wedge

    Attributes
    ----------
    W0 : float
        Slot isthmus orthoradial angular width.
        Unit: rad; Default: 0.043633; Minimum: 0
    H0 : float
        Slot isthmus radial height.
        Unit: m; Default: 0.006; Minimum: 0
    H2 : float
        Slot radial height below wedge
        Unit: m; Default: 0.04; Minimum: 0
    W2 : float
        Angle between slot edges
        Unit: rad; Default: 0.08725; Minimum: 0
    """

    IS_SYMMETRICAL: ClassVar = 1
    MAGNET_COLOR = config_dict["PLOT"]["COLOR_DICT"]["MAGNET_COLOR"]
    W0: float = 0.043633
    """Slot isthmus orthoradial angular width."""
    H0: float = 0.006
    """Slot isthmus radial height."""
    H2: float = 0.04
    """Slot radial height below wedge """
    W2: float = 0.08725
    """Angle between slot edges"""

    # Inlined from Methods.Slot.SlotW22._comp_line_dict
    def _comp_line_dict(self):
        """Define a dictionnary of the lines to draw the slot
        If a line has begin==end, it is replaced by "None" (dict has always the same number of keys)

        Parameters
        ----------
        self : SlotW22
            A SlotW22 object

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
        Zc = 0

        # Creation of curve
        line_dict = {}
        if self.H0 > 0:
            line_dict["1-2"] = Segment(Z1, Z2)
        else:
            line_dict["1-2"] = None

        if self.W2 != self.W0:
            line_dict["2-3"] = Arc2(Z2, Zc, -(self.W2 - self.W0) / 2)
        else:
            line_dict["2-3"] = None
        line_dict["3-4"] = Segment(Z3, Z4)
        line_dict["4-5"] = Arc2(Z4, Zc, self.W2)
        line_dict["5-6"] = Segment(Z5, Z6)
        if self.W2 != self.W0:
            line_dict["6-7"] = Arc2(Z6, Zc, -(self.W2 - self.W0) / 2)
        else:
            line_dict["6-7"] = None

        if self.H0 > 0:
            line_dict["7-8"] = Segment(Z7, Z8)
        else:
            line_dict["7-8"] = None

        # Closing Arc (Rbo)
        line_dict["8-1"] = Arc1(Z8, Z1, -self.get_Rbo(), is_trigo_direction=False)

        # Closing Active part
        line_dict["2-7"] = Arc1(
            begin=Z2,
            end=Z7,
            radius=abs(Z7),
            is_trigo_direction=True,
        )
        line_dict["7-2"] = Arc1(
            begin=Z7,
            end=Z2,
            radius=-abs(Z7),
            is_trigo_direction=False,
        )

        return line_dict

    # Inlined from Methods.Slot.SlotW22._comp_point_coordinate
    def _comp_point_coordinate(self):
        """Compute the point coordinates needed to plot the Slot.

        Parameters
        ----------
        self : SlotW22
            A SlotW22 object

        Returns
        -------
        point_dict: dict
            A dict of the slot point coordinates
        """
        Rbo = self.get_Rbo()

        # comp point coordinate (in complex)
        Z1 = Rbo * np.exp(-1j * self.W0 / 2)
        if self.is_outwards():
            R1 = Rbo + self.H0
            R2 = Rbo + self.H0 + self.H2
        else:  # inward slot
            R1 = Rbo - self.H0
            R2 = Rbo - self.H0 - self.H2
        Z2 = R1 * np.exp(-1j * self.W0 / 2.0)
        Z3 = R1 * np.exp(-1j * self.W2 / 2.0)
        Z4 = R2 * np.exp(-1j * self.W2 / 2.0)

        point_dict = {}
        # symetry
        point_dict["Z1"] = Z1
        point_dict["Z2"] = Z2
        point_dict["Z3"] = Z3
        point_dict["Z4"] = Z4
        point_dict["Z5"] = Z4.conjugate()
        point_dict["Z6"] = Z3.conjugate()
        point_dict["Z7"] = Z2.conjugate()
        point_dict["Z8"] = Z1.conjugate()
        return point_dict

    # Inlined from Methods.Slot.SlotW22.build_geometry
    def build_geometry(self):
        """Compute the curve (Segment) needed to plot the object.
        The ending point of a curve is the starting point of the next curve in
        the list

        Parameters
        ----------
        self : SlotW22
            A SlotW22 object

        Returns
        -------
        curve_list: llist
            A list of 5 Segment and 3 Arc2

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

    # Inlined from Methods.Slot.SlotW22.build_geometry_active
    def build_geometry_active(self, Nrad, Ntan, alpha=0, delta=0):
        """Split the slot winding area in several zone

        Parameters
        ----------
        self : SlotW22
            A SlotW22 object
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

        Rbo = self.get_Rbo()

        # Polar Meshgrid
        if self.is_outwards():
            r = np.linspace(Rbo + self.H0, Rbo + self.H0 + self.H2, Nrad + 1)
        else:
            r = np.linspace(Rbo - self.H0, Rbo - self.H0 - self.H2, Nrad + 1)

        theta = np.linspace(-self.W2 / 2.0, self.W2 / 2.0, Ntan + 1)
        Z = np.meshgrid(r, theta)

        Z = Z[0] * np.exp(1j * Z[1])
        Z = Z.T
        # if self.is_outwards():
        #     assert Z[0][0] == (Rbo + self.H0) * exp(-1j * self.W2 * 0.5)  # Z6
        #     assert Z[Nrad][0] == (Rbo + self.H0 + self.H2) * exp(-1j * self.W2 * 0.5)  # Z5
        #     assert Z[0][Ntan] == (Rbo + self.H0) * exp(1j * self.W2 * 0.5)  # Z3
        #     assert Z[Nrad][Ntan] == (Rbo + self.H0 + self.H2) * exp(
        #         1j * self.W2 * 0.5
        #     )  # Z4
        # else:
        #     assert Z[0][0] == (Rbo - self.H0) * exp(-1j * self.W2 * 0.5)  # Z6
        #     assert Z[Nrad][0] == (Rbo - self.H0 - self.H2) * exp(-1j * self.W2 * 0.5)  # Z5
        #     assert Z[0][Ntan] == (Rbo - self.H0) * exp(1j * self.W2 * 0.5)  # Z3
        #     assert Z[Nrad][Ntan] == (Rbo - self.H0 - self.H2) * exp(
        #         1j * self.W2 * 0.5
        #     )  # Z4

        surf_list = []
        for jj in range(Ntan):  # jj from 0 to Ntan-1
            for ii in range(Nrad):  # ii from 0 to Nrad-1
                Z1 = Z[ii][jj]
                Z2 = Z[ii][jj + 1]
                Z3 = Z[ii + 1][jj + 1]
                Z4 = Z[ii + 1][jj]
                point_ref = (
                    Z[ii][jj] + Z[ii][jj + 1] + Z[ii + 1][jj + 1] + Z[ii + 1][jj]
                ) / 4  # the reference point of the surface
                curve_list = []
                curve_list.append(
                    Arc1(
                        Z1,
                        Z2,
                        abs(Z1),
                        is_trigo_direction=True,
                    )
                )
                curve_list.append(
                    Segment(
                        Z2,
                        Z3,
                        prop_dict={DRAW_PROP_LAB: False},
                    )
                )
                curve_list.append(
                    Arc1(
                        Z3,
                        Z4,
                        -abs(Z3),
                        is_trigo_direction=False,
                        prop_dict={DRAW_PROP_LAB: False},
                    )
                )
                curve_list.append(
                    Segment(
                        Z4,
                        Z1,
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
                )
                surf_list.append(surface)

        # Correct bottom line for particular case (cf Tests\Validation\Magnetics\test_FEMM_fast_draw.py)
        if (Ntan == 2 and Nrad == 1) and self.W0 != self.W2:
            # Cut Ox- surface
            arc_to_cut = surf_list[0].line_list[0]
            arc1, arc2 = arc_to_cut.split_line(Z1=0, Z2=Rbo * np.exp(-1j * self.W0 / 2))
            surf_list[0].line_list = [arc1[0], arc2[0]] + surf_list[0].line_list[1:]
            surf_list[0].line_list[1].prop_dict = {DRAW_PROP_LAB: False}
            # Cut Ox+ surface
            arc_to_cut = surf_list[1].line_list[0]
            arc1, arc2 = arc_to_cut.split_line(Z1=0, Z2=Rbo * np.exp(1j * self.W0 / 2))
            surf_list[1].line_list = [arc1[0], arc2[0]] + surf_list[1].line_list[1:]
            surf_list[1].line_list[0].prop_dict = {DRAW_PROP_LAB: False}

        for surf in surf_list:
            surf.rotate(alpha)
            surf.translate(delta)
        return surf_list

    # Inlined from Methods.Slot.SlotW22.check
    def check(self):
        """Check that the SlotW22 object is correct

        Parameters
        ----------
        self : SlotW22
            A SlotW22 object

        Returns
        -------
        None

        Raises
        -------
        S22_A02CheckError
            You must have W0 <= W2
        S22_SpCheckError
            You must have W2 < 2*pi/Zs
        """
        if self.W2 < self.W0:
            raise S22_A02CheckError("You must have W0 <= W2")

        if 2 * np.pi / self.Zs <= self.W2:
            raise S22_SpCheckError("You must have W2 < 2*pi/Zs")

    # Inlined from Methods.Slot.SlotW22.comp_angle_opening
    def comp_angle_opening(self):
        """Compute the average opening angle of the Slot

        Parameters
        ----------
        self : SlotW22
            A SlotW22 object

        Returns
        -------
        alpha: float
            Average opening angle of the slot [rad]

        """

        return self.W0

    # Inlined from Methods.Slot.SlotW22.comp_height
    def comp_height(self):
        """Compute the height of the Slot.
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotW22
            A SlotW22 object

        Returns
        -------
        Htot: float
            Height of the slot [m]

        """

        return self.H0 + self.H2

    # Inlined from Methods.Slot.SlotW22.comp_height_active
    def comp_height_active(self):
        """Compute the height of the winding area

        Parameters
        ----------
        self : SlotW22
            A SlotW22 object

        Returns
        -------
        Hwind: float
            Height of the winding area [m]

        """

        return self.H2

    # Inlined from Methods.Slot.SlotW22.comp_surface
    def comp_surface(self):
        """Compute the Slot total surface (by analytical computation).
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotW22
            A SlotW22 object

        Returns
        -------
        S: float
            Slot total surface [m**2]

        """
        return self.comp_surface_active() + self.comp_surface_opening()

    # Inlined from Methods.Slot.SlotW22.comp_surface_active
    def comp_surface_active(self):
        """Compute the Slot inner surface for winding (by analytical computation)

        Parameters
        ----------
        self : SlotW22
            A SlotW22 object

        Returns
        -------
        Swind: float
            Slot inner surface for winding [m**2]

        """
        Rbo = self.get_Rbo()

        if self.is_outwards():
            # Surface of the external disk
            Sext = ((self.H2 + self.H0 + Rbo) ** 2) * np.pi

            # Surface of the internal disk
            Sint = ((self.H0 + Rbo) ** 2) * np.pi
        else:
            # Surface of the external disk
            Sext = ((Rbo - self.H0) ** 2) * np.pi

            # Surface of the internal disk
            Sint = ((Rbo - self.H2 - self.H0) ** 2) * np.pi

        # Surface of the ring
        Sring = Sext - Sint

        # Only an W2 angle of the ring
        return Sring * self.W2 / (2 * np.pi)

    # Inlined from Methods.Slot.SlotW22.comp_surface_opening
    def comp_surface_opening(self):
        """Compute the Slot opening surface (by analytical computation).
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotW22
            A SlotW22 object

        Returns
        -------
        S: float
            Slot opening surface [m**2]

        """
        Rbo = self.get_Rbo()

        # Computation of isthmus surface
        if self.is_outwards():
            # Surface of the external disk
            Sext = ((self.H0 + Rbo) ** 2) * np.pi

            # Surface of the internal disk
            Sint = (Rbo**2) * np.pi
        else:
            # Surface of the external disk
            Sext = (Rbo**2) * np.pi

            # Surface of the internal disk
            Sint = ((Rbo - self.H0) ** 2) * np.pi
        # Surface of the ring
        Sring = Sext - Sint

        # Only an W0 angle of the ring
        return Sring * self.W0 / (2 * np.pi)

    # Inlined from Methods.Slot.SlotW22.get_surface_active
    def get_surface_active(self, alpha=0, delta=0):
        """Return the full winding surface

        Parameters
        ----------
        self : SlotW22
            A SlotW22 object
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
                curve.prop_dict = {}
            curve.prop_dict.update({DRAW_PROP_LAB: False})

        # Create surface
        label = self.parent.get_label() + "_" + WIND_LAB + "_R0-T0-S0"
        if self.is_outwards():
            Zmid = self.get_Rbo() + self.H0 + self.H2 / 2
        else:
            Zmid = self.get_Rbo() - self.H0 - self.H2 / 2
        surface = SurfLine(line_list=curve_list, label=label, point_ref=Zmid)

        # Apply transformation
        surface.rotate(alpha)
        surface.translate(delta)

        return surface

    # Inlined from Methods.Slot.SlotW22.get_surface_opening
    def get_surface_opening(self, alpha=0, delta=0):
        """Return the list of surfaces defining the opening area of the Slot

        Parameters
        ----------
        self : SlotW22
            A SlotW22 object
        alpha : float
            float number for rotation (Default value = 0) [rad]
        delta : complex
            complex number for translation (Default value = 0)

        Returns
        -------
        surf_list : list
            list of surfaces objects
        """

        # H0=0 => No opening
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
                curve.prop_dict = {}
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

    # Inlined from Methods.Slot.SlotW22.plot_schematics
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
        self : SlotW22
            A SlotW22 object
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
            slot = type(self)(Zs=8, H0=10e-3, W0=np.pi / 24, H2=60e-3, W2=np.pi / 8)
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
                R = Rbo + sign * self.H0 * 0.5
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
                    offset_label=sign * self.H0 * 0.4,
                    fontsize=SC_FONT_SIZE,
                )
                # W2
                R = Rbo + sign * (self.H0 + self.H2 * 0.5)
                line = Arc1(
                    begin=R * np.exp(-1j * self.W2 / 2),
                    end=R * np.exp(1j * self.W2 / 2),
                    radius=R,
                    is_trigo_direction=True,
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="W2",
                    offset_label=sign * self.H0 * 0.4,
                    fontsize=SC_FONT_SIZE,
                )
                # H0
                line = Segment(point_dict["Z1"], point_dict["Z2"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    label="H0",
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    offset_label=-1j * self.H0 * 0.8,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # H2
                line = Segment(point_dict["Z3"], point_dict["Z4"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    label="H2",
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    offset_label=-1j * self.H0 * 0.8,
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
                # Bot Arc
                line = Arc1(
                    begin=abs(point_dict["Z4"]) * np.exp(-1j * np.pi / 4),
                    end=abs(point_dict["Z4"]) * np.exp(1j * np.pi / 4),
                    radius=abs(point_dict["Z4"]),
                    is_trigo_direction=True,
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # Middle Arc
                line = Arc1(
                    begin=abs(point_dict["Z3"]) * np.exp(-1j * np.pi / 4),
                    end=abs(point_dict["Z3"]) * np.exp(1j * np.pi / 4),
                    radius=abs(point_dict["Z3"]),
                    is_trigo_direction=True,
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # Rad lines
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
                line = Segment(
                    0, lam.Rext * 1.5 * np.exp(1j * np.angle(point_dict["Z5"]))
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                line = Segment(
                    0, lam.Rext * 1.5 * np.exp(1j * np.angle(point_dict["Z7"]))
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
            W = point_dict["Z5"].imag * 1.2
            Rint = min(point_dict["Z4"].real, point_dict["Z1"].real)
            Rext = max(point_dict["Z4"].real, point_dict["Z1"].real)

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

    class MachineCheckError(Exception):
        """ """

    class LaminationCheckError(MachineCheckError):
        """ """

    class SlotCheckError(LaminationCheckError):
        """ """

    class S22_SpCheckError(SlotCheckError):
        """ """

    class S22_A02CheckError(SlotCheckError):
        """ """


MachineCheckError = SlotW22.MachineCheckError
LaminationCheckError = SlotW22.LaminationCheckError
SlotCheckError = SlotW22.SlotCheckError
S22_SpCheckError = SlotW22.S22_SpCheckError
S22_A02CheckError = SlotW22.S22_A02CheckError
