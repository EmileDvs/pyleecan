# File generated according to Generator/ClassesRef/Slot/SlotW29.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Slot/SlotW29"""

from os import linesep
from sys import getsizeof

import matplotlib.pyplot as plt
import numpy as np
from pyleecan.Classes import ParentMissingError
from pyleecan.Classes.Arc1 import Arc1
from pyleecan.Classes.LamSlot import LamSlot
from pyleecan.Classes.Segment import Segment
from pyleecan.Classes.Slot import Slot
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
    plot_quote,
)
from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.labels import DRAW_PROP_LAB, SOP_LAB, WIND_LAB
from pyleecan.Functions.load import load_init_dict
from pyleecan.Functions.save import save


class SlotW29(Slot):

    VERSION = 1
    IS_SYMMETRICAL = 1
    MAGNET_COLOR = config_dict["PLOT"]["COLOR_DICT"]["MAGNET_COLOR"]

    # cf Methods.Slot.SlotW29._comp_line_dict
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
        line_dict = dict()
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

    # cf Methods.Slot.SlotW29._comp_point_coordinate
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

        point_dict = dict()

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

    # cf Methods.Slot.SlotW29.build_geometry
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

    # cf Methods.Slot.SlotW29.build_geometry_active
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
        surf_list = list()
        for jj in range(Ntan):  # jj from 0 to Ntan-1
            for ii in range(Nrad):  # ii from 0 to Nrad-1
                Z1 = Z[ii][jj]
                Z2 = Z[ii][jj + 1]
                Z3 = Z[ii + 1][jj + 1]
                Z4 = Z[ii + 1][jj]
                point_ref = (Z1 + Z2 + Z3 + Z4) / 4
                # With one zone the order would be [Z7,Z4,Z5,Z6]
                curve_list = list()
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

    # cf Methods.Slot.SlotW29.check
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

    # cf Methods.Slot.SlotW29.comp_angle_opening
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

    # cf Methods.Slot.SlotW29.comp_height
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

    # cf Methods.Slot.SlotW29.comp_height_active
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

    # cf Methods.Slot.SlotW29.comp_surface
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

    # cf Methods.Slot.SlotW29.comp_surface_active
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

    # cf Methods.Slot.SlotW29.comp_surface_opening
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

    # cf Methods.Slot.SlotW29.comp_surface_wedge
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

    # cf Methods.Slot.SlotW29.get_surface_active
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
                curve.prop_dict = dict()
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

    # cf Methods.Slot.SlotW29.get_surface_opening
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
                curve.prop_dict = dict()
            curve.prop_dict.update({DRAW_PROP_LAB: False})

        # Create surface
        label = self.parent.get_label() + "_" + SOP_LAB + "_R0-T0-S0"
        surface = SurfLine(line_list=curve_list, label=label, point_ref=Zmid)

        # Apply transformation
        surface.rotate(alpha)
        surface.translate(delta)

        return [surface]

    # cf Methods.Slot.SlotW29.get_surface_wedge
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

    # cf Methods.Slot.SlotW29.plot_schematics
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

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        W0=0.05,
        H0=0.001,
        H1=0.0015,
        W1=0.015,
        wedge_type=0,
        H2=0.03,
        W2=0.2,
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
            if "W1" in list(init_dict.keys()):
                W1 = init_dict["W1"]
            if "wedge_type" in list(init_dict.keys()):
                wedge_type = init_dict["wedge_type"]
            if "H2" in list(init_dict.keys()):
                H2 = init_dict["H2"]
            if "W2" in list(init_dict.keys()):
                W2 = init_dict["W2"]
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
        self.W1 = W1
        self.wedge_type = wedge_type
        self.H2 = H2
        self.W2 = W2
        # Call Slot init
        super(SlotW29, self).__init__(Zs=Zs, wedge_mat=wedge_mat, is_bore=is_bore)
        # The class is frozen (in Slot init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        SlotW29_str = ""
        # Get the properties inherited from Slot
        SlotW29_str += super(SlotW29, self).__str__()
        SlotW29_str += "W0 = " + str(self.W0) + linesep
        SlotW29_str += "H0 = " + str(self.H0) + linesep
        SlotW29_str += "H1 = " + str(self.H1) + linesep
        SlotW29_str += "W1 = " + str(self.W1) + linesep
        SlotW29_str += "wedge_type = " + str(self.wedge_type) + linesep
        SlotW29_str += "H2 = " + str(self.H2) + linesep
        SlotW29_str += "W2 = " + str(self.W2) + linesep
        return SlotW29_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from Slot
        if not super(SlotW29, self).__eq__(other):
            return False
        if other.W0 != self.W0:
            return False
        if other.H0 != self.H0:
            return False
        if other.H1 != self.H1:
            return False
        if other.W1 != self.W1:
            return False
        if other.wedge_type != self.wedge_type:
            return False
        if other.H2 != self.H2:
            return False
        if other.W2 != self.W2:
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
            super(SlotW29, self).compare(
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
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from Slot
        S += super(SlotW29, self).__sizeof__()
        S += getsizeof(self.W0)
        S += getsizeof(self.H0)
        S += getsizeof(self.H1)
        S += getsizeof(self.W1)
        S += getsizeof(self.wedge_type)
        S += getsizeof(self.H2)
        S += getsizeof(self.W2)
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
        SlotW29_dict = super(SlotW29, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        SlotW29_dict["W0"] = self.W0
        SlotW29_dict["H0"] = self.H0
        SlotW29_dict["H1"] = self.H1
        SlotW29_dict["W1"] = self.W1
        SlotW29_dict["wedge_type"] = self.wedge_type
        SlotW29_dict["H2"] = self.H2
        SlotW29_dict["W2"] = self.W2
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        SlotW29_dict["__class__"] = "SlotW29"
        return SlotW29_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        W0_val = self.W0
        H0_val = self.H0
        H1_val = self.H1
        W1_val = self.W1
        wedge_type_val = self.wedge_type
        H2_val = self.H2
        W2_val = self.W2
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
            W1=W1_val,
            wedge_type=wedge_type_val,
            H2=H2_val,
            W2=W2_val,
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
        self.W1 = None
        self.wedge_type = None
        self.H2 = None
        self.W2 = None
        # Set to None the properties inherited from Slot
        super(SlotW29, self)._set_None()

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
        doc="""Slot middle height

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
        doc="""Slot middle width.

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
        doc="""Slot bottom height

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
        doc="""Slot bottom width.

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

    class S29_W01CheckError(SlotCheckError):
        """ """

        pass

    class S29_H2CheckError(SlotCheckError):
        """ """

        pass


MachineCheckError = SlotW29.MachineCheckError

LaminationCheckError = SlotW29.LaminationCheckError

SlotCheckError = SlotW29.SlotCheckError

S29_W01CheckError = SlotW29.S29_W01CheckError

S29_H2CheckError = SlotW29.S29_H2CheckError
