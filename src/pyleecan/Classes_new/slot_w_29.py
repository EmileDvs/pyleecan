# Experimental dataclass generated from Generator/ClassesRef/Slot/SlotW29.csv
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
class SlotW29(Slot):
    """SlotW29

    Attributes
    ----------
    W0 : float
        Slot isthmus width.
        Unit: m; Default: 0.05; Minimum: 0
    H0 : float
        Slot isthmus height.
        Unit: m; Default: 0.001; Minimum: 0
    H1 : float
        Slot middle height
        Unit: m; Default: 0.0015; Minimum: 0
    W1 : float
        Slot middle width.
        Unit: m; Default: 0.015; Minimum: 0
    wedge_type : int
        selection type wedge
        Default: 0; Minimum: 0
    H2 : float
        Slot bottom height
        Unit: m; Default: 0.03; Minimum: 0
    W2 : float
        Slot bottom width.
        Unit: m; Default: 0.2; Minimum: 0
    """

    IS_SYMMETRICAL: ClassVar = 1
    MAGNET_COLOR = config_dict["PLOT"]["COLOR_DICT"]["MAGNET_COLOR"]
    W0: float = 0.05
    """Slot isthmus width."""
    H0: float = 0.001
    """Slot isthmus height."""
    H1: float = 0.0015
    """Slot middle height"""
    W1: float = 0.015
    """Slot middle width."""
    wedge_type: int = 0
    """selection type wedge"""
    H2: float = 0.03
    """Slot bottom height"""
    W2: float = 0.2
    """Slot bottom width."""

    # Inlined from Methods.Slot.SlotW29._comp_line_dict
    def _comp_line_dict(self):
        """Define a dictionnary of the lines to draw the slot
        If a line has begin==end, it is replaced by "None" (dict has always the same number of keys)

        Parameters
        ----------
        self : SlotW29
            A SlotW29 object

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
        Z12 = point_dict["Z12"]

        # Creation of curve
        line_dict = {}
        if self.H0 > 0:
            line_dict["1-2"] = Segment(Z1, Z2)
        else:
            line_dict["1-2"] = None

        if self.W0 != self.W1:
            line_dict["2-3"] = Segment(Z2, Z3)
        else:
            line_dict["2-3"] = None

        if self.H1 > 0:
            line_dict["3-4"] = Segment(Z3, Z4)
        else:
            line_dict["3-4"] = None
        if self.W1 != self.W2:
            line_dict["4-5"] = Segment(Z4, Z5)
        else:
            line_dict["4-5"] = None
        line_dict["5-6"] = Segment(Z5, Z6)
        line_dict["6-7"] = Segment(Z6, Z7)
        line_dict["7-8"] = Segment(Z7, Z8)
        if self.W1 != self.W2:
            line_dict["8-9"] = Segment(Z8, Z9)
        else:
            line_dict["8-9"] = None
        if self.H1 > 0:
            line_dict["9-10"] = Segment(Z9, Z10)
        else:
            line_dict["9-10"] = None

        if self.W0 != self.W1:
            line_dict["10-11"] = Segment(Z10, Z11)
        else:
            line_dict["10-11"] = None

        if self.H0 > 0:
            line_dict["11-12"] = Segment(Z11, Z12)
        else:
            line_dict["11-12"] = None

        # Closing Arc (Rbo)
        line_dict["12-1"] = Arc1(Z12, Z1, -self.get_Rbo(), is_trigo_direction=False)

        # Closing Active part
        line_dict["4-9"] = Segment(Z4, Z9)
        line_dict["9-4"] = Segment(Z9, Z4)

        line_dict["11-2"] = Segment(Z11, Z2)
        line_dict["2-11"] = Segment(Z2, Z11)

        return line_dict

    # Inlined from Methods.Slot.SlotW29._comp_point_coordinate
    def _comp_point_coordinate(self):
        """Compute the point coordinates needed to plot the Slot.

        Parameters
        ----------
        self : SlotW29
            A SlotW29 object

        Returns
        -------
        point_dict: dict
            A dict of the slot point coordinates
        """
        Rbo = self.get_Rbo()

        # alpha is the angle to rotate Z0 so ||Z1,Z12|| = W0
        alpha = np.arcsin(self.W0 / (2 * Rbo))

        Z0 = Rbo * np.exp(1j * 0)
        Z1 = Z0 * np.exp(-1j * alpha)

        if self.is_outwards():
            Z2 = Z1 + self.H0
            Z3 = Z2 - (self.W1 - self.W0) * 1j / 2.0
            Z4 = Z3 + self.H1
            Z5 = Z4 - (self.W2 - self.W1) * 1j / 2.0
            Z6 = Z5 + self.H2
        else:
            Z2 = Z1 - self.H0
            Z3 = Z2 - (self.W1 - self.W0) * 1j / 2.0
            Z4 = Z3 - self.H1
            Z5 = Z4 - (self.W2 - self.W1) * 1j / 2.0
            Z6 = Z5 - self.H2

        point_dict = {}

        point_dict["Z1"] = Z1
        point_dict["Z2"] = Z2
        point_dict["Z3"] = Z3
        point_dict["Z4"] = Z4
        point_dict["Z5"] = Z5
        point_dict["Z6"] = Z6
        # symetry
        point_dict["Z7"] = Z6.conjugate()
        point_dict["Z8"] = Z5.conjugate()
        point_dict["Z9"] = Z4.conjugate()
        point_dict["Z10"] = Z3.conjugate()
        point_dict["Z11"] = Z2.conjugate()
        point_dict["Z12"] = Z1.conjugate()
        return point_dict

    # Inlined from Methods.Slot.SlotW29.build_geometry
    def build_geometry(self):
        """Compute the curve (Line) needed to plot the Slot.
        The ending point of a curve is the starting point of the next curve in
        the list

        Parameters
        ----------
        self : SlotW29
            A SlotW29 object

        Returns
        -------
        curve_list: list
            A list of 11 Segment

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
            line_dict["10-11"],
            line_dict["11-12"],
        ]
        return [line for line in curve_list if line is not None]

    # Inlined from Methods.Slot.SlotW29.build_geometry_active
    def build_geometry_active(self, Nrad, Ntan, alpha=0, delta=0):
        """Split the slot winding area in several zone

        Parameters
        ----------
        self : SlotW29
            A SlotW29 object
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
        surf_list: list
            List of surface delimiting the winding zone
        """

        # get the name of the lamination
        lam_label = self.parent.get_label()

        point_dict = self._comp_point_coordinate()
        Z5 = point_dict["Z5"]
        Z6 = point_dict["Z6"]
        Z7 = point_dict["Z7"]
        Z8 = point_dict["Z8"]

        X = np.linspace(Z5, Z6, Nrad + 1)

        # Nrad+1 and Ntan+1 because 3 points => 2 zones
        Z = np.zeros((Nrad + 1, Ntan + 1), dtype=complex)
        for ii in range(Nrad + 1):
            Z[ii][:] = np.linspace(X[ii], X[ii].conjugate(), Ntan + 1)

        assert Z[0][0] == Z5
        assert Z[Nrad][0] == Z6
        assert Z[0][Ntan] == Z8
        assert Z[Nrad][Ntan] == Z7
        Z_8 = Z5 + (self.W2 / 2) + (self.W1 / 2)
        Z_5 = Z5 + (self.W2 / 2) - (self.W1 / 2)
        # We go thought the zone by Rad then Tan, starting by (0,0)
        surf_list = []
        for jj in range(Ntan):  # jj from 0 to Ntan-1
            for ii in range(Nrad):  # ii from 0 to Nrad-1
                Z1 = Z[ii][jj]
                Z2 = Z[ii][jj + 1]
                Z3 = Z[ii + 1][jj + 1]
                Z4 = Z[ii + 1][jj]
                point_ref = (Z1 + Z2 + Z3 + Z4) / 4
                # With one zone the order would be [Z7,Z4,Z5,Z6]
                curve_list = []
                curve_list.append(Segment(Z1, Z2))
                curve_list.append(
                    Segment(
                        Z2,
                        Z3,
                        prop_dict={DRAW_PROP_LAB: False},
                    )
                )
                curve_list.append(
                    Segment(
                        Z3,
                        Z4,
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
        if (
            Ntan == 2
            and Nrad == 1
            and (
                (self.W1 != self.W2 and self.H1 != 0)
                or (self.H1 == 0 and self.W0 != self.W2)
            )
        ):
            if self.H1 > 0:  # Cut on W1
                ZOm = point_dict["Z4"]
                ZOp = point_dict["Z9"]
            else:  # Cut on W0
                ZOm = point_dict["Z2"]
                ZOp = point_dict["Z11"]
            # Cut Ox- surface
            arc_to_cut = surf_list[0].line_list[0]
            arc1, arc2 = arc_to_cut.split_line(Z1=0, Z2=ZOm)
            surf_list[0].line_list = [arc1[0], arc2[0]] + surf_list[0].line_list[1:]
            surf_list[0].line_list[1].prop_dict = {DRAW_PROP_LAB: False}
            # Cut Ox+ surface
            arc_to_cut = surf_list[1].line_list[0]
            arc1, arc2 = arc_to_cut.split_line(Z1=0, Z2=ZOp)
            surf_list[1].line_list = [arc1[0], arc2[0]] + surf_list[1].line_list[1:]
            surf_list[1].line_list[0].prop_dict = {DRAW_PROP_LAB: False}

        for surf in surf_list:
            surf.rotate(alpha)
            surf.translate(delta)
        return surf_list

    # Inlined from Methods.Slot.SlotW29.check
    def check(self):
        """Check that the SlotW29 object is correct

        Parameters
        ----------
        self : SlotW29
            A SlotW29 object

        Returns
        -------
        None

        Raises
        -------
        S29_W01CheckError
            You must have W0 <= W1

        S29_W12CheckError
            You must have W1 <= W2

        S29_H2CheckError
            You must have H2 > 0

        """
        if self.W1 < self.W0:
            raise S29_W01CheckError("You must have W0 <= W1")

        elif self.H2 == 0:
            raise S29_H2CheckError("You must have H2 > 0")

    # Inlined from Methods.Slot.SlotW29.comp_angle_opening
    def comp_angle_opening(self):
        """Compute the average opening angle of the Slot

        Parameters
        ----------
        self : SlotW29
            A SlotW29 object

        Returns
        -------
        alpha: float
            Average opening angle of the slot [rad]

        """
        Rbo = self.get_Rbo()

        return float(2 * np.arcsin(self.W0 / (2 * Rbo)))

    # Inlined from Methods.Slot.SlotW29.comp_height
    def comp_height(self):
        """Compute the height of the Slot.
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotW29
            A SlotW29 object

        Returns
        -------
        Htot: float
            Height of the slot [m]

        """
        Rbo = self.get_Rbo()

        # Computation of the arc height
        alpha = self.comp_angle_opening() / 2
        Harc = float(Rbo * (1 - np.cos(alpha)))

        if self.is_outwards():
            return (
                abs(Rbo - Harc + self.H0 + self.H1 + self.H2 + 1j * self.W2 / 2.0) - Rbo
            )
        else:
            return self.H0 + self.H1 + self.H2 + Harc

    # Inlined from Methods.Slot.SlotW29.comp_height_active
    def comp_height_active(self):
        """Compute the height of the winding area

        Parameters
        ----------
        self : SlotW29
            A SlotW29 object

        Returns
        -------
        Hwind: float
            Height of the winding area [m]

        """

        return self.H2

    # Inlined from Methods.Slot.SlotW29.comp_surface
    def comp_surface(self):
        """Compute the Slot total surface (by analytical computation).
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotW29
            A SlotW29 object

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

    # Inlined from Methods.Slot.SlotW29.comp_surface_active
    def comp_surface_active(self):
        """Compute the Slot inner surface for winding (by analytical computation)

        Parameters
        ----------
        self : SlotW29
            A SlotW29 object

        Returns
        -------
        Swind: float
            Slot inner surface for winding [m**2]

        """

        return self.W2 * self.H2

    # Inlined from Methods.Slot.SlotW29.comp_surface_opening
    def comp_surface_opening(self):
        """Compute the Slot opening surface (by analytical computation).
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotW29
            A SlotW29 object

        Returns
        -------
        S: float
            Slot opening surface [m**2]

        """

        Rbo = self.get_Rbo()

        S0 = self.H0 * self.W0
        S1 = self.H1 * self.W1

        # The bottom is an arc
        alpha = self.comp_angle_opening()
        Sarc = (Rbo**2.0) / 2.0 * (alpha - np.sin(alpha))

        # Because Slamination = S - Zs * Sslot
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

    # Inlined from Methods.Slot.SlotW29.comp_surface_wedge
    def comp_surface_wedge(self):
        """Compute the Slot wedge surface (by analytical computation).
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotW29
            A SlotW29 object

        Returns
        -------
        S: float
            Slot wedge surface [m**2]

        """
        # Selection type Wedge
        if self.wedge_type == 0:
            return self.comp_surface_opening()

        if self.wedge_type == 1:
            return (self.W1) * self.H1

    # Inlined from Methods.Slot.SlotW29.get_surface_active
    def get_surface_active(self, alpha=0, delta=0):
        """Return the full winding surface

        Parameters
        ----------
        self : SlotW29
            A SlotW29 object
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
            line_dict["7-8"],
            line_dict["8-9"],
            line_dict["9-4"],
        ]
        curve_list = [line for line in curve_list if line is not None]

        # Only the closing arc (9-4) needs to be drawn (in FEMM)
        for curve in curve_list[:-1]:
            if curve.prop_dict is None:
                curve.prop_dict = {}
            curve.prop_dict.update({DRAW_PROP_LAB: False})

        # Create surface
        if self.is_outwards():
            Zmid = self.get_Rbo() + self.H0 + self.H1 + self.H2 / 2
        else:
            Zmid = self.get_Rbo() - self.H0 - self.H1 - self.H2 / 2
        label = self.parent.get_label() + "_" + WIND_LAB + "_R0-T0-S0"
        surface = SurfLine(line_list=curve_list, label=label, point_ref=Zmid)

        # Apply transformation
        surface.rotate(alpha)
        surface.translate(delta)

        return surface

    # Inlined from Methods.Slot.SlotW29.get_surface_opening
    def get_surface_opening(self, alpha=0, delta=0):
        """Return the list of surfaces defining the opening area of the Slot

        Parameters
        ----------
        self : SlotW29
            A SlotW29 object
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
        if self.H0 == 0 and self.H1 == 0:
            return []

        # Create curve list
        line_dict = self._comp_line_dict()
        # Selection type Wedge
        if self.wedge_type == 0:
            # Create curve list

            curve_list = [
                line_dict["1-2"],
                line_dict["2-3"],
                line_dict["3-4"],
                line_dict["4-9"],
                line_dict["9-10"],
                line_dict["10-11"],
                line_dict["11-12"],
                line_dict["12-1"],
            ]
            # Create surface
            if self.is_outwards():
                Zmid = self.get_Rbo() + (self.H0 + self.H1) / 2
            else:
                Zmid = self.get_Rbo() - (self.H0 + self.H1) / 2

        else:
            # Create curve list
            curve_list = [
                line_dict["1-2"],
                line_dict["2-11"],
                line_dict["11-12"],
                line_dict["12-1"],
            ]
            # Create surface
            if self.is_outwards():
                Zmid = self.get_Rbo() + self.H0 / 2
            else:
                Zmid = self.get_Rbo() - self.H0 / 2

        curve_list = [line for line in curve_list if line is not None]

        # Only the closing arc (12-1) needs to be drawn (in FEMM)
        for curve in curve_list[:-1]:
            if curve.prop_dict is None:
                curve.prop_dict = {}
            curve.prop_dict.update({DRAW_PROP_LAB: False})

        # Create surface
        label = self.parent.get_label() + "_" + SOP_LAB + "_R0-T0-S0"
        surface = SurfLine(line_list=curve_list, label=label, point_ref=Zmid)

        # Apply transformation
        surface.rotate(alpha)
        surface.translate(delta)

        return [surface]

    # Inlined from Methods.Slot.SlotW29.get_surface_wedge
    def get_surface_wedge(self, alpha=0, delta=0):
        """Return the list of surfaces defining the opening area of the Slot

        Parameters
        ----------
        self : SlotW29
            A SlotW29 object
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
        if self.H0 == 0 and self.H1 == 0:
            return []

        # Create curve list
        line_dict = self._comp_line_dict()
        curve_list = [
            line_dict["2-3"],
            line_dict["3-4"],
            line_dict["4-9"],
            line_dict["9-10"],
            line_dict["10-11"],
            line_dict["11-2"],
        ]
        curve_list = [line for line in curve_list if line is not None]

        # Create surface
        if self.is_outwards():
            Zmid = self.get_Rbo() + self.H0 + self.H1 / 2
        else:
            Zmid = self.get_Rbo() - self.H0 + self.H1 / 2

        label = self.parent.get_label() + "_" + SOP_LAB + "_R0-T0-S0"
        surface = SurfLine(line_list=curve_list, label=label, point_ref=Zmid)

        # Apply transformation
        surface.rotate(alpha)
        surface.translate(delta)

        return [surface]

    # Inlined from Methods.Slot.SlotW29.plot_schematics
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
        self : SlotW29
            A SlotW29 object
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
            0: No active surface, 1: active surface as winding, 2: active surface as magnet, 3: active surface as winding + wedges, 4: type_active =3 and wedge_type = 1
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
                Zs=8,
                H0=10e-3,
                H1=20e-3,
                H2=60e-3,
                W0=20e-3,
                W1=40e-3,
                W2=60e-3,
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
                Zs=8, H0=10e-3, H1=20e-3, H2=60e-3, W0=20e-3, W1=40e-3, W2=60e-3
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
                line = Segment(point_dict["Z1"], point_dict["Z12"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="W0",
                    offset_label=-self.H0 * 0.9,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # W1
                line = Segment(
                    (point_dict["Z3"] + point_dict["Z4"]) / 2,
                    (point_dict["Z9"] + point_dict["Z10"]) / 2,
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="W1",
                    offset_label=-self.H0 * 0.9,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # W2
                Zlim1 = point_dict["Z6"] + sign * self.H0
                Zlim2 = point_dict["Z7"] + sign * self.H0
                plot_quote(
                    point_dict["Z6"],
                    Zlim1,
                    Zlim2,
                    point_dict["Z7"],
                    offset_label=self.H0 * 0.3,
                    fig=fig,
                    ax=ax,
                    label="W2",
                )
                # H0
                Zlim1 = point_dict["Z12"].real + 1j * point_dict["Z7"].imag
                Zlim2 = point_dict["Z11"].real + 1j * point_dict["Z7"].imag
                plot_quote(
                    point_dict["Z12"],
                    Zlim1,
                    Zlim2,
                    point_dict["Z11"],
                    offset_label=1j * self.H0 * 0.4,
                    fig=fig,
                    ax=ax,
                    label="H0",
                )
                # H1
                line = Segment(point_dict["Z3"], point_dict["Z4"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="H1",
                    offset_label=-1j * self.H0 * 0.6,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # H2
                line = Segment(point_dict["Z5"].real, point_dict["Z6"].real)
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="H2",
                    offset_label=1j * self.H0 * 0.4,
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
                    end=point_dict["Z12"],
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
                line = Segment(point_dict["Z2"], point_dict["Z11"])
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
            W = max(self.W1, self.W2, self.W0) * 0.7
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

    class MachineCheckError(Exception):
        """ """

    class LaminationCheckError(MachineCheckError):
        """ """

    class SlotCheckError(LaminationCheckError):
        """ """

    class S29_H2CheckError(SlotCheckError):
        """ """

    class S29_W01CheckError(SlotCheckError):
        """ """


MachineCheckError = SlotW29.MachineCheckError
LaminationCheckError = SlotW29.LaminationCheckError
SlotCheckError = SlotW29.SlotCheckError
S29_H2CheckError = SlotW29.S29_H2CheckError
S29_W01CheckError = SlotW29.S29_W01CheckError
