# Experimental dataclass generated from Generator/ClassesRef/Slot/SlotCirc.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass
from typing import ClassVar

import matplotlib.pyplot as plt
import numpy as np

from ..definitions import config_dict
from ..Functions_new.Geometry.circle_from_3_points import circle_from_3_points
from ..Functions_new.labels import DRAW_PROP_LAB, WIND_LAB
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
from ._error import ParentMissingError
from .arc_1 import Arc1
from .lam_slot import LamSlot
from .segment import Segment
from .slot import Slot
from .surf_line import SurfLine


@dataclass(eq=False)
class SlotCirc(Slot):
    """Circular slot (for notches)

    Attributes
    ----------
    W0 : float
        Slot isthmus width.
        Unit: m; Default: 0.01; Minimum: 0
    H0 : float
        Slot height
        Unit: m; Default: 0.03; Minimum: 0
    is_H0_bore : bool
        True to define H0 from top of arc to bore radius, False top arc to middle of W0 segment
        Default: True
    """

    IS_SYMMETRICAL: ClassVar = 1
    MAGNET_COLOR = config_dict["PLOT"]["COLOR_DICT"]["MAGNET_COLOR"]
    W0: float = 0.01
    """Slot isthmus width."""
    H0: float = 0.03
    """Slot height"""
    is_H0_bore: bool = True
    """True to define H0 from top of arc to bore radius, False top arc to middle of W0 segment"""

    # Inlined from Methods.Slot.SlotCirc._comp_line_dict
    def _comp_line_dict(self):
        """Define a dictionnary of the lines to draw the slot
        If a line has begin==end, it is replaced by "None" (dict has always the same number of keys)

        Parameters
        ----------
        self : SlotCirc
            A SlotCirc object

        Returns
        -------
        line_dict: dict
            Dictionnary of the slot lines (key: line name, value: line object)
        """

        point_dict = self._comp_point_coordinate()
        R0 = self._comp_R0()

        if self.H0 < self.W0 / 2:
            sign = -1
        else:
            sign = 1
        # Creation of curve
        if self.is_outwards():
            full_arc = Arc1(
                begin=point_dict["Z1"],
                end=point_dict["Z2"],
                radius=-R0 * sign,
                is_trigo_direction=True,
            )
        else:
            full_arc = Arc1(
                begin=point_dict["Z1"],
                end=point_dict["Z2"],
                radius=R0 * sign,
                is_trigo_direction=False,
            )

        line_dict = {}
        line_dict["1-2"] = full_arc
        # Split arc to avoid angle > 180 deg (for FEMM)
        line_dict["1-M"] = full_arc.copy()
        line_dict["1-M"].split_half(is_begin=True)
        line_dict["M-2"] = full_arc.copy()
        line_dict["M-2"].split_half(is_begin=False)
        # Closing arc
        line_dict["2-1"] = Arc1(
            begin=point_dict["Z2"],
            end=point_dict["Z1"],
            radius=-self.get_Rbo(),
            is_trigo_direction=False,
        )

        return line_dict

    # Inlined from Methods.Slot.SlotCirc._comp_point_coordinate
    def _comp_point_coordinate(self):
        """Compute the point coordinates needed to plot the Slot.

        Parameters
        ----------
        self : SlotCirc
            A SlotCirc object

        Returns
        -------
        point_dict: dict
            A dict of the slot coordinates
        """

        if self.is_H0_bore is None:
            self.is_H0_bore = True  # Set default value
        Rbo = self.get_Rbo()
        alpha = self.comp_angle_opening()

        Z1 = Rbo * np.exp(-1j * alpha / 2)
        Z2 = Rbo * np.exp(1j * alpha / 2)
        if self.is_H0_bore:
            if self.is_outwards():
                ZM = Rbo + self.H0
            else:
                ZM = Rbo - self.H0
            R0, _ = circle_from_3_points(Z1, Z2, ZM)
            ZH = Rbo
        else:
            if self.is_outwards():
                ZM = (Z1 + Z2) / 2 + self.H0
            else:
                ZM = (Z1 + Z2) / 2 - self.H0
            ZH = (Z1 + Z2) / 2
            R0 = None

        point_dict = {}
        # symetry
        point_dict["Z1"] = Z1
        point_dict["Z2"] = Z2
        point_dict["ZM"] = ZM
        point_dict["ZH"] = ZH  # For H0 schematics
        # Store R0 for _comp_R0
        if R0 is not None:
            point_dict["R0"] = R0
        return point_dict

    # Inlined from Methods.Slot.SlotCirc._comp_R0
    def _comp_R0(self):
        """Compute the radius of the circle

        Parameters
        ----------
        self : SlotCirc
            A SlotCirc object

        Returns
        -------
        R0 : float
            Radius of the circle [m]
        """

        if self.is_H0_bore is None:
            self.is_H0_bore = True  # Set default value

        if self.is_H0_bore:
            return self._comp_point_coordinate()["R0"]
        else:
            # R0 is the radius of the circle
            # Pythagore in Triangle: Center, Z2, middle(Z1,Z2)
            # R0**2 = (W0/2)**2 + (H0-R0)**2

            return ((self.W0 / 2) ** 2 + self.H0**2) / (2 * self.H0)

    # Inlined from Methods.Slot.SlotCirc.build_geometry
    def build_geometry(self):
        """Compute the curve (Line) needed to plot the Slot.
        The ending point of a curve is the starting point of the next curve in
        the list

        Parameters
        ----------
        self : SlotCirc
            A SlotCirc object

        Returns
        -------
        curve_list: list
            A list of one Arc
        """

        line_dict = self._comp_line_dict()

        curve_list = [
            line_dict["1-M"],
            line_dict["M-2"],
        ]
        return [line for line in curve_list if line is not None]

    # Inlined from Methods.Slot.SlotCirc.check
    def check(self):
        """Check that the SlotCirc object is correct

        Parameters
        ----------
        self : SlotCirc
            A SlotCirc object

        Returns
        -------
        None
        """
        pass

    # Inlined from Methods.Slot.SlotCirc.comp_angle_opening
    def comp_angle_opening(self):
        """Compute the average opening angle of the Slot

        Parameters
        ----------
        self : SlotCirc
            A SlotCirc object

        Returns
        -------
        alpha: float
            Average opening angle of the slot [rad]
        """

        Rbo = self.get_Rbo()

        return float(2 * np.arcsin(self.W0 / (2 * Rbo)))

    # Inlined from Methods.Slot.SlotCirc.comp_height
    def comp_height(self):
        """Compute the height of the Slot.
        Caution, the top of the Slot is an Arc

        Parameters
        ----------
        self : SlotCirc
            A SlotCirc object

        Returns
        -------
        Htot: float
            Height of the slot [m]
        """

        return self.comp_height_active()

    # Inlined from Methods.Slot.SlotCirc.comp_height_active
    def comp_height_active(self):
        """Compute the height of the winding area

        Parameters
        ----------
        self : SlotCirc
            A SlotCirc object

        Returns
        -------
        Hwind: float
            Height of the winding area [m]
        """

        if self.is_H0_bore is None:
            self.is_H0_bore = True  # Set default value

        if self.is_H0_bore:
            return self.H0
        else:
            point_dict = self._comp_point_coordinate()
            ZM = point_dict["ZM"]
            Rbo = self.get_Rbo()
            return abs(Rbo - abs(ZM))

    # Inlined from Methods.Slot.SlotCirc.comp_surface
    def comp_surface(self):
        """Compute the Slot total surface (by analytical computation).
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotCirc
            A SlotCirc object

        Returns
        -------
        S: float
            Slot total surface [m**2]

        """

        return self.comp_surface_active()

    # Inlined from Methods.Slot.SlotCirc.comp_surface_active
    def comp_surface_active(self):
        """Compute the Slot inner surface for winding (by analytical computation)

        Parameters
        ----------
        self : SlotCirc
            A SlotCirc object

        Returns
        -------
        Swind: float
            Slot inner surface for winding [m**2]
        """

        R0 = self._comp_R0()
        alpha = float(2 * np.arcsin(self.W0 / (2 * R0)))
        # Area of the full circle
        S1 = np.pi * (R0**2)
        # Area of the top Arc
        S2 = (R0**2.0) / 2.0 * (alpha - np.sin(alpha))
        # Arc of the bore
        alpha_op = self.comp_angle_opening()
        S3 = (self.get_Rbo() ** 2.0) / 2.0 * (alpha_op - np.sin(alpha_op))

        if self.H0 < self.W0 / 2:
            # Center is in airgap
            if self.is_outwards():
                return S2 - S3
            else:
                return S2 + S3
        else:  # Center is in the Lamination
            if self.is_outwards():
                return S1 - S2 - S3
            else:
                return S1 - S2 + S3

    # Inlined from Methods.Slot.SlotCirc.comp_surface_opening
    def comp_surface_opening(self):
        """Compute the Slot opening surface (by analytical computation).
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotCirc
            A SlotCirc object

        Returns
        -------
        S: float
            Slot opening surface [m**2]

        """

        return 0

    # Inlined from Methods.Slot.SlotCirc.convert_to_H0_bore
    def convert_to_H0_bore(self):
        """Convert the slot to the other definition of H0

        Parameters:
        -----------
        self : SlotCirc
            A SlotCirc objec with is_H0_bore==False
        """

        if self.is_H0_bore:
            raise Exception("Error, slot is already H0 bore type!")

        self.H0 = self.comp_height()
        self.is_H0_bore = True

    # Inlined from Methods.Slot.SlotCirc.get_surface_active
    def get_surface_active(self, alpha=0, delta=0):
        """Return the full active surface

        Parameters
        ----------
        self : SlotCirc
            A SlotCirc object
        alpha : float
            float number for rotation (Default value = 0) [rad]
        delta : complex
            complex number for translation (Default value = 0)

        Returns
        -------
        surf_wind: Surface
            Surface corresponding to the Active Area
        """

        # Create curve list
        line_dict = self._comp_line_dict()
        curve_list = [
            line_dict["1-M"],
            line_dict["M-2"],
            line_dict["2-1"],
        ]
        curve_list = [line for line in curve_list if line is not None]

        # Only the closing arc (2-1) needs to be drawn (in FEMM)
        for curve in curve_list[:-1]:
            if curve.prop_dict is None:
                curve.prop_dict = {}
            curve.prop_dict.update({DRAW_PROP_LAB: False})

        # Create surface
        ZM = line_dict["M-2"].get_begin()
        Zmid = (self.get_Rbo() + ZM) / 2
        label = self.parent.get_label() + "_" + WIND_LAB + "_R0-T0-S0"
        surface = SurfLine(line_list=curve_list, label=label, point_ref=Zmid)

        # Apply transformation
        surface.rotate(alpha)
        surface.translate(delta)

        return surface

    # Inlined from Methods.Slot.SlotCirc.get_surface_opening
    def get_surface_opening(self, alpha=0, delta=0):
        """Return the list of surfaces defining the opening area of the Slot

        Parameters
        ----------
        self : SlotCirc
            A SlotCirc object
        alpha : float
            float number for rotation (Default value = 0) [rad]
        delta : complex
            complex number for translation (Default value = 0)

        Returns
        -------
        surf_list : list
            list of surfaces objects
        """

        # No opening surface in SlotCirc
        return []

    # Inlined from Methods.Slot.SlotCirc.plot_schematics
    def plot_schematics(
        self,
        is_default=False,
        is_return_default=False,
        is_enforce_default_H0_bore=None,
        is_add_point_label=False,
        is_add_schematics=True,
        is_add_main_line=True,
        type_add_active=0,
        save_path=None,
        is_show_fig=True,
        fig=None,
        ax=None,
    ):
        """Plot the schematics of the slot

        Parameters
        ----------
        self : SlotCirc
            A SlotCirc object
        is_default : int
            0: current slot values, 1: default internal rotor schematics, 2: default external stator schematics
        is_return_default : bool
            True: return the default lamination used for the schematics (skip plot)
        is_enforce_default_H0_bore : bool
            To enforce is_H0_bore on default slot (is_default=True only), None use default value
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
            Figure containing the schematics
        ax : Matplotlib.axes.Axes object
            Axis containing the schematics
        -------
        lam : LamSlot
            Default lamination used for the schematics
        """

        # Use some default parameter
        if is_default:
            slot = type(self)(Zs=8, H0=10e-3, W0=45e-3, is_H0_bore=True)
            if is_enforce_default_H0_bore is not None:
                slot.is_H0_bore = is_enforce_default_H0_bore
            if is_default == 1:  # Internal rotor schematics
                lam = LamSlot(
                    Rint=0.1, Rext=0.135, is_internal=True, is_stator=False, slot=slot
                )
                if is_return_default:
                    return lam
            else:  # External stator schematics
                lam = LamSlot(
                    Rint=0.1, Rext=0.135, is_internal=False, is_stator=True, slot=slot
                )
                if is_return_default:
                    return lam
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
                line = Segment(begin=point_dict["Z1"], end=point_dict["Z2"])
                if self.is_outwards():
                    offset_label = -1 * self.H0 * 0.9 + 1j * 0.3 * self.W0
                else:
                    offset_label = self.H0 * 0.3 + 1j * 0.3 * self.W0
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="W0",
                    offset_label=offset_label,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # H0
                line = Segment(begin=point_dict["ZH"], end=point_dict["ZM"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="H0",
                    offset_label=1j * -0.15 * self.W0,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )

            if is_add_main_line:
                # Top arc
                line = Arc1(
                    begin=point_dict["Z1"],
                    end=point_dict["Z2"],
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

            # Zooming and cleaning
            W = self.W0 / 2 * 1.4
            Rint, Rext = self.comp_radius()

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
