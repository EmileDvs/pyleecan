# Experimental dataclass generated from Generator/ClassesRef/Slot/HoleM58.csv
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
class HoleM58(HoleMag):
    """One magnet with circular notches

    Attributes
    ----------
    H0 : float
        Slot depth
        Unit: m; Default: 0.003; Minimum: 0
    W0 : float
        Slot width
        Unit: m; Default: 0.003; Minimum: 0
    H1 : float
        Distance from the lamination Bore
        Unit: m; Default: 0; Minimum: 0
    W1 : float
        Magnet width
        Unit: m; Default: 0.013; Minimum: 0
    H2 : float
        Magnet Height
        Unit: m; Default: 0.02; Minimum: 0
    W2 : float
        Distance Magnet to side of the notch
        Unit: m; Default: 0.01; Minimum: 0
    W3 : float
        Tooth angular opening width
        Unit: rad; Default: 0.01; Minimum: 0
    R0 : float
        Notch radius
        Unit: m; Default: 0.01; Minimum: 0
    magnet_0 : Magnet or None
        Magnet
        Default: None
    """

    IS_SYMMETRICAL: ClassVar = 1
    MAGNET_COLOR = config_dict["PLOT"]["COLOR_DICT"]["MAGNET_COLOR"]
    H0: float = 0.003
    """Slot depth"""
    W0: float = 0.003
    """Slot width"""
    H1: float = 0
    """Distance from the lamination Bore"""
    W1: float = 0.013
    """Magnet width"""
    H2: float = 0.02
    """Magnet Height"""
    W2: float = 0.01
    """Distance Magnet to side of the notch"""
    W3: float = 0.01
    """Tooth angular opening width"""
    R0: float = 0.01
    """Notch radius"""
    magnet_0: Magnet | None = None
    """Magnet"""

    # Inlined from Methods.Slot.HoleM58._comp_point_coordinate
    def _comp_point_coordinate(self):
        """Compute the point coordinates needed to plot the Slot.

        Parameters
        ----------
        self : HoleM53
            A HoleM53 object

        Returns
        -------
        point_dict: dict
            A dict of the slot coordinates
        """
        Rext = self.get_Rext()

        Z0 = Rext - self.H0
        Z2 = Z0 + 1j * (self.W0 / 2)
        Z1 = Z2 - 1j * self.W2
        Z12 = Z1 - 1j * self.W1
        Z11 = Z2 - 1j * self.W0
        Z5 = Z2 - self.H2
        Z6 = Z5 - 1j * self.W2
        Z7 = Z6 - 1j * self.W1
        Z8 = Z5 - 1j * self.W0

        Zc1 = (Rext - self.H1 - self.R0) * np.exp(1j * self.W3 / 2)

        # Z3 is the tangent point of the circle for (Z3,Z2)
        # (X3 - X2) * (X3 - Xc) + (Y3 - Y2) * (Y3 - Yc)
        # Z3 is on the circle
        # (X3 - Xc) ** 2 + (Y3 - Yc) ** 2 - R0 ** 2
        R0 = self.R0
        X2 = Z2.real
        Y2 = Z2.imag
        Xc = Zc1.real
        Yc = Zc1.imag
        # Solved with Sympy
        X3 = (
            R0**2 * X2
            - R0**2 * Xc
            - R0
            * Y2
            * np.sqrt(
                -(R0**2) + X2**2 - 2 * X2 * Xc + Xc**2 + Y2**2 - 2 * Y2 * Yc + Yc**2
            )
            + R0
            * Yc
            * np.sqrt(
                -(R0**2) + X2**2 - 2 * X2 * Xc + Xc**2 + Y2**2 - 2 * Y2 * Yc + Yc**2
            )
            + X2**2 * Xc
            - 2 * X2 * Xc**2
            + Xc**3
            + Xc * Y2**2
            - 2 * Xc * Y2 * Yc
            + Xc * Yc**2
        ) / (X2**2 - 2 * X2 * Xc + Xc**2 + Y2**2 - 2 * Y2 * Yc + Yc**2)
        Y3 = (
            R0**2 * Y2
            - R0**2 * Yc
            + R0
            * (X2 - Xc)
            * np.sqrt(
                -(R0**2) + X2**2 - 2 * X2 * Xc + Xc**2 + Y2**2 - 2 * Y2 * Yc + Yc**2
            )
            + X2**2 * Yc
            - 2 * X2 * Xc * Yc
            + Xc**2 * Yc
            + Y2**2 * Yc
            - 2 * Y2 * Yc**2
            + Yc**3
        ) / (X2**2 - 2 * X2 * Xc + Xc**2 + Y2**2 - 2 * Y2 * Yc + Yc**2)
        Z3 = X3 + 1j * Y3

        # Same for Z4
        X5 = Z5.real
        Y5 = Z5.imag
        X4 = (
            R0**2 * X5
            - R0**2 * Xc
            + R0
            * Y5
            * np.sqrt(
                -(R0**2) + X5**2 - 2 * X5 * Xc + Xc**2 + Y5**2 - 2 * Y5 * Yc + Yc**2
            )
            - R0
            * Yc
            * np.sqrt(
                -(R0**2) + X5**2 - 2 * X5 * Xc + Xc**2 + Y5**2 - 2 * Y5 * Yc + Yc**2
            )
            + X5**2 * Xc
            - 2 * X5 * Xc**2
            + Xc**3
            + Xc * Y5**2
            - 2 * Xc * Y5 * Yc
            + Xc * Yc**2
        ) / (X5**2 - 2 * X5 * Xc + Xc**2 + Y5**2 - 2 * Y5 * Yc + Yc**2)
        Y4 = (
            R0**2 * Y5
            - R0**2 * Yc
            - R0
            * (X5 - Xc)
            * np.sqrt(
                -(R0**2) + X5**2 - 2 * X5 * Xc + Xc**2 + Y5**2 - 2 * Y5 * Yc + Yc**2
            )
            + X5**2 * Yc
            - 2 * X5 * Xc * Yc
            + Xc**2 * Yc
            + Y5**2 * Yc
            - 2 * Y5 * Yc**2
            + Yc**3
        ) / (X5**2 - 2 * X5 * Xc + Xc**2 + Y5**2 - 2 * Y5 * Yc + Yc**2)
        Z4 = X4 + 1j * Y4

        Z9 = Z4.conjugate()
        Z10 = Z3.conjugate()
        Zc2 = Zc1.conjugate()

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
        point_dict["Z12"] = Z12
        point_dict["Zc1"] = Zc1
        point_dict["Zc2"] = Zc2

        return point_dict

    # Inlined from Methods.Slot.HoleM58.build_geometry
    def build_geometry(self, alpha=0, delta=0, is_simplified=False):
        """Compute the curve (Segment) needed to plot the Slot.
        The ending point of a curve is the starting point of the next curve in
        the list

        Parameters
        ----------
        self : HoleM58
            A HoleM58 object
        alpha : float
            Angle to rotate the slot (Default value = 0) [rad]
        delta : complex
            Complex to translate the slot (Default value = 0)
        is_simplified : bool
           True to avoid line superposition

        Returns
        -------
        surf_list: list
            List of SurfLine needed to draw the HoleM58

        """

        # Get correct label for surfaces
        lam_label = self.parent.get_label()
        R_id, surf_type = self.get_R_id()
        vent_label = lam_label + "_" + surf_type + "_R" + str(R_id) + "-"
        mag_label = lam_label + "_" + HOLEM_LAB + "_R" + str(R_id) + "-"

        Rext = self.get_Rext()
        R0 = self.R0

        # Get all the points
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
        Zc1 = point_dict["Zc1"]
        Zc2 = point_dict["Zc2"]

        surf_list = []

        surf_list = []
        # Create all the surfaces for all the cases
        # Air surface Zc1 with magnet_0
        curve_list = []
        if self.W2 > 0:
            curve_list.append(Segment(Z1, Z2))
        curve_list.append(Segment(Z2, Z3))
        curve_list.append(Arc1(begin=Z3, end=Z4, radius=R0, is_trigo_direction=True))
        curve_list.append(Segment(Z4, Z5))
        if self.W2 > 0:
            curve_list.append(Segment(Z5, Z6))
        curve_list.append(Segment(Z6, Z1))
        point_ref = Zc1
        S1 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # Magnet_0 surface
        curve_list = []
        curve_list.append(Segment(Z1, Z6))
        curve_list.append(Segment(Z6, Z7))
        curve_list.append(Segment(Z7, Z12))
        curve_list.append(Segment(Z12, Z1))
        point_ref = (Z1 + Z6 + Z7 + Z12) / 4

        S2 = SurfLine(
            line_list=curve_list, label=mag_label + "T0-S0", point_ref=point_ref
        )

        # Air surface Zc2 with magnet_0
        curve_list = []
        curve_list.append(Segment(Z12, Z7))
        if self.W2 + self.W1 < self.W0:
            curve_list.append(Segment(Z7, Z8))
        curve_list.append(Segment(Z8, Z9))
        curve_list.append(Arc1(begin=Z9, end=Z10, radius=R0, is_trigo_direction=True))
        curve_list.append(Segment(Z10, Z11))
        if self.W2 + self.W1 < self.W0:
            curve_list.append(Segment(Z11, Z12))
        point_ref = Zc2
        S3 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # Full surface, no magnet
        curve_list = []
        curve_list.append(Segment(Z2, Z3))
        curve_list.append(Arc1(begin=Z3, end=Z4, radius=R0, is_trigo_direction=True))
        curve_list.append(Segment(Z4, Z5))
        curve_list.append(Segment(Z5, Z8))
        curve_list.append(Segment(Z8, Z9))
        curve_list.append(Arc1(begin=Z9, end=Z10, radius=R0, is_trigo_direction=True))
        curve_list.append(Segment(Z10, Z11))
        curve_list.append(Segment(Z11, Z2))
        point_ref = Rext - self.H0 - self.H2 / 2
        S4 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # Create the surface list by selecting the correct ones
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

    # Inlined from Methods.Slot.HoleM58.check
    def check(self):
        """Check that the HoleM58 object is correct

        Parameters
        ----------
        self : HoleM58
            A HoleM58 object

        Returns
        -------
        None

        Raises
        _______
        S58_WCheckError
            You must have W1+W2 <= W0
        """
        # Check that everything is set
        if self.W0 is None:
            raise S58_NoneError("You must set W0 !")
        elif self.W1 is None:
            raise S58_NoneError("You must set W1 !")
        elif self.W2 is None:
            raise S58_NoneError("You must set W2 !")
        elif self.W3 is None:
            raise S58_NoneError("You must set W3 !")
        elif self.R0 is None:
            raise S58_NoneError("You must set R0 !")
        elif self.H0 is None:
            raise S58_NoneError("You must set H0 !")
        elif self.H1 is None:
            raise S58_NoneError("You must set H1 !")
        elif self.H2 is None:
            raise S58_NoneError("You must set H2 !")

        Rext = self.get_Rext()

        if self.W0 < self.W1 + self.W2:
            raise S58_WCheckError("You must have W1+W2 <= W0")

    # Inlined from Methods.Slot.HoleM58.comp_magnetization_dict
    def comp_magnetization_dict(self, is_north=True):
        """Compute the dictionary of the magnetization direction of the magnets (key=magnet_X, value=angle[rad])
        Mangetization angle with Hole centered on Ox axis

        Parameters
        ----------
        self : HoleM58
            a HoleM58 object
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
        S0 = Segment(point_dict["Z6"], point_dict["Z7"])
        mag_dict["magnet_0"] = S0.comp_normal()

        if not is_north:
            mag_dict["magnet_0"] += np.pi

        if self.magnetization_dict_offset is not None:
            for key, value in self.magnetization_dict_offset:
                mag_dict[key] += value

        return mag_dict

    # Inlined from Methods.Slot.HoleM58.comp_radius
    def comp_radius(self):
        """Compute the radius of the min and max circle that contains the hole

        Parameters
        ----------
        self : HoleM58
            A HoleM58 object

        Returns
        -------
        (Rmin,Rmax): tuple
            Radius of the circle that contains the hole [m]
        """
        Rext = self.get_Rext()

        Rmax = Rext - self.H1
        Rmin = Rext - self.H0 - self.H2

        return (Rmin, Rmax)

    # Inlined from Methods.Slot.HoleM58.comp_surface_magnet_id
    def comp_surface_magnet_id(self, index):
        """Compute the surface of the hole magnet of the corresponding index

        Parameters
        ----------
        self : HoleM58
            A HoleM58 object
        index : int
            Index of the magnet to compute the surface

        Returns
        -------
        Smag: float
            Surface of the Magnet [m**2]
        """

        if index == 0 and self.magnet_0:
            return self.H2 * self.W1
        return 0

    # Inlined from Methods.Slot.HoleM58.has_magnet
    def has_magnet(self):
        """Return if the Hole has magnets

        Parameters
        ----------
        self : HoleM58
            A HoleM58 object

        Returns
        -------
        has_magnet : bool
            True if the magnets are not None
        """

        return self.magnet_0 is not None

    # Inlined from Methods.Slot.HoleM58.plot_schematics
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
        self : HoleM58
            A HoleM58 object
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
            Default lamination used for the schematics
        """

        # Use some default parameter
        if is_default:
            hole = type(self)(
                Zh=8,
                W0=20e-3,
                W1=12e-3,
                W2=6e-3,
                W3=2 * np.pi / 8 * 0.6,
                H0=17e-3,
                H1=5e-3,
                H2=5e-3,
                R0=1.7e-3,
            )
            lam = LamHole(
                Rint=0.021, Rext=0.075, is_internal=True, is_stator=False, hole=[hole]
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

        else:
            # Getting the main plot
            if self.parent is None:
                raise ParentMissingError("Error: The hole is not inside a Lamination")
            lam = self.parent

            # Remove the magnets
            if type_add_active == 0:
                lam.hole[0].remove_magnet()

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
                # H0
                line = Segment(
                    point_dict["Z1"].real * np.exp(1j * alpha),
                    Rbo * np.exp(1j * alpha),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="H0",
                    offset_label=self.H2 * 0.2 + 1j * self.H0 * 0.35,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # H1
                line = Segment(
                    Rbo * np.exp(1j * np.angle(point_dict["Zc2"])) * np.exp(1j * alpha),
                    (Rbo - self.H1)
                    * np.exp(1j * np.angle(point_dict["Zc2"]))
                    * np.exp(1j * alpha),
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
                    point_dict["Z6"].real * np.exp(1j * alpha),
                    point_dict["Z1"].real * np.exp(1j * alpha),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="H2",
                    offset_label=self.H2 * 0.2,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # R0
                Zlim1 = (Rbo - self.H1) * np.exp(1j * np.angle(point_dict["Zc1"]))
                Zlim2 = (Rbo - self.H1 - self.R0) * np.exp(
                    1j * np.angle(point_dict["Zc1"])
                )
                plot_quote(
                    (Rbo - self.H1)
                    * np.exp(1j * np.angle(point_dict["Zc1"]))
                    * np.exp(1j * alpha),
                    Zlim1 * np.exp(1.02j * alpha),
                    Zlim2 * np.exp(1.02j * alpha),
                    (Rbo - self.H1 - self.R0)
                    * np.exp(1j * np.angle(point_dict["Zc1"]))
                    * np.exp(1j * alpha),
                    offset_label=-self.H2 * 0.8,
                    fig=fig,
                    ax=ax,
                    label="R0",
                )

                # W0
                Zlim1 = point_dict["Z2"] + 0.2 * self.H0
                Zlim2 = point_dict["Z11"] + 0.2 * self.H0
                plot_quote(
                    point_dict["Z2"] * np.exp(1j * alpha),
                    Zlim1 * np.exp(1j * alpha),
                    Zlim2 * np.exp(1j * alpha),
                    point_dict["Z11"] * np.exp(1j * alpha),
                    offset_label=(1 + 1j) * self.H2 * 0.2,
                    fig=fig,
                    ax=ax,
                    label="W0",
                )
                if type_add_active != 0:
                    # W1
                    line = Segment(
                        point_dict["Z6"] * np.exp(1j * alpha),
                        point_dict["Z7"] * np.exp(1j * alpha),
                    )
                    line.plot(
                        fig=fig,
                        ax=ax,
                        color=ARROW_COLOR,
                        linewidth=ARROW_WIDTH,
                        label="W1",
                        offset_label=-1j * self.H2 * 0.5,
                        is_arrow=True,
                        fontsize=SC_FONT_SIZE,
                    )
                    # W2
                    line = Segment(
                        point_dict["Z6"] * np.exp(1j * alpha),
                        point_dict["Z5"] * np.exp(1j * alpha),
                    )
                    line.plot(
                        fig=fig,
                        ax=ax,
                        color=ARROW_COLOR,
                        linewidth=ARROW_WIDTH,
                        label="W2",
                        offset_label=-1j * self.H2 * 0.5,
                        is_arrow=True,
                        fontsize=SC_FONT_SIZE,
                    )
                # W3
                line = Arc1(
                    begin=point_dict["Zc2"] * np.exp(1j * alpha),
                    end=point_dict["Zc1"] * np.exp(1j * alpha),
                    radius=abs(point_dict["Zc1"]),
                    is_trigo_direction=True,
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="W3",
                    offset_label=(1 + 1j) * self.H2 * 0.2,
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
                # H1 radius
                line = Arc1(
                    begin=(Rbo - self.H1)
                    * np.exp(-1j * np.pi / 2)
                    * np.exp(1j * alpha),
                    end=(Rbo - self.H1) * np.exp(1j * np.pi / 2) * np.exp(1j * alpha),
                    radius=Rbo - self.H1,
                    is_trigo_direction=True,
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # W1 lines
                line = Segment(
                    0,
                    abs(point_dict["Zc1"])
                    * 1.5
                    * np.exp(1j * np.angle(point_dict["Zc1"]))
                    * np.exp(1j * alpha),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                line = Segment(
                    0,
                    abs(point_dict["Zc2"])
                    * 1.5
                    * np.exp(1j * np.angle(point_dict["Zc2"]))
                    * np.exp(1j * alpha),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # Magnet lines
                line = Segment(
                    point_dict["Z2"] * np.exp(1j * alpha),
                    point_dict["Z5"] * np.exp(1j * alpha),
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
                    point_dict["Z11"] * np.exp(1j * alpha),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # R0 Arc
                line = Arc1(
                    begin=point_dict["Z4"] * np.exp(1j * alpha),
                    end=point_dict["Z3"] * np.exp(1j * alpha),
                    radius=self.R0,
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
            W = (point_dict["Zc1"].imag + self.R0) * 1.05
            Rint = (Rbo - self.H0 - self.H2) * 0.9
            Rext = self.parent.Rext * 1.05

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

    # Inlined from Methods.Slot.HoleM58.remove_magnet
    def remove_magnet(self):
        """Remove the magnet (set to None) of the Hole

        Parameters
        ----------
        self : HoleM58
            a HoleM58 object
        """

        self.magnet_0 = None

    class MachineCheckError(Exception):
        """ """

    class LaminationCheckError(MachineCheckError):
        """ """

    class SlotCheckError(LaminationCheckError):
        """ """

    class S58_NoneError(SlotCheckError):
        """Raised when a propery of HoleM58 is None"""

    class S58_WCheckError(SlotCheckError):
        """ """


MachineCheckError = HoleM58.MachineCheckError
LaminationCheckError = HoleM58.LaminationCheckError
SlotCheckError = HoleM58.SlotCheckError
S58_NoneError = HoleM58.S58_NoneError
S58_WCheckError = HoleM58.S58_WCheckError
