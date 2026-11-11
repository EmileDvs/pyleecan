# Experimental dataclass generated from Generator/ClassesRef/Slot/SlotWLSRPM.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass
from typing import ClassVar

import matplotlib.pyplot as plt
import numpy as np

from ..definitions import config_dict
from ..Functions_new.labels import WIND_LAB
from ..Functions_new.Plot import (
    ARROW_COLOR,
    ARROW_WIDTH,
    MAIN_LINE_COLOR,
    MAIN_LINE_STYLE,
    MAIN_LINE_WIDTH,
    P_FONT_SIZE,
    SC_FONT_SIZE,
    TEXT_BOX,
)
from ._error import ParentMissingError, SlotCheckError
from .arc_1 import Arc1
from .lam_slot import LamSlot
from .segment import Segment
from .slot import Slot
from .surf_line import SurfLine


@dataclass(eq=False)
class SlotWLSRPM(Slot):
    """Open Rectangular or trapezoidal slot with wedge

    Attributes
    ----------
    W1 : float
        Slot bottom side width.
        Unit: m; Default: 0.008; Minimum: 0
    W3 : float
        Tooth width
        Unit: m; Default: 0.0116; Minimum: 0
    H2 : float
        Slot height
        Unit: m; Default: 0.0148; Minimum: 0
    R1 : float
        Top radius
        Unit: m; Default: 0.00075; Minimum: 0
    H3 : float
        damper winding height
        Unit: m; Default: 0.001; Minimum: 0
    """

    IS_SYMMETRICAL: ClassVar = 1
    MAGNET_COLOR = config_dict["PLOT"]["COLOR_DICT"]["MAGNET_COLOR"]
    W1: float = 0.008
    """Slot bottom side width."""
    W3: float = 0.0116
    """Tooth width"""
    H2: float = 0.0148
    """Slot height """
    R1: float = 0.00075
    """Top radius"""
    H3: float = 0.001
    """damper winding height"""

    # Inlined from Methods.Slot.SlotWLSRPM._comp_point_coordinate
    def _comp_point_coordinate(self):
        """Compute the point coordinates needed to plot the Slot.

        Parameters
        ----------
        self : SlotWLSRPM
            A SlotWLSRPM object

        Returns
        -------
        point_dict: dict
            A dict of the slot coordinates
        """

        Rbo = self.get_Rbo()

        hsp = np.pi / self.Zs  # Half slot pitch

        # ZXt => Complex coordinate in the tooth ref
        # ZX => Complex coordinate in the slot ref
        y1t = self.W1 + self.W3 / 2
        # Point Zch slot midium high point
        Zch = Rbo + self.H2
        # Point Zcl slot midium low point
        Zcl = Rbo

        # relation bewteen the axis tooth and the axis slot
        Zcht = Zch * np.exp(1j * hsp)
        xcht = Zch * np.cos(hsp)
        ycht = Zch * np.sin(hsp)

        Zclt = Zcl * np.exp(1j * hsp)
        xclt = Zcl * np.cos(hsp)
        yclt = Zcl * np.sin(hsp)

        # Line Zch Zcl
        # y=-(xcht-xclt)/(ycht-yclt)*x+ycht+xcht*(xcht-xclt)/(ycht-yclt)

        # Z4
        x4t = (
            (self.W1 + self.W3 / 2 - ycht - xcht * (xcht - xclt) / (ycht - yclt))
            * -(ycht - yclt)
            / (xcht - xclt)
        )
        y4t = (
            -(xcht - xclt) / (ycht - yclt) * x4t
            + ycht
            + xcht * (xcht - xclt) / (ycht - yclt)
        )
        Z4t = x4t + 1j * y4t
        Z4 = Z4t * np.exp(-1j * hsp)
        # Z3
        x3t = x4t
        y3t = y4t - self.W1 + self.R1
        Z3t = x3t + 1j * y3t
        Z3 = Z3t * np.exp(-1j * hsp)
        # Z2
        x2t = x3t - self.R1
        y2t = self.W3 / 2
        Z2t = x2t + 1j * y2t
        Z2 = Z2t * np.exp(-1j * hsp)
        # Z1
        y1t = self.W3 / 2
        x1t = np.sqrt((Rbo) ** 2 - (y1t) ** 2)
        Z1t = x1t + 1j * y1t
        Z1 = Z1t * np.exp(-1j * hsp)

        # Z9 damper winding point

        x9t = x1t + self.H3
        y9t = self.W3 / 2
        Z9t = x9t + 1j * y9t
        Z9 = Z9t * np.exp(-1j * hsp)

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
        point_dict["Z9"] = Z9
        point_dict["Z10"] = Z9.conjugate()
        point_dict["Zcl"] = Rbo
        point_dict["Zcm"] = Rbo + self.H3
        point_dict["Zch"] = Rbo + self.H2
        point_dict["Zmid"] = (point_dict["Zcl"] + point_dict["Zch"]) / 2.0
        # Zc1
        xc1 = Z2.real
        yc1 = Z3.imag
        Zc1 = (xc1 + 1j * yc1).conjugate()

        point_dict["Zc1"] = Zc1

        return point_dict

    # Inlined from Methods.Slot.SlotWLSRPM.build_geometry
    def build_geometry(self):
        """Compute the curve (Line) needed to plot the Slot.
        The ending point of a curve is the starting point of the next curve in
        the list

        Parameters
        ----------
        self : SlotWLSRPM
            A SlotWLSRPM object

        Returns
        -------
        curve_list: list
            A list of 5 Segments and 2 Arcs

        """

        Rbo = self.get_Rbo()

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
        curve_list = []
        curve_list.append(Segment(Z1, Z2))
        curve_list.append(Arc1(Z2, Z3, self.R1, is_trigo_direction=True))
        curve_list.append(Segment(Z3, Z4))
        curve_list.append(Segment(Z4, Z5))
        curve_list.append(Segment(Z5, Z6))
        curve_list.append(Arc1(Z6, Z7, self.R1, is_trigo_direction=True))
        curve_list.append(Segment(Z7, Z8))

        return curve_list

    # Inlined from Methods.Slot.SlotWLSRPM.build_geometry_active
    def build_geometry_active(self, Nrad, Ntan, is_simplified=False, alpha=0, delta=0):
        """Split the slot active area in several zone

        Parameters
        ----------
        self : SlotWLSRPM
            A SlotWLSRPM object
        Nrad : int
            Number of radial layer
        Ntan : int
            Number of tangentiel layer
        is_simplified : bool
            boolean to specify if coincident lines are considered as one or different lines (Default value = False)
        alpha : float
            Angle for rotation (Default value = 0) [rad]
        delta : Complex
            complex for translation (Default value = 0)

        Returns
        -------
        surf_list:
            List of surface delimiting the active zone

        """

        lam_label = self.parent.get_label()
        Rbo = self.get_Rbo()

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

        Zcl = point_dict["Zcl"]
        Zcm = point_dict["Zcm"]
        Zch = point_dict["Zch"]
        Zmid = point_dict["Zmid"]

        # Creation of curve
        surf_list = []
        if Nrad == 1 and Ntan == 2:
            # Part 1 (0,0)
            line1 = Segment(Z3, Z4)
            line2 = Segment(Z4, Zch)
            line3 = Segment(Zch, Zcl)
            line4 = Arc1(Zcl, Z1, -Rbo, is_trigo_direction=False)
            line5 = Segment(Z1, Z2)
            line6 = Arc1(Z2, Z3, self.R1, is_trigo_direction=True)
            point_ref = (Z3 + Z4 + Zch + Zcl + Z1 + Z2) / 6

            surface = SurfLine(
                line_list=[line1, line2, line3, line4, line5, line6],
                label=(lam_label + "_" + WIND_LAB + "_R0-T0-S0"),
                point_ref=point_ref,
            )
            surf_list.append(surface)

            # Part2 (0,1)
            line1 = Segment(Zch, Z5)
            line2 = Segment(Z5, Z6)
            line3 = Arc1(Z6, Z7, self.R1, is_trigo_direction=True)
            line4 = Segment(Z7, Z8)
            line5 = Arc1(Z8, Zcl, -Rbo, is_trigo_direction=False)
            line6 = Segment(Zcl, Zch)
            point_ref = (Zch + Z5 + Z6 + Z7 + Z8 + Zcl) / 6
            surface = SurfLine(
                line_list=[line1, line2, line3, line4, line5, line6],
                label=(lam_label + "_" + WIND_LAB + "_R0-T1-S0"),
                point_ref=point_ref,
            )
            surf_list.append(surface)

        if Nrad == 2 and Ntan == 2:
            # Part 1 (0,0)
            line1 = Segment(Z3, Z4)
            line2 = Segment(Z4, Zch)
            line3 = Segment(Zch, Zcm)
            line4 = Arc1(Zcm, Z9, -(Rbo + self.H3), is_trigo_direction=False)
            line5 = Segment(Z9, Z2)
            line6 = Arc1(Z2, Z3, self.R1, is_trigo_direction=True)
            point_ref = (Z3 + Z4 + Zch + Zcm + Z9 + Z2) / 6

            surface = SurfLine(
                line_list=[line1, line2, line3, line4, line5, line6],
                label=(lam_label + "_" + WIND_LAB + "_R0-T0-S0"),
                point_ref=point_ref,
            )
            surf_list.append(surface)

            # Part2 (0,1)
            line1 = Segment(Zch, Z5)
            line2 = Segment(Z5, Z6)
            line3 = Arc1(Z6, Z7, self.R1, is_trigo_direction=True)
            line4 = Segment(Z7, Z10)
            line5 = Arc1(Z10, Zcm, -(Rbo + self.H3), is_trigo_direction=False)
            line6 = Segment(Zcm, Zch)
            point_ref = (Zch + Z5 + Z6 + Z7 + Z10 + Zcm) / 6
            surface = SurfLine(
                line_list=[line1, line2, line3, line4, line5, line6],
                label=(lam_label + "_" + WIND_LAB + "_R0-T1-S0"),
                point_ref=point_ref,
            )
            surf_list.append(surface)

            # Part3 (1,1)
            line1 = Arc1(Zcm, Z10, Rbo + self.H3, is_trigo_direction=True)
            line2 = Segment(Z10, Z8)
            line3 = Arc1(Z8, Zcl, -Rbo, is_trigo_direction=False)
            line4 = Segment(Zcl, Zcm)
            point_ref = (Zcm + Z10 + Z8 + Zcl) / 4
            surface = SurfLine(
                line_list=[line1, line2, line3, line4],
                label=(lam_label + "_" + WIND_LAB + "_R1-T1-S0"),
                point_ref=point_ref,
            )
            surf_list.append(surface)

            # Part4 (1,0)
            line1 = Arc1(Z9, Zcm, Rbo + self.H3, is_trigo_direction=True)
            line2 = Segment(Zcm, Zcl)
            line3 = Arc1(Zcl, Z1, -Rbo, is_trigo_direction=False)
            line4 = Segment(Z1, Z9)
            point_ref = (Z9 + Zcm + Zcl + Z1) / 4
            surface = SurfLine(
                line_list=[line1, line2, line3, line4],
                label=(lam_label + "_" + WIND_LAB + "_R1-T0-S0"),
                point_ref=point_ref,
            )
            surf_list.append(surface)

        else:  # Default : only one zone
            curve_list = self.build_geometry()

            # Add a line to close the winding area
            lines = [
                Arc1(
                    curve_list[-1].end,
                    curve_list[0].begin,
                    -Rbo,
                    is_trigo_direction=False,
                )
            ]
            lines.extend(curve_list)
            surface = SurfLine(
                line_list=lines,
                label=lam_label + "_" + WIND_LAB + "_R0-T0-S0",
                point_ref=Zmid,
            )
            surf_list.append(surface)

        for surf in surf_list:
            surf.rotate(alpha)
            surf.translate(delta)
        return surf_list

    # Inlined from Methods.Slot.SlotWLSRPM.check
    def check(self):
        """Check that the SlotW16 object is correct

        Parameters
        ----------
        self : SlotWLSRPM
            A SlotWLSRPM object

        Returns
        -------
        None

        Raises
        -------

        """

        if self.is_outwards():
            raise self.SLSRPMOutterError(
                "Slot Type LSRPM can’t be used on outer lamination"
            )

    # Inlined from Methods.Slot.SlotWLSRPM.comp_angle_opening
    def comp_angle_opening(self):
        """Compute the average opening angle of the Slot

        Parameters
        ----------
        self : SlotWLSRPM：
            A SlotWLSRPM： object

        Returns
        -------
        alpha: float
            Average opening angle of the slot [rad]

        """
        Rbo = self.get_Rbo()
        return 2 * (np.pi / self.Zs - np.arcsin(self.W3 / 2 / Rbo))

    # Inlined from Methods.Slot.SlotWLSRPM.comp_height
    def comp_height(self):
        """Compute the height of the Slot.
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotWLSRPM
            A SlotWLSRPM object

        Returns
        -------
        Htot: float
            Height of the slot [m]

        """

        return self.H2

    # Inlined from Methods.Slot.SlotWLSRPM.comp_height_damper
    def comp_height_damper(self):
        """Compute the height of the damper winding area

        Parameters
        ----------
        self : SlotWLSRPM
            A SlotWLSRPM object

        Returns
        -------
        Hwind: float
            Height of the damper winding area [m]

        """

        return self.H3

    # Inlined from Methods.Slot.SlotWLSRPM.comp_height_wind
    def comp_height_wind(self):
        """Compute the height of the winding area

        Parameters
        ----------
        self : SlotWLSRPM
            A SlotWLSRPM object

        Returns
        -------
        Hwind: float
            Height of the winding area [m]

        """

        return self.H2 - self.H3

    # Inlined from Methods.Slot.SlotWLSRPM.get_surface_active
    def get_surface_active(self, alpha=0, delta=0):
        """Return the full winding surface

        Parameters
        ----------
        self : SlotWLSRPM
            A SlotWLSRPM object
        alpha : float
            float number for rotation (Default value = 0) [rad]
        delta : complex
            complex number for translation (Default value = 0)

        Returns
        -------
        surf_wind: Surface
            Surface corresponding to the Winding Area
        """

        # get the name of the lamination
        st = self.get_name_lam()

        # Create curve list
        curve_list = self.build_geometry()
        curve_list.append(
            Arc1(
                begin=curve_list[-1].get_end(),
                end=curve_list[0].get_begin(),
                radius=-self.get_Rbo(),
                is_trigo_direction=False,
            )
        )

        # Create surface
        if self.is_outwards():
            Zmid = self.get_Rbo() + self.H2 / 2
        else:
            Zmid = self.get_Rbo() - self.H2 / 2
        surface = SurfLine(
            line_list=curve_list, label="Wind_" + st + "_R0_T0_S0", point_ref=Zmid
        )

        # Apply transformation
        surface.rotate(alpha)
        surface.translate(delta)

        return surface

    # Inlined from Methods.Slot.SlotWLSRPM.plot_schematics
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
        self : SlotWLSRPM
            A SlotWLSRPM object
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
            Figure containing the plot
        ax : Matplotlib.axes.Axes object
            Axis containing the plot
        -------
        lam : LamSlot
            Default lamination used for the schematics
        """

        # Use some default parameter
        if is_default:
            slot = type(self)(
                Zs=12, W1=8e-3, W3=11.6e-3, H2=14.8e-3, R1=0.75e-3, H3=2e-3
            )
            lam = LamSlot(
                Rint=50.7e-3,
                Rext=72.5e-3,
                is_internal=False,
                is_stator=True,
                L1=0.95,
                Nrvd=0,
                Wrvd=0,
                slot=slot,
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
                # W1
                line = Segment(
                    point_dict["Z4"] + 0.005 - 1j * 0.002,
                    point_dict["Z2"] + 0.005 - 1j * 0.002,
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="W1",
                    offset_label=self.H3 * 5,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # W3
                line = Segment(
                    point_dict["Z2"],
                    point_dict["Z2"]
                    + self.W3 * np.exp(1j * -(np.pi / 2 + 15 / 180 * np.pi)),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="W3",
                    offset_label=-1j * 0.01,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )

                # H2
                line = Segment(point_dict["Zch"], point_dict["Zcl"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="H2",
                    offset_label=-1j * self.H3 * 3,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # H3
                line = Segment(
                    point_dict["Zcm"] + 1j * 0.003 - 0.0001,
                    point_dict["Zcl"] + 1j * 0.003 - 0.0001,
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="H3",
                    offset_label=-self.H3 * 2 + 1j * self.H3 * 2,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )

                # R1
                line = Segment(point_dict["Zc1"], point_dict["Z7"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    label="R1",
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    offset_label=self.H3 * 0.8,
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
                # damper arc
                line = Arc1(
                    begin=point_dict["Z9"],
                    end=point_dict["Z10"],
                    radius=self.get_Rbo(),
                    is_trigo_direction=True,
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )

            if type_add_active == 1:
                self.plot_active(fig=fig, is_show_fig=False)
            elif type_add_active == 2:
                self.plot_active(
                    fig=fig, is_show_fig=False, enforced_default_color=self.MAGNET_COLOR
                )

            # Zooming and cleaning
            W = (point_dict["Zch"] * np.exp(1j * sp)).imag
            Rint = min(point_dict["Z2"].real, point_dict["Z1"].real)
            Rext = max(point_dict["Z2"].real, point_dict["Z1"].real)

            ax.axis("equal")
            ax.set_xlim(Rint, Rext)
            ax.set_ylim(-W * 0.9, W * 0.7)
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

    class SLSRPMOutterError(SlotCheckError):
        """ """
