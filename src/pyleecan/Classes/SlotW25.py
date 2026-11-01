# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Slot/SlotW25.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Slot/SlotW25
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
from pyleecan.Methods.Slot.SlotW25.check import check
from pyleecan.Classes.Segment import Segment
from pyleecan.Classes.Arc1 import Arc1
import numpy as np, matplotlib.pyplot as plt
from pyleecan.Classes.SurfLine import SurfLine
from pyleecan.Functions.labels import WIND_LAB, DRAW_PROP_LAB, SOP_LAB
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
)
from pyleecan.Methods import ParentMissingError


from pyleecan.Classes._check import InitUnKnowClassError


class SlotW25(Slot):

    VERSION = 1
    IS_SYMMETRICAL = 1
    MAGNET_COLOR = config_dict["PLOT"]["COLOR_DICT"]["MAGNET_COLOR"]

    # cf Methods.Slot.SlotW25._comp_line_dict
    def _comp_line_dict(self):
        """Define a dictionnary of the lines to draw the slot
        If a line has begin==end, it is replaced by "None" (dict has always the same number of keys)

        Parameters
        ----------
        self : SlotW25
            A SlotW25 object

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
        # Creation of curve
        line_dict = dict()
        line_dict["1-2"] = Segment(Z1, Z2)
        line_dict["2-3"] = Arc1(Z2, Z3, -abs(Z2), is_trigo_direction=False)
        line_dict["3-4"] = Segment(Z3, Z4)
        line_dict["4-5"] = Arc1(Z4, Z5, abs(Z5))
        line_dict["5-6"] = Segment(Z5, Z6)
        line_dict["6-7"] = Arc1(Z6, Z7, -abs(Z2), is_trigo_direction=False)
        line_dict["7-8"] = Segment(Z7, Z8)

        # Closing Arc (Rbo)
        line_dict["8-1"] = Arc1(Z8, Z1, -self.get_Rbo(), is_trigo_direction=False)

        # Closing Active part
        line_dict["2-7"] = Arc1(Z2, Z7, abs(Z2), is_trigo_direction=True)
        line_dict["7-2"] = Arc1(Z7, Z2, -abs(Z2), is_trigo_direction=False)

        return line_dict

    # cf Methods.Slot.SlotW25._comp_point_coordinate
    def _comp_point_coordinate(self):
        """Compute the point coordinates needed to plot the Slot.

        Parameters
        ----------
        self : SlotW25
            A SlotW25 object

        Returns
        -------
        point_dict: dict
            A dict of the slot point coordinates
        """
        Rbo = self.get_Rbo()

        # We compute the point on the tooth, then rotation to get the slot
        # Zxt is the equivalent of point Zx in tooth ref

        # alpha_0 is the angle to rotate Z0 so ||Z1,Z8|| = W4
        alpha_0 = float(np.arcsin(self.W4 / (2 * Rbo)))

        # comp point coordinate (in complex)
        Z0 = Rbo * np.exp(1j * 0)
        Z1t = Z0 * np.exp(1j * alpha_0)

        if self.is_outwards():
            Z2t = Z1t + self.H1
            # alpha_1 is the angle of Z3t so ||Z3t,Z6t|| = W3
            alpha_1 = float(np.arcsin(self.W3 / (2 * abs(Z2t))))
            Z3t = abs(Z2t) * np.exp(1j * alpha_1)
            Z4t = Z3t + self.H2
        else:  # inward slot
            Z2t = Z1t - self.H1
            # alpha_1 is the angle of Z3t so ||Z3t,Z6t|| = W3
            alpha_1 = float(np.arcsin(self.W3 / (2 * abs(Z2t))))
            Z3t = abs(Z2t) * np.exp(1j * alpha_1)
            Z4t = Z3t - self.H2

        point_dict = dict()
        # Rotation to get the slot
        hssp = np.pi / self.Zs
        point_dict["Z1"] = Z1t * np.exp(-1j * hssp)
        point_dict["Z2"] = Z2t * np.exp(-1j * hssp)
        point_dict["Z3"] = Z3t * np.exp(-1j * hssp)
        point_dict["Z4"] = Z4t * np.exp(-1j * hssp)
        # symetry
        point_dict["Z5"] = point_dict["Z4"].conjugate()
        point_dict["Z6"] = point_dict["Z3"].conjugate()
        point_dict["Z7"] = point_dict["Z2"].conjugate()
        point_dict["Z8"] = point_dict["Z1"].conjugate()

        return point_dict

    # cf Methods.Slot.SlotW25.build_geometry
    def build_geometry(self):
        """Compute the curve needed to plot the object.
        The ending point of a curve is the starting point of the next curve in
        the list

        Parameters
        ----------
        self : SlotW25
            A SlotW25 object

        Returns
        -------
        curve_list: list
            A list of 4 Segment and 3 Arc
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

    # cf Methods.Slot.SlotW25.build_geometry_active
    def build_geometry_active(self, Nrad, Ntan, alpha=0, delta=0):
        """Split the slot winding area in several zone

        Parameters
        ----------
        self : SlotW25
            A SlotW25 object
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
        Z3 = point_dict["Z3"]
        Z4 = point_dict["Z4"]
        Z5 = point_dict["Z5"]
        Z6 = point_dict["Z6"]
        X = np.linspace(Z3, Z4, Nrad + 1)

        # Nrad+1 and Ntan+1 because 3 points => 2 zones
        Z = np.zeros((Nrad + 1, Ntan + 1), dtype=complex)
        for ii in range(Nrad + 1):
            Z[ii][:] = abs(X[ii]) * np.exp(
                1j * np.linspace(np.angle(X[ii]), np.angle(X[ii].conjugate()), Ntan + 1)
            )

        if self.is_outwards():
            assert abs(Z3) < abs(Z4)
            assert abs(Z6) < abs(Z5)
        assert abs(Z[0][0] - Z3) < 1e-6
        assert abs(Z[Nrad][0] - Z4) < 1e-6
        assert abs(Z[0][Ntan] - Z6) < 1e-6
        assert abs(Z[Nrad][Ntan] - Z5) < 1e-6

        # We go thought the zone by Rad then Tan, starting by (0,0)
        surf_list = list()
        for jj in range(Ntan):  # jj from 0 to Ntan-1
            for ii in range(Nrad):  # ii from 0 to Nrad-1
                Z1 = Z[ii][jj]
                Z2 = Z[ii][jj + 1]
                Z3 = Z[ii + 1][jj + 1]
                Z4 = Z[ii + 1][jj]
                point_ref = (Z1 + Z2 + Z3 + Z4) / 4  # reference point of the surface
                # With one zone the order would be [Z7,Z4,Z5,Z6]
                curve_list = list()
                curve_list.append(Arc1(Z1, Z2, abs(Z1), is_trigo_direction=True))
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
        if Ntan == 2 and Nrad == 1:
            Z2 = point_dict["Z2"]
            Z7 = point_dict["Z7"]
            # Cut Ox- surface
            arc_to_cut = surf_list[0].line_list[0]
            arc1, arc2 = arc_to_cut.split_line(Z1=0, Z2=Z2)
            surf_list[0].line_list = [arc1[0], arc2[0]] + surf_list[0].line_list[1:]
            surf_list[0].line_list[1].prop_dict = {DRAW_PROP_LAB: False}
            # Cut Ox+ surface
            arc_to_cut = surf_list[1].line_list[0]
            arc1, arc2 = arc_to_cut.split_line(Z1=0, Z2=Z7)
            surf_list[1].line_list = [arc1[0], arc2[0]] + surf_list[1].line_list[1:]
            surf_list[1].line_list[0].prop_dict = {DRAW_PROP_LAB: False}

        for surf in surf_list:
            surf.rotate(alpha)
            surf.translate(delta)
        return surf_list

    # cf Methods.Slot.SlotW25.check
    check = check

    # cf Methods.Slot.SlotW25.comp_angle_opening
    def comp_angle_opening(self):
        """Compute the average opening angle of the Slot

        Parameters
        ----------
        self : SlotW25
            A SlotW25 object

        Returns
        -------
        alpha: float
            Average opening angle of the slot [rad]

        """
        Rbo = self.get_Rbo()

        slot_pitch = 2 * np.pi / self.Zs

        alpha_4 = float(2 * np.arcsin(self.W4 / (2 * Rbo)))
        return slot_pitch - alpha_4

    # cf Methods.Slot.SlotW25.comp_height
    def comp_height(self):
        """Compute the height of the Slot.
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotW25
            A SlotW25 object

        Returns
        -------
        Htot: float
            Height of the slot [m]

        """
        point_dict = self._comp_point_coordinate()
        Z4 = point_dict["Z4"]
        Rbo = self.get_Rbo()

        if self.is_outwards():
            return abs(Z4) - Rbo
        else:  # inward slot
            return Rbo - abs(Z4)

    # cf Methods.Slot.SlotW25.comp_height_active
    def comp_height_active(self):
        """Compute the height of the winding area

        Parameters
        ----------
        self : SlotW25
            A SlotW25 object

        Returns
        -------
        Hwind: float
            Height of the winding area [m]

        """

        return self.H2

    # cf Methods.Slot.SlotW25.comp_surface
    def comp_surface(self):
        """Compute the Slot total surface (by analytical computation).
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotW25
            A SlotW25 object

        Returns
        -------
        S: float
            Slot total surface [m**2]

        """
        return self.comp_surface_active() + self.comp_surface_opening()

    # cf Methods.Slot.SlotW25.comp_surface_active
    def comp_surface_active(self):
        """Compute the Slot inner surface for winding (by analytical computation)

        Parameters
        ----------
        self : SlotW25
            A SlotW25 object

        Returns
        -------
        Swind: float
            Slot inner surface for winding [m**2]

        """

        point_dict = self._comp_point_coordinate()
        Z2 = point_dict["Z2"]
        Z4 = point_dict["Z4"]

        if self.is_outwards():
            Rint = abs(Z2)
            Rext = abs(Z4)
        else:
            Rint = abs(Z4)
            Rext = abs(Z2)

        # Surface of a slot pitch
        Sring = (np.pi * Rext**2 - np.pi * Rint**2) * 1 / self.Zs

        # Tooth surface
        St = self.H2 * self.W3

        alpha_bore = 2 * np.arcsin(self.W3 / (2 * Rint))
        Sarc_bore = (Rint**2.0) / 2.0 * (alpha_bore - np.sin(alpha_bore))

        alpha_yoke = 2 * np.arcsin(self.W3 / (2 * Rext))
        Sarc_yoke = (Rext**2.0) / 2.0 * (alpha_yoke - np.sin(alpha_yoke))

        return Sring - (St + Sarc_yoke - Sarc_bore)

    # cf Methods.Slot.SlotW25.comp_surface_opening
    def comp_surface_opening(self):
        """Compute the Slot opening surface (by analytical computation).
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotW25
            A SlotW25 object

        Returns
        -------
        S: float
            Slot opening surface [m**2]

        """

        point_dict = self._comp_point_coordinate()
        Z1 = point_dict["Z1"]
        Z2 = point_dict["Z2"]

        if self.is_outwards():
            Rint = abs(Z1)
            Rext = abs(Z2)
        else:
            Rint = abs(Z2)
            Rext = abs(Z1)

        # Surface of a slot pitch
        Sring = (np.pi * Rext**2 - np.pi * Rint**2) * 1 / self.Zs

        # Tooth surface
        St = self.H1 * self.W4

        alpha_bore = 2 * np.arcsin(self.W4 / (2 * Rint))
        Sarc_bore = (Rint**2.0) / 2.0 * (alpha_bore - np.sin(alpha_bore))

        alpha_yoke = 2 * np.arcsin(self.W4 / (2 * Rext))
        Sarc_yoke = (Rext**2.0) / 2.0 * (alpha_yoke - np.sin(alpha_yoke))

        return Sring - (St + Sarc_yoke - Sarc_bore)

    # cf Methods.Slot.SlotW25.get_surface_active
    def get_surface_active(self, alpha=0, delta=0):
        """Return the full winding surface

        Parameters
        ----------
        self : SlotW25
            A SlotW25 object
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
            Zmid = self.get_Rbo() + self.H1 + self.H2 / 2
        else:
            Zmid = self.get_Rbo() - self.H1 - self.H2 / 2
        label = self.parent.get_label() + "_" + WIND_LAB + "_R0-T0-S0"
        surface = SurfLine(line_list=curve_list, label=label, point_ref=Zmid)

        # Apply transformation
        surface.rotate(alpha)
        surface.translate(delta)

        return surface

    # cf Methods.Slot.SlotW25.get_surface_opening
    def get_surface_opening(self, alpha=0, delta=0):
        """Return the list of surfaces defining the opening area of the Slot

        Parameters
        ----------
        self : SlotW25
            A SlotW25 object
        alpha : float
            float number for rotation (Default value = 0) [rad]
        delta : complex
            complex number for translation (Default value = 0)

        Returns
        -------
        surf_list : list
            list of surfaces objects
        """

        # H1=0 no opening
        if self.H1 == 0:
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
            Zmid = self.get_Rbo() + self.H1 / 2
        else:
            Zmid = self.get_Rbo() - self.H1 / 2
        label = self.parent.get_label() + "_" + SOP_LAB + "_R0-T0-S0"
        surface = SurfLine(line_list=curve_list, label=label, point_ref=Zmid)

        # Apply transformation
        surface.rotate(alpha)
        surface.translate(delta)

        return [surface]

    # cf Methods.Slot.SlotW25.plot_schematics
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
        self : SlotW25
            A SlotW25 object
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
            slot = type(self)(Zs=14, W3=20e-3, H2=80e-3, H1=15e-3, W4=40e-3)
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
            sp = 2 * np.pi / self.Zs
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
                # W4
                line = Segment(point_dict["Z8"], point_dict["Z1"] * np.exp(1j * sp))
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="W4",
                    offset_label=self.H1 * 0.3,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # W3
                line = Segment(
                    (point_dict["Z3"] + point_dict["Z4"]) / 2,
                    (point_dict["Z5"] + point_dict["Z6"]) / 2 * np.exp(-1j * sp),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="W3",
                    offset_label=self.H1 * 0.3,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # H1
                line = Segment(point_dict["Z1"], point_dict["Z2"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="H1",
                    offset_label=-1j * self.H1 * 0.8,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # H2
                line = Segment(point_dict["Z5"], point_dict["Z6"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    label="H2",
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    offset_label=-1j * self.H1 * 0.6,
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
                # Middle arc
                R = abs(point_dict["Z3"])
                line = Arc1(
                    begin=R * np.exp(-1j * np.pi / 2 * 0.9),
                    end=R * np.exp(1j * np.pi / 2 * 0.9),
                    radius=R,
                    is_trigo_direction=True,
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # Bot arc
                R = abs(point_dict["Z4"])
                line = Arc1(
                    begin=R * np.exp(-1j * np.pi / 2 * 0.9),
                    end=R * np.exp(1j * np.pi / 2 * 0.9),
                    radius=R,
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
                line = Segment(0, lam.Rext * 1.5 * np.exp(-1j * sp / 2))
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                line = Segment(0, lam.Rext * 1.5 * np.exp(1j * sp / 2))
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
            W = (point_dict["Z4"] * np.exp(1j * sp)).imag * 1.1
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

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        W3=0.003,
        H2=0.003,
        W4=0.003,
        H1=0.003,
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
            if "W3" in list(init_dict.keys()):
                W3 = init_dict["W3"]
            if "H2" in list(init_dict.keys()):
                H2 = init_dict["H2"]
            if "W4" in list(init_dict.keys()):
                W4 = init_dict["W4"]
            if "H1" in list(init_dict.keys()):
                H1 = init_dict["H1"]
            if "Zs" in list(init_dict.keys()):
                Zs = init_dict["Zs"]
            if "wedge_mat" in list(init_dict.keys()):
                wedge_mat = init_dict["wedge_mat"]
            if "is_bore" in list(init_dict.keys()):
                is_bore = init_dict["is_bore"]
        # Set the properties (value check and convertion are done in setter)
        self.W3 = W3
        self.H2 = H2
        self.W4 = W4
        self.H1 = H1
        # Call Slot init
        super(SlotW25, self).__init__(Zs=Zs, wedge_mat=wedge_mat, is_bore=is_bore)
        # The class is frozen (in Slot init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        SlotW25_str = ""
        # Get the properties inherited from Slot
        SlotW25_str += super(SlotW25, self).__str__()
        SlotW25_str += "W3 = " + str(self.W3) + linesep
        SlotW25_str += "H2 = " + str(self.H2) + linesep
        SlotW25_str += "W4 = " + str(self.W4) + linesep
        SlotW25_str += "H1 = " + str(self.H1) + linesep
        return SlotW25_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from Slot
        if not super(SlotW25, self).__eq__(other):
            return False
        if other.W3 != self.W3:
            return False
        if other.H2 != self.H2:
            return False
        if other.W4 != self.W4:
            return False
        if other.H1 != self.H1:
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
            super(SlotW25, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
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
            other._W4 is not None
            and self._W4 is not None
            and np.isnan(other._W4)
            and np.isnan(self._W4)
        ):
            pass
        elif other._W4 != self._W4:
            if is_add_value:
                val_str = " (self=" + str(self._W4) + ", other=" + str(other._W4) + ")"
                diff_list.append(name + ".W4" + val_str)
            else:
                diff_list.append(name + ".W4")
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
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from Slot
        S += super(SlotW25, self).__sizeof__()
        S += getsizeof(self.W3)
        S += getsizeof(self.H2)
        S += getsizeof(self.W4)
        S += getsizeof(self.H1)
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
        SlotW25_dict = super(SlotW25, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        SlotW25_dict["W3"] = self.W3
        SlotW25_dict["H2"] = self.H2
        SlotW25_dict["W4"] = self.W4
        SlotW25_dict["H1"] = self.H1
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        SlotW25_dict["__class__"] = "SlotW25"
        return SlotW25_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        W3_val = self.W3
        H2_val = self.H2
        W4_val = self.W4
        H1_val = self.H1
        Zs_val = self.Zs
        if self.wedge_mat is None:
            wedge_mat_val = None
        else:
            wedge_mat_val = self.wedge_mat.copy()
        is_bore_val = self.is_bore
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(
            W3=W3_val,
            H2=H2_val,
            W4=W4_val,
            H1=H1_val,
            Zs=Zs_val,
            wedge_mat=wedge_mat_val,
            is_bore=is_bore_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.W3 = None
        self.H2 = None
        self.W4 = None
        self.H1 = None
        # Set to None the properties inherited from Slot
        super(SlotW25, self)._set_None()

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
        doc="""Teeth bottom width

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
        doc="""Slot bottom height

        :Type: float
        :min: 0
        """,
    )

    def _get_W4(self):
        """getter of W4"""
        return self._W4

    def _set_W4(self, value):
        """setter of W4"""
        check_var("W4", value, "float", Vmin=0)
        self._W4 = value

    W4 = property(
        fget=_get_W4,
        fset=_set_W4,
        doc="""Teeth top width

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
        doc="""Slot top height

        :Type: float
        :min: 0
        """,
    )
