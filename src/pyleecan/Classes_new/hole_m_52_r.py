# Experimental dataclass generated from Generator/ClassesRef/Slot/HoleM52R.csv
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
from . import ParentMissingError
from .arc_1 import Arc1
from .hole_mag import HoleMag
from .lam_hole import LamHole
from .magnet import Magnet
from .segment import Segment
from .surf_line import SurfLine


@dataclass(eq=False)
class HoleM52R(HoleMag):
    """Rectangular slot for buried magnet

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
    W1 : float
        Void width
        Unit: m; Default: 0.001; Minimum: 0
    H2 : float
        Additional depth for the magnet
        Unit: m; Default: 0.02; Minimum: 0
    magnet_0 : Magnet or None
        Magnet of the hole
        Default: None
    R0 : float
        Void corner radius
        Unit: m; Default: 0; Minimum: 0
    """

    IS_SYMMETRICAL: ClassVar = 1
    MAGNET_COLOR = config_dict["PLOT"]["COLOR_DICT"]["MAGNET_COLOR"]
    H0: float = 0.003
    """Slot depth"""
    W0: float = 0.003
    """Magnet width"""
    H1: float = 0
    """Magnet height"""
    W1: float = 0.001
    """Void width"""
    H2: float = 0.02
    """Additional depth for the magnet"""
    magnet_0: Magnet | None = None
    """Magnet of the hole"""
    R0: float = 0
    """Void corner radius"""

    # Inlined from Methods.Slot.HoleM52R._comp_point_coordinate
    def _comp_point_coordinate(self):
        """Compute the point coordinates needed to plot the Slot.

        Parameters
        ----------
        self : HoleM52R
            A HoleM52R object

        Returns
        -------
        point_dict: dict
            A dict of the slot coordinates
        """

        Rext = self.get_Rext()

        alpha1 = self.comp_alpha()
        Z1 = (Rext - self.H0) * np.exp(1j * alpha1 / 2)  # top corner of void
        Z9 = (Rext - self.H0) * np.exp(-1j * alpha1 / 2)

        Z0 = (Z1 + Z9) / 2  # middle of magnet at top
        Z5 = Z0 - self.H1  # middle of magnet at bottom

        Z4 = Z5 + 1j * self.W0 / 2  # bottom corner of magnet hole
        Z6 = Z4.conjugate()

        Z3 = Z4 + self.H2
        Z7 = Z3.conjugate()

        Z2 = Z3 + 1j * self.W1  # bottom corner of void
        Z8 = Z2.conjugate()

        Z11 = Z3 + (self.H1 - self.H2)  # top corner of magnet
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

    # Inlined from Methods.Slot.HoleM52R.build_geometry
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

        # modify points for void radius in case
        is_radius = False
        if self.R0 > 0:
            if self.R0 < (self.H1 - self.H2) and self.R0 < self.W1:
                is_radius = True
                Z1R = Z1 - 1j * self.R0
                Z1L = Z1 - self.R0
                Z9L = Z9 + 1j * self.R0
                Z9R = Z9 - self.R0

            else:
                self.get_logger().warning("Radius R0 enforced to 0.")

        # Creation of the air curve
        curve_list = []
        if is_radius:
            curve_list.append(Arc1(Z1R, Z1L, self.R0))
        curve_list.append(Segment(Z1L if is_radius else Z1, Z2))
        curve_list.append(Segment(Z2, Z3))
        curve_list.append(Segment(Z3, Z11))
        curve_list.append(Segment(Z11, Z1R if is_radius else Z1))
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
        curve_list.append(Segment(Z8, Z9R if is_radius else Z9))
        if is_radius:
            curve_list.append(Arc1(Z9R, Z9L, self.R0))
        curve_list.append(Segment(Z9L if is_radius else Z9, Z10))
        curve_list.append(Segment(Z10, Z7))
        point_ref = (Z7 + Z8 + Z9 + Z10) / 4
        S3 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # Area with no magnet (S1 + S2 + S3)
        curve_list = []
        if is_radius:
            curve_list.append(Arc1(Z1R, Z1L, self.R0))
        curve_list.append(Segment(Z1L if is_radius else Z1, Z2))
        curve_list.append(Segment(Z2, Z3))
        if self.H2 > 0:
            curve_list.append(Segment(Z3, Z4))
        curve_list.append(Segment(Z4, Z6))
        if self.H2 > 0:
            curve_list.append(Segment(Z6, Z7))
        curve_list.append(Segment(Z7, Z8))
        curve_list.append(Segment(Z8, Z9R if is_radius else Z9))
        if is_radius:
            curve_list.append(Arc1(Z9R, Z9L, self.R0))
        curve_list.append(Segment(Z9L if is_radius else Z9, Z1R if is_radius else Z1))
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

    # Inlined from Methods.Slot.HoleM52R.check
    def check(self):
        """Check that the HoleM52 object is correct

        Parameters
        ----------
        self : HoleM52R
            A HoleM52R object

        Returns
        -------
        None

        Raises
        -------
        S52R_H12CheckError
            You must have H2 < H1
        S52R_alphaCheckError
            The teeth are too wide for the lamination (reduce W3 or H0)
        S52R_W1CheckError
            W1 is <=0, you must reduce W0 or W3
        """

        # Check that everything is set
        if self.W0 is None:
            raise S52R_NoneError("You must set W0 !")
        elif self.W1 is None:
            raise S52R_NoneError("You must set W1 !")
        elif self.H0 is None:
            raise S52R_NoneError("You must set H0 !")
        elif self.H1 is None:
            raise S52R_NoneError("You must set H1 !")
        elif self.H2 is None:
            raise S52R_NoneError("You must set H2 !")
        elif self.R0 is None:
            raise S52R_NoneError("You must set R0 !")

        if self.H2 >= self.H1:
            raise S52R_H12CheckError("You must have H2 < H1")

        if self.R0 >= self.H1:
            raise S52R_R0CheckError("You must have R0 < H1")

        if self.R0 >= self.H1 - self.H2:
            raise S52R_R0CheckError("You must have R0 < H1")

        h = self.H1 - self.H2
        w = self.W0 + self.W1
        Z2 = np.sqrt((self.get_Rext() - self.H0) ** 2 - h**2) - h + 1j * w / 2

        if np.angle(Z2) >= np.pi / self.Zh:
            raise S52R_widthCheckError(
                "The hole is too wide for the lamination (reduce W1, H0 or W0)"
            )

    # Inlined from Methods.Slot.HoleM52R.comp_alpha
    def comp_alpha(self):
        """The opening angle incl. W1 width and a Rext - H0 radius

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

        alpha = 2 * np.arcsin((2 * self.W1 + self.W0) / (2 * (Rext - self.H0)))

        return alpha

    # Inlined from Methods.Slot.HoleM52R.comp_magnetization_dict
    def comp_magnetization_dict(self, is_north=True):
        """Compute the dictionary of the magnetization direction of the magnets (key=magnet_X, value=angle[rad])
        Mangetization angle with Hole centered on Ox axis

        Parameters
        ----------
        self : HoleM52R
            a HoleM52R object
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

    # Inlined from Methods.Slot.HoleM52R.comp_radius
    def comp_radius(self):
        """Compute the radius of the min and max circle that contains the hole

        Parameters
        ----------
        self : HoleM52
            A HoleM52R object

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

    # Inlined from Methods.Slot.HoleM52R.comp_surface
    def comp_surface(self):
        """Compute the surface of the Hole

        Parameters
        ----------
        self : HoleM52R
            A HoleM52R object

        Returns
        -------
        S: float
            Surface of the Hole. [m**2]

        """

        Smag = self.comp_surface_magnets()
        # one side rectangular air area
        Srect = self.W1 * (self.H1 - self.H2) - (4 - np.pi) * self.R0**2 / 4

        return Smag + 2 * Srect

    # Inlined from Methods.Slot.HoleM52R.comp_surface_magnet_id
    def comp_surface_magnet_id(self, index):
        """Compute the surface of the hole magnet of the corresponding index

        Parameters
        ----------
        self : HoleM52R
            A HoleM52R object
        index : int
            Index of the magnet to compute the surface

        Returns
        -------
        Smag: float
            Surface of the Magnet [m**2]
        """
        return self.W0 * self.H1 if index == 0 and self.magnet_0 else 0

    # Inlined from Methods.Slot.HoleM52R.get_height_magnet_id
    def get_height_magnet_id(self, index):
        """Get the height of the hole magnet of the corresponding index

        Parameters
        ----------
        self : HoleM52R
            A HoleM52R object
        index : int
            Index of the magnet to get the height

        Returns
        -------
        Hmag: float
            Height of the Magnet [m]
        """

        if index == 0 and self.magnet_0:
            return self.H1
        return 0

    # Inlined from Methods.Slot.HoleM52R.has_magnet
    def has_magnet(self):
        """Return if the Hole has magnets

        Parameters
        ----------
        self : HoleM52R
            A HoleM52R object

        Returns
        -------
        has_magnet : bool
            True if the magnets are not None
        """

        return self.magnet_0 is not None

    # Inlined from Methods.Slot.HoleM52R.plot_schematics
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

        Returns
        -------
        fig : Matplotlib.figure.Figure
            Figure containing the schematics
        ax : Matplotlib.axes.Axes object
            Axis containing the schematics
        -------
        lam : LamHole / LamSlot
            Default lamination used for the schematics
        """

        # Use some default parameter
        if is_default:
            hole = type(self)(
                Zh=10, W0=27e-3, W1=5e-3, H0=3e-3, H1=8e-3, H2=3e-3, R0=2e-3
            )
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
                hole.plot_schematics(
                    is_default=False,
                    is_return_default=False,
                    is_add_point_label=is_add_point_label,
                    is_add_schematics=is_add_schematics,
                    is_add_main_line=is_add_main_line,
                    type_add_active=type_add_active,
                    save_path=save_path,
                    is_show_fig=is_show_fig,
                )
        elif type_add_active == 0:
            # Remove magnets
            lam = self.parent.copy()
            lam.hole[0].remove_magnet()
            lam.hole[0].plot_schematics(
                is_default=False,
                is_add_point_label=is_add_point_label,
                is_add_schematics=is_add_schematics,
                is_add_main_line=is_add_main_line,
                type_add_active=2,
                save_path=save_path,
                is_show_fig=is_show_fig,
            )
        else:
            # Getting the main plot
            if self.parent is None:
                raise ParentMissingError("Error: The hole is not inside a Lamination")
            lam = self.parent
            alpha = np.pi / 2  # To rotate the schematics
            lam.plot(
                alpha=np.pi / self.Zh + alpha,
                is_show_fig=False,
                is_lam_only=type_add_active == 0,
            )  # center hole on Ox axis
            sp = 2 * np.pi / self.Zh
            Rbo = self.get_Rbo()
            fig = plt.gcf()
            ax = plt.gca()
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
                # W1
                line = Segment(
                    point_dict["Z2"] * np.exp(1j * alpha),
                    point_dict["Z3"] * np.exp(1j * alpha),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="W1",
                    offset_label=-self.W1 * 0.5 - 1j * self.H2 * 0.7,
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
                # R0
                line = Segment(
                    (point_dict["Z9"] + (1j - 1) * self.R0) * np.exp(1j * alpha),
                    (point_dict["Z9"] + 1j * self.R0) * np.exp(1j * alpha),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="R0",
                    offset_label=-self.W1,
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
                # H0 radius
                R = Rbo - self.H0
                rot_N = 1
                rot_P = np.exp(1j * np.pi * 0.98)
                line = Arc1(
                    begin=R * rot_N, end=R * rot_P, radius=R, is_trigo_direction=True
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
                # H0 lines
                line = Segment(
                    point_dict["Z10"] * np.exp(1j * alpha),
                    point_dict["Z9"] * np.exp(1j * alpha),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                line = Segment(
                    point_dict["Z8"] * np.exp(1j * alpha),
                    point_dict["Z9"] * np.exp(1j * alpha),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                line = Segment(
                    point_dict["Z1"] * np.exp(1j * alpha),
                    point_dict["Z2"] * np.exp(1j * alpha),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                line = Segment(
                    point_dict["Z1"] * np.exp(1j * alpha),
                    point_dict["Z11"] * np.exp(1j * alpha),
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
                # R0 circle
                line = Arc1(
                    begin=(point_dict["Z9"] - self.R0) * np.exp(1j * alpha),
                    end=(point_dict["Z9"] + 1j * self.R0) * np.exp(1j * alpha),
                    radius=self.R0,
                    is_trigo_direction=False,
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

            plt.axis("equal")
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
                plt.close()

            if is_show_fig:
                fig.show()

    # Inlined from Methods.Slot.HoleM52R.remove_magnet
    def remove_magnet(self):
        """Remove the magnet (set to None) of the Hole

        Parameters
        ----------
        self : HoleM52R
            a HoleM52R object
        """

        self.magnet_0 = None

    class MachineCheckError(Exception):
        """ """

    class LaminationCheckError(MachineCheckError):
        """ """

    class SlotCheckError(LaminationCheckError):
        """ """

    class S52R_H12CheckError(SlotCheckError):
        """ """

    class S52R_widthCheckError(SlotCheckError):
        """ """

    class S52R_R0CheckError(SlotCheckError):
        """ """

    class S52R_NoneError(SlotCheckError):
        """Raised when a propery of HoleM52R is None"""


MachineCheckError = HoleM52R.MachineCheckError
LaminationCheckError = HoleM52R.LaminationCheckError
SlotCheckError = HoleM52R.SlotCheckError
S52R_H12CheckError = HoleM52R.S52R_H12CheckError
S52R_widthCheckError = HoleM52R.S52R_widthCheckError
S52R_R0CheckError = HoleM52R.S52R_R0CheckError
S52R_NoneError = HoleM52R.S52R_NoneError
