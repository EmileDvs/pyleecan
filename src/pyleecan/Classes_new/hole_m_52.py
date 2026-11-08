# Experimental dataclass generated from Generator/ClassesRef/Slot/HoleM52.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass
from typing import ClassVar

import matplotlib.pyplot as plt
import numpy as np

from ..definitions import config_dict
from ..Functions.labels import HOLEM_LAB
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
from ._error import ParentMissingError, SlotCheckError
from .hole_mag import HoleMag
from .lam_hole import LamHole
from .magnet import Magnet
from .segment import Segment
from .surf_line import SurfLine


@dataclass(eq=False)
class HoleM52(HoleMag):
    """V shape slot for buried magnet

    Attributes
    ----------
    H0 : float
        Slot depth
        Unit: m; Default: 0.003; Minimum: 0
    W0 : float
        Magnet width
        Unit: m; Default: 0.003; Minimum: 0
    H1 : float
        Magnet height
        Unit: m; Default: 0; Minimum: 0
    W3 : float
        Tooth width
        Unit: m; Default: 0.013; Minimum: 0
    H2 : float
        Additional depth for the magnet
        Unit: m; Default: 0.02; Minimum: 0
    magnet_0 : Magnet or None
        Magnet of the hole
        Default: None
    """

    IS_SYMMETRICAL: ClassVar = 1
    MAGNET_COLOR = config_dict["PLOT"]["COLOR_DICT"]["MAGNET_COLOR"]
    H0: float = 0.003
    """Slot depth"""
    W0: float = 0.003
    """Magnet width"""
    H1: float = 0
    """Magnet height"""
    W3: float = 0.013
    """Tooth width"""
    H2: float = 0.02
    """Additional depth for the magnet"""
    magnet_0: Magnet | None = None
    """Magnet of the hole"""

    # Inlined from Methods.Slot.HoleM52._comp_point_coordinate
    def _comp_point_coordinate(self):
        """Compute the point coordinates needed to plot the Slot.

        Parameters
        ----------
        self : HoleM52
            A HoleM52 object

        Returns
        -------
        point_dict: dict
            A dict of the slot coordinates
        """

        Rext = self.get_Rext()

        alpha1 = self.comp_alpha()
        Z1 = (Rext - self.H0) * np.exp(1j * alpha1 / 2)
        Z9 = (Rext - self.H0) * np.exp(-1j * alpha1 / 2)

        Z0 = (Z1 + Z9) / 2
        Z5 = Z0 - self.H1

        Z4 = Z5 + 1j * self.W0 / 2
        Z6 = Z4.conjugate()

        Z3 = Z4 + self.H2
        Z7 = Z3.conjugate()

        W1 = self.comp_W1()
        Z2 = Z3 + 1j * W1
        Z8 = Z2.conjugate()

        Z11 = Z3 + (self.H1 - self.H2)
        Z10 = Z7 + (self.H1 - self.H2)

        point_dict = {}
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

        return point_dict

    # Inlined from Methods.Slot.HoleM52.build_geometry
    def build_geometry(self, alpha=0, delta=0, is_simplified=False):
        """Compute the curve (Line) needed to plot the Slot.
        The ending point of a curve is the starting point of the next curve in
        the list

        Parameters
        ----------
        self : HoleM52
            A HoleM52 object
        alpha : float
            Angle to rotate the slot (Default value = 0) [rad]
        delta : complex
            Complex to translate the slot (Default value = 0)
        is_simplified : bool
           True to avoid line superposition

        Returns
        -------
        surf_list: list
            List of SurfLine needed to draw the HoleM51

        """
        # Get correct label for surfaces
        lam_label = self.parent.get_label()
        R_id, surf_type = self.get_R_id()
        vent_label = lam_label + "_" + surf_type + "_R" + str(R_id) + "-"
        mag_label = lam_label + "_" + HOLEM_LAB + "_R" + str(R_id) + "-"

        point_dict = self._comp_point_coordinate()
        Z1 = point_dict["Z1"]
        Z2 = point_dict["Z2"]
        Z3 = point_dict["Z3"]
        Z4 = point_dict["Z4"]
        Z6 = point_dict["Z6"]
        Z7 = point_dict["Z7"]
        Z8 = point_dict["Z8"]
        Z9 = point_dict["Z9"]
        Z10 = point_dict["Z10"]
        Z11 = point_dict["Z11"]

        # Creation of the air curve
        curve_list = []
        curve_list.append(Segment(Z1, Z2))
        curve_list.append(Segment(Z2, Z3))
        curve_list.append(Segment(Z3, Z11))
        curve_list.append(Segment(Z11, Z1))
        point_ref = (Z1 + Z2 + Z3 + Z11) / 4
        S1 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # Creation of the magnet curve
        curve_list = []
        if is_simplified:
            curve_list.append(Segment(Z3, Z11))
            curve_list.append(Segment(Z7, Z10))
        else:
            curve_list.append(Segment(Z4, Z11))
            curve_list.append(Segment(Z11, Z10))
            curve_list.append(Segment(Z10, Z6))
            curve_list.append(Segment(Z6, Z4))
        point_ref = (Z11 + Z4 + Z6 + Z10) / 4
        S2 = SurfLine(
            line_list=curve_list, label=mag_label + "T0-S0", point_ref=point_ref
        )

        # Creation of the second air curve
        curve_list = []
        curve_list.append(Segment(Z7, Z8))
        curve_list.append(Segment(Z8, Z9))
        curve_list.append(Segment(Z9, Z10))
        curve_list.append(Segment(Z10, Z7))
        point_ref = (Z7 + Z8 + Z9 + Z10) / 4
        S3 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # Area with no magnet (S1 + S2 + S3)
        curve_list = []
        curve_list.append(Segment(Z1, Z2))
        curve_list.append(Segment(Z2, Z3))
        if self.H2 > 0:
            curve_list.append(Segment(Z3, Z4))
        curve_list.append(Segment(Z4, Z6))
        if self.H2 > 0:
            curve_list.append(Segment(Z6, Z7))
        curve_list.append(Segment(Z7, Z8))
        curve_list.append(Segment(Z8, Z9))
        curve_list.append(Segment(Z9, Z1))
        point_ref = (Z11 + Z4 + Z6 + Z10) / 4
        S4 = SurfLine(line_list=curve_list, point_ref=point_ref)

        if self.magnet_0:
            S1.label = vent_label + "T0-S0"  # Hole
            S3.label = vent_label + "T1-S0"  # Hole
            surf_list = [S1, S2, S3]
        else:
            S4.label = vent_label + "T0-S0"  # Hole
            surf_list = [S4]

        # Apply the transformations
        for surf in surf_list:
            surf.rotate(alpha)
            surf.translate(delta)

        return surf_list

    # Inlined from Methods.Slot.HoleM52.check
    def check(self):
        """Check that the HoleM52 object is correct

        Parameters
        ----------
        self : HoleM52
            A HoleM52 object

        Returns
        -------
        None

        Raises
        -------
        S52_H12CheckError
            You must have H2 < H1
        S52_alphaCheckError
            The teeth are too wide for the lamination (reduce W3 or H0)
        S52_W1CheckError
            W1 is <=0, you must reduce W0 or W3
        """

        # Check that everything is set
        if self.W0 is None:
            raise self.S52_NoneError("You must set W0 !")
        elif self.W3 is None:
            raise self.S52_NoneError("You must set W3 !")
        elif self.H0 is None:
            raise self.S52_NoneError("You must set H0 !")
        elif self.H1 is None:
            raise self.S52_NoneError("You must set H1 !")
        elif self.H2 is None:
            raise self.S52_NoneError("You must set H2 !")

        if self.H2 >= self.H1:
            raise self.S52_H12CheckError("You must have H2 < H1")

        alpha = self.comp_alpha()
        if alpha <= 0:
            raise self.S52_alphaCheckError(
                "The teeth are too wide for the lamination (reduce W3 or H0)"
            )

        W1 = self.comp_W1()
        if W1 <= 0:
            raise self.S52_W1CheckError("W1 is <=0, you must reduce W0 or W3")

    # Inlined from Methods.Slot.HoleM52.comp_alpha
    def comp_alpha(self):
        """The opening angle with a W3 teeth width and Rext - H0 radius

        Parameters
        ----------
        self : HoleM52
            A HoleM52 object

        Returns
        -------
        alpha: float
            Angle between P1 and P9 (cf schematics) [rad]

        """
        Rext = self.get_Rext()

        alpha_tooth = 2 * np.arcsin(self.W3 / (2 * (Rext - self.H0)))
        slot_pitch = 2 * np.pi / self.Zh

        return slot_pitch - alpha_tooth

    # Inlined from Methods.Slot.HoleM52.comp_magnetization_dict
    def comp_magnetization_dict(self, is_north=True):
        """Compute the dictionary of the magnetization direction of the magnets (key=magnet_X, value=angle[rad])
        Mangetization angle with Hole centered on Ox axis

        Parameters
        ----------
        self : HoleM52
            a HoleM52 object
        is_north: True
            True: comp north magnetization, else add pi [rad]

        Returns
        -------
        mag_dict: dict
            magnetization dictionary (key=magnet_X, value=angle[rad])
        """

        # Comp magnet
        point_dict = self._comp_point_coordinate()

        mag_dict = {}
        S0 = Segment(point_dict["Z4"], point_dict["Z6"])
        mag_dict["magnet_0"] = S0.comp_normal()

        if not is_north:
            mag_dict["magnet_0"] += np.pi

        if self.magnetization_dict_offset is not None:
            for key, value in self.magnetization_dict_offset:
                mag_dict[key] += value

        return mag_dict

    # Inlined from Methods.Slot.HoleM52.comp_radius
    def comp_radius(self):
        """Compute the radius of the min and max circle that contains the hole

        Parameters
        ----------
        self : HoleM52
            A HoleM52 object

        Returns
        -------
        (Rmin,Rmax): tuple
            Radius of the circle that contains the hole [m]

        """

        Rext = self.get_Rext()

        Rmax = Rext - self.H0

        alpha = self.comp_alpha()
        Z1 = (Rext - self.H0) * np.exp(1j * alpha / 2)
        Z5 = Z1.real - self.H1
        Rmin = abs(Z5)

        return (Rmin, Rmax)

    # Inlined from Methods.Slot.HoleM52.comp_surface
    def comp_surface(self):
        """Compute the surface of the Hole

        Parameters
        ----------
        self : HoleM52
            A HoleM52 object

        Returns
        -------
        S: float
            Surface of the Hole. [m**2]

        """

        Rext = self.get_Rext()

        alpha = self.comp_alpha()

        # Angle between (P1,P2) and (0,P0) is slot_pitch /2
        # It is also the angle (P1,P2,S)
        hsp = np.pi / self.Zh  # Half Slot Pitch

        # Distance P1,P9
        D19 = ((Rext - self.H0) * np.exp(1j * alpha / 2)).imag * 2

        # S is the intersectioni between (P1,P9) and the parallel to x passing by P2
        D1S = np.tan(hsp) * (self.H1 - self.H2)

        W1 = D19 / 2.0 - D1S - self.W0 / 2.0

        Smag = self.comp_surface_magnets()
        # Two air trapeze area
        Strap = ((D19 / 2.0 - self.W0 / 2.0) + W1) * (self.H1 - self.H2)

        return Smag + Strap

    # Inlined from Methods.Slot.HoleM52.comp_surface_magnet_id
    def comp_surface_magnet_id(self, index):
        """Compute the surface of the hole magnet of the corresponding index

        Parameters
        ----------
        self : HoleM52
            A HoleM52 object
        index : int
            Index of the magnet to compute the surface

        Returns
        -------
        Smag: float
            Surface of the Magnet [m**2]
        """

        if index == 0 and self.magnet_0:
            return self.W0 * self.H1
        return 0

    # Inlined from Methods.Slot.HoleM52.comp_W1
    def comp_W1(self):
        """Compute W1 (cf schematics)

        Parameters
        ----------
        self : HoleM52
            A HoleM52 object

        Returns
        -------
        W1: float
            cf schematics [m]

        """

        Rext = self.get_Rext()

        alpha = self.comp_alpha()

        # Angle between (P1,P2) and (0,P0) is slot_pitch /2
        # It is also the angle (P1,P2,S)
        hsp = np.pi / self.Zh  # Half Slot Pitch

        # Distance P1,P9
        D19 = ((Rext - self.H0) * np.exp(1j * alpha / 2)).imag * 2

        # S is the intersectioni between (P1,P9) and the parallel to x passing by P2
        D1S = np.tan(hsp) * (self.H1 - self.H2)

        return D19 / 2.0 - D1S - self.W0 / 2.0

    # Inlined from Methods.Slot.HoleM52.has_magnet
    def has_magnet(self):
        """Return if the Hole has magnets

        Parameters
        ----------
        self : HoleM52
            A HoleM52 object

        Returns
        -------
        has_magnet : bool
            True if the magnets are not None
        """

        return self.magnet_0 is not None

    # Inlined from Methods.Slot.HoleM52.plot_schematics
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
        self : HoleM51
            A HoleM51 object
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
            Figure containing the schematics
        ax : Matplotlib.axes.Axes object
            Axis containing the schematics
        -------
        lam : LamHole / LamSlot
            Default lamination used for the schematic
        """

        # Use some default parameter
        if is_default:
            hole = type(self)(Zh=10, W0=27e-3, W3=5e-3, H0=3e-3, H1=7e-3, H2=3e-3)
            lam = LamHole(
                Rint=45e-3 / 2,
                Rext=81.5e-3,
                is_internal=True,
                is_stator=False,
                hole=[hole],
            )
            if is_return_default:
                return lam
            else:
                return hole.plot_schematics(
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
        elif type_add_active == 0:
            # Remove magnets
            lam = self.parent.copy()
            lam.hole[0].remove_magnet()
            return lam.hole[0].plot_schematics(
                is_default=False,
                is_add_point_label=is_add_point_label,
                is_add_schematics=is_add_schematics,
                is_add_main_line=is_add_main_line,
                type_add_active=2,
                save_path=save_path,
                is_show_fig=is_show_fig,
                fig=fig,
                ax=ax,
            )
        else:
            # Getting the main plot
            if self.parent is None:
                raise ParentMissingError("Error: The hole is not inside a Lamination")
            lam = self.parent
            alpha = np.pi / 2  # To rotate the schematics
            fig, ax = lam.plot(
                alpha=np.pi / self.Zh + alpha,
                is_show_fig=False,
                is_lam_only=type_add_active == 0,
                fig=fig,
                ax=ax,
            )  # center hole on Ox axis
            sp = 2 * np.pi / self.Zh
            Rbo = self.get_Rbo()
            point_dict = self._comp_point_coordinate()

            # Adding point label
            if is_add_point_label:
                for name, Z in point_dict.items():
                    Z = Z * np.exp(1j * alpha)
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
                Zlim1 = point_dict["Z4"] - self.H2 * 0.4
                Zlim2 = point_dict["Z6"] - self.H2 * 0.4
                plot_quote(
                    point_dict["Z4"] * np.exp(1j * alpha),
                    Zlim1 * np.exp(1j * alpha),
                    Zlim2 * np.exp(1j * alpha),
                    point_dict["Z6"] * np.exp(1j * alpha),
                    offset_label=-1j * self.H2 * 0.7,
                    fig=fig,
                    ax=ax,
                    label="W0",
                )
                # W3
                line = Segment(
                    (point_dict["Z2"] + point_dict["Z1"]) / 2 * np.exp(1j * alpha),
                    (point_dict["Z9"] + point_dict["Z8"])
                    / 2
                    * np.exp(1j * sp)
                    * np.exp(1j * alpha),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="W3",
                    offset_label=-1j * self.H2 * 0.7,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # H0
                line = Segment(
                    point_dict["Z9"] * np.exp(1j * alpha),
                    Rbo * np.exp(1j * np.angle(point_dict["Z9"])) * np.exp(1j * alpha),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="H0",
                    offset_label=self.H2 * 0.5,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # H1
                line = Segment(
                    point_dict["Z11"] * np.exp(1j * alpha),
                    point_dict["Z4"] * np.exp(1j * alpha),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="H1",
                    offset_label=self.H2 * 0.3,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # H2
                line = Segment(
                    point_dict["Z7"] * np.exp(1j * alpha),
                    point_dict["Z6"] * np.exp(1j * alpha),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="H2",
                    offset_label=(1 - 1j) * self.H2 * 0.3,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )

            if is_add_main_line:
                # Ox axis
                line = Segment(0, lam.Rext * 1.5 * np.exp(1j * alpha))
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # Tooth axis
                line = Segment(
                    0, lam.Rext * 1.5 * np.exp(1j * sp / 2) * np.exp(1j * alpha)
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                line = Segment(
                    0, lam.Rext * 1.5 * np.exp(-1j * sp / 2) * np.exp(1j * alpha)
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # H0 lines
                line = Segment(
                    0,
                    abs(point_dict["Z9"])
                    * 1.5
                    * np.exp(1j * np.angle(point_dict["Z9"]))
                    * np.exp(1j * alpha),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # W3 lines
                line = Segment(
                    point_dict["Z1"] * np.exp(1j * alpha),
                    point_dict["Z9"] * np.exp(1j * sp) * np.exp(1j * alpha),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                line = Segment(
                    point_dict["Z2"] * np.exp(1j * alpha),
                    point_dict["Z8"] * np.exp(1j * sp) * np.exp(1j * alpha),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # Magnet line
                line = Segment(
                    point_dict["Z3"] * np.exp(1j * alpha),
                    point_dict["Z7"] * np.exp(1j * alpha),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )

            # Zooming and cleaning
            W = (
                -1
                * (point_dict["Z9"] * np.exp(1j * sp) * np.exp(1j * alpha)).real
                * 1.2
            )
            Rint = (point_dict["Z5"] * np.exp(1j * alpha)).imag * 0.9
            Rext = self.parent.Rext * 1.1

            ax.axis("equal")
            ax.set_ylim(Rint, Rext)
            ax.set_xlim(-W, W)
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

    # Inlined from Methods.Slot.HoleM52.remove_magnet
    def remove_magnet(self):
        """Remove the magnet (set to None) of the Hole

        Parameters
        ----------
        self : HoleM52
            a HoleM52 object
        """

        self.magnet_0 = None

    class S52_H12CheckError(SlotCheckError):
        """ """

    class S52_NoneError(SlotCheckError):
        """Raised when a propery of HoleM52 is None"""

    class S52_W1CheckError(SlotCheckError):
        """ """

    class S52_alphaCheckError(SlotCheckError):
        """ """
