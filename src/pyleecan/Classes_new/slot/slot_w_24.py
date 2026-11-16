# Experimental dataclass generated from Generator/ClassesRef/Slot/SlotW24.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, ClassVar

import matplotlib.pyplot as plt
import numpy as np

from ...classes_common.errors import (
    ParentMissingError,
    S24_HWCheckError,
    S24_W3CheckError,
)
from ...Functions_new.labels import DRAW_PROP_LAB, WIND_LAB
from ...Functions_new.Plot import (
    ARROW_COLOR,
    ARROW_WIDTH,
    MAIN_LINE_COLOR,
    MAIN_LINE_STYLE,
    MAIN_LINE_WIDTH,
    P_FONT_SIZE,
    SC_FONT_SIZE,
    TEXT_BOX,
)
from ..geometry.arc_1 import Arc1
from ..geometry.segment import Segment
from ..geometry.surf_line import SurfLine
from ..machine.lam_slot import LamSlot
from .slot import Slot

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure

    from ..geometry.line import Line
    from ..geometry.surface import Surface
    from ..machine.lamination import Lamination


@dataclass(eq=False)
class SlotW24(Slot):
    """SlotW24

    Attributes
    ----------
    W3 : float
        Teeth width
        Unit: m; Default: 0.003; Minimum: 0
    H2 : float
        Slot height
        Unit: m; Default: 0.003; Minimum: 0
    """

    IS_SYMMETRICAL: ClassVar = 1

    W3: float = field(default=0.003, metadata={"unit": "m", "min": 0})
    """Teeth width"""
    H2: float = field(default=0.003, metadata={"unit": "m", "min": 0})
    """Slot height"""

    _package: ClassVar[str] = "Slot"
    """Name of the package of the legacy class module"""

    # Inlined from Methods.Slot.SlotW24._comp_line_dict
    def _comp_line_dict(self) -> dict:
        """Define a dictionnary of the lines to draw the slot
        If a line has begin==end, it is replaced by "None" (dict has always the same number of keys)

        Parameters
        ----------
        self : SlotW24
            A SlotW24 object

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
        Zc = 0

        # Creation of curve
        line_dict = {}
        line_dict["1-2"] = Segment(begin=Z1, end=Z2)
        line_dict["2-3"] = Arc1(begin=Z2, end=Z3, radius=abs(Z2))
        line_dict["3-4"] = Segment(begin=Z3, end=Z4)

        # Closing Arc (Rbo)
        line_dict["4-1"] = Arc1(
            begin=Z4, end=Z1, radius=-self.get_Rbo(), is_trigo_direction=False
        )

        # Closing Active part
        line_dict["1-4"] = Arc1(
            begin=Z1, end=Z4, radius=self.get_Rbo(), is_trigo_direction=True
        )

        return line_dict

    # Inlined from Methods.Slot.SlotW24._comp_point_coordinate
    def _comp_point_coordinate(self) -> dict:
        """Compute the point coordinates needed to plot the Slot.

        Parameters
        ----------
        self : SlotW24
            A SlotW24 object

        Returns
        -------
        point_dict: dict
            A dict of the slot point coordinates
        """
        Rbo = self.get_Rbo()

        # alpha_0 is the angle to have a W3 tooth width on the bore
        alpha_0 = float(np.arcsin(self.W3 / (2 * Rbo)))

        # comp point coordinate (in complex)
        Z0 = Rbo * np.exp(1j * 0)
        Z1t = Z0 * np.exp(1j * alpha_0)

        if self.is_outwards():
            Z2t = Z1t + self.H2
        else:  # inward slot
            Z2t = Z1t - self.H2
        hsp = np.pi / self.Zs

        point_dict = {}
        # symetry
        point_dict["Z1"] = Z1t * np.exp(-1j * hsp)
        point_dict["Z2"] = Z2t * np.exp(-1j * hsp)
        point_dict["Z3"] = point_dict["Z2"].conjugate()
        point_dict["Z4"] = point_dict["Z1"].conjugate()
        return point_dict

    # Inlined from Methods.Slot.SlotW24.build_geometry
    def build_geometry(self) -> list:
        """Compute the curve needed to plot the object.
        The ending point of a curve is the starting point of the next curve in
        the list

        Parameters
        ----------
        self : SlotW24
            A SlotW24 object

        Returns
        -------
        curve_list: list
            A list of 2 Segment and 1 Arc

        """

        line_dict = self._comp_line_dict()

        curve_list = [
            line_dict["1-2"],
            line_dict["2-3"],
            line_dict["3-4"],
        ]
        return [line for line in curve_list if line is not None]

    # Inlined from Methods.Slot.SlotW24.build_geometry_active
    def build_geometry_active(
        self, Nrad: int, Ntan: int, alpha: float = 0, delta: complex = 0
    ) -> list:
        """Split the slot winding area in several zone

        Parameters
        ----------
        self : SlotW24
            A SlotW24 object
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
        Z1 = point_dict["Z1"]
        Z2 = point_dict["Z2"]
        Z3 = point_dict["Z3"]
        Z4 = point_dict["Z4"]

        X = np.linspace(Z1, Z2, Nrad + 1)

        # Nrad+1 and Ntan+1 because 3 points => 2 zones
        Z = np.zeros((Nrad + 1, Ntan + 1), dtype=complex)
        for ii in range(Nrad + 1):
            Z[ii][:] = abs(X[ii]) * np.exp(
                1j * np.linspace(np.angle(X[ii]), np.angle(X[ii].conjugate()), Ntan + 1)
            )

        assert abs(Z[0][0] - Z1) < 1e-6
        assert abs(Z[Nrad][0] - Z2) < 1e-6
        assert abs(Z[0][Ntan] - Z4) < 1e-6
        assert abs(Z[Nrad][Ntan] - Z3) < 1e-6

        # We go thought the zone by Rad then Tan, starting by (0,0)
        surf_list = []
        for jj in range(Ntan):  # jj from 0 to Ntan-1
            for ii in range(Nrad):  # ii from 0 to Nrad-1
                Z1 = Z[ii][jj]
                Z2 = Z[ii][jj + 1]
                Z3 = Z[ii + 1][jj + 1]
                Z4 = Z[ii + 1][jj]
                point_ref = (Z1 + Z2 + Z3 + Z4) / 4  # reference point of the surface
                # With one zone the order would be [Z7,Z4,Z5,Z6]
                curve_list: list[Line] = []
                curve_list.append(
                    Arc1(begin=Z1, end=Z2, radius=abs(Z1), is_trigo_direction=True)
                )
                curve_list.append(
                    Segment(
                        begin=Z2,
                        end=Z3,
                        prop_dict={DRAW_PROP_LAB: False},
                    )
                )
                curve_list.append(
                    Arc1(
                        begin=Z3,
                        end=Z4,
                        radius=-abs(Z3),
                        is_trigo_direction=False,
                        prop_dict={DRAW_PROP_LAB: False},
                    )
                )
                curve_list.append(
                    Segment(
                        begin=Z4,
                        end=Z1,
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

        for surf in surf_list:
            surf.rotate(alpha)
            surf.translate(delta)
        return surf_list

    # Inlined from Methods.Slot.SlotW24.check
    def check(self):
        """Check that the SlotW24 object is correct

        Parameters
        ----------
        self : SlotW24
            A SlotW24 object

        Returns
        -------
        None

        Raises
        -------
        S24_W3CheckError
            The teeth are too wide, reduce Zs or W3
        S24_HWCheckError
            The teeth are too wide, reduce Zs, H2 or W3
        """
        Rbo = self.get_Rbo()

        if 2 * np.arcsin(self.W3 / (2 * Rbo)) > 2 * np.pi / self.Zs:
            raise S24_W3CheckError("The teeth are too wide, reduce Zs or W3")

        if (
            not self.is_outwards()
            and 2 * np.arcsin(self.W3 / (2 * Rbo - self.H2)) > 2 * np.pi / self.Zs
        ):
            raise S24_HWCheckError("The teeth are too wide, reduce Zs, H2 or W3")

    # Inlined from Methods.Slot.SlotW24.comp_angle_opening
    def comp_angle_opening(self) -> float:
        """Compute the average opening angle of the Slot

        Parameters
        ----------
        self : SlotW24
            A SlotW24 object

        Returns
        -------
        alpha: float
            Average opening angle of the slot [rad]

        """

        alpha = float(np.arcsin(self.W3 / (2 * self.get_Rbo())))
        return 2 * np.pi / self.Zs - 2 * alpha

    # Inlined from Methods.Slot.SlotW24.comp_height
    def comp_height(self) -> float:
        """Compute the height of the Slot.
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotW24
            A SlotW24 object

        Returns
        -------
        Htot: float
            Height of the slot [m]

        """

        return self.comp_height_active()

    # Inlined from Methods.Slot.SlotW24.comp_height_active
    def comp_height_active(self) -> float:
        """Compute the height of the winding area

        Parameters
        ----------
        self : SlotW24
            A SlotW24 object

        Returns
        -------
        Hwind: float
            Height of the winding area [m]

        """

        point_dict = self._comp_point_coordinate()
        Rbo = self.get_Rbo()
        return abs(Rbo - abs(point_dict["Z2"]))

    # Inlined from Methods.Slot.SlotW24.comp_surface
    def comp_surface(self) -> float:
        """Compute the Slot total surface (by analytical computation).
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotW24
            A SlotW24 object

        Returns
        -------
        S: float
            Slot total surface [m**2]

        """

        return self.comp_surface_active()

    # Inlined from Methods.Slot.SlotW24.comp_surface_active
    def comp_surface_active(self) -> float:
        """Compute the Slot inner surface for winding (by analytical computation)

        Parameters
        ----------
        self : SlotW24
            A SlotW24 object

        Returns
        -------
        Swind: float
            Slot inner surface for winding [m**2]

        """

        Rbo = self.get_Rbo()
        point_dict = self._comp_point_coordinate()

        if self.is_outwards():
            Rint = Rbo
            Rext = abs(point_dict["Z2"])
        else:
            Rint = abs(point_dict["Z2"])
            Rext = Rbo

        # Surface of a slot pitch
        Sring = (np.pi * Rext**2 - np.pi * Rint**2) * 1 / self.Zs

        # Tooth surface
        St = self.H2 * self.W3

        alpha_bore = 2 * np.arcsin(self.W3 / (2 * Rint))
        Sarc_bore = (Rint**2.0) / 2.0 * (alpha_bore - np.sin(alpha_bore))

        alpha_yoke = 2 * np.arcsin(self.W3 / (2 * Rext))
        Sarc_yoke = (Rext**2.0) / 2.0 * (alpha_yoke - np.sin(alpha_yoke))

        if self.is_outwards():
            return Sring - (St + Sarc_yoke - Sarc_bore)
        else:
            return Sring - (St + Sarc_yoke - Sarc_bore)

    # Inlined from Methods.Slot.SlotW24.comp_surface_opening
    def comp_surface_opening(self) -> float:
        """Compute the Slot opening surface (by analytical computation).
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotW24
            A SlotW24 object

        Returns
        -------
        S: float
            Slot opening surface [m**2]

        """

        return 0

    # Inlined from Methods.Slot.SlotW24.get_surface_active
    def get_surface_active(self, alpha: float = 0, delta: complex = 0) -> Surface:
        """Return the full winding surface

        Parameters
        ----------
        self : SlotW24
            A SlotW24 object
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
        curve_list: list[Line] = [
            line_dict["1-2"],
            line_dict["2-3"],
            line_dict["3-4"],
            line_dict["4-1"],
        ]
        curve_list = [line for line in curve_list if line is not None]

        # Only the closing arc (4-1) needs to be drawn (in FEMM)
        for curve in curve_list[:-1]:
            if curve.prop_dict is None:
                curve.prop_dict = {}
            curve.prop_dict.update({DRAW_PROP_LAB: False})

        # Create surface
        if self.is_outwards():
            Zmid = self.get_Rbo() + self.H2 / 2
        else:
            Zmid = self.get_Rbo() - self.H2 / 2
        label = self.parent.get_label() + "_" + WIND_LAB + "_R0-T0-S0"
        surface = SurfLine(line_list=curve_list, label=label, point_ref=Zmid)

        # Apply transformation
        surface.rotate(alpha)
        surface.translate(delta)

        return surface

    # Inlined from Methods.Slot.SlotW24.get_surface_opening
    def get_surface_opening(self, alpha: float = 0, delta: complex = 0) -> list:
        """Return the list of surfaces defining the opening area of the Slot

        Parameters
        ----------
        self : SlotW24
            A SlotW24 object
        alpha : float
            float number for rotation (Default value = 0) [rad]
        delta : complex
            complex number for translation (Default value = 0)

        Returns
        -------
        surf_list : list
            list of surfaces objects
        """

        # No opening surface in SlotW14
        return []

    # Inlined from Methods.Slot.SlotW24.plot_schematics
    def plot_schematics(
        self,
        is_default: bool = False,
        is_return_default: bool = False,
        is_add_point_label: bool = False,
        is_add_schematics: bool = True,
        is_add_main_line: bool = True,
        type_add_active: int = 1,
        save_path: str | None = None,
        is_show_fig: bool = True,
        fig: Figure | None = None,
        ax: Axes | None = None,
    ) -> tuple[Figure, Axes] | Lamination:
        """Plot the schematics of the slot

        Parameters
        ----------
        self : SlotW24
            A SlotW24 object
        is_default : bool
            True: plot default schematics, else use current slot values
        is_return_default : bool
            True: return the default lamination used for the schematics (skip plot
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
            slot = type(self)(Zs=24, W3=20e-3, H2=60e-3)
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
                # H2
                line = Segment(begin=point_dict["Z3"], end=point_dict["Z4"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="H2",
                    offset_label=1j * self.W3 * 0.25,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # W3
                line = Segment(
                    begin=(point_dict["Z1"] + point_dict["Z2"]) / 2,
                    end=(point_dict["Z3"] + point_dict["Z4"]) / 2 * np.exp(-1j * sp),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    label="W3",
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    offset_label=self.W3 * 0.25,
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
                    end=point_dict["Z4"],
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
                # Bot arc
                R = abs(point_dict["Z2"])
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
                line = Segment(begin=0, end=lam.Rext * 1.5 * np.exp(-1j * sp / 2))
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                line = Segment(begin=0, end=lam.Rext * 1.5 * np.exp(1j * sp / 2))
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
            W = (point_dict["Z2"] * np.exp(1j * sp)).imag * 1.2
            Rint = min(point_dict["Z2"].real, point_dict["Z1"].real)
            Rext = max(point_dict["Z2"].real, point_dict["Z1"].real)

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
