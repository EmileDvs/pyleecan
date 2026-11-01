# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Slot/HoleM58.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Slot/HoleM58
"""

from os import linesep
from sys import getsizeof
from logging import getLogger
from pyleecan.Classes._check import check_var, raise_
from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.save import save
from pyleecan.Functions.load import load_init_dict
from pyleecan.Functions.Load.import_class import import_class
from copy import deepcopy
from pyleecan.Classes.HoleMag import HoleMag

# Import all class method
# Try/catch to remove unnecessary dependencies in unused method
import numpy as np, matplotlib.pyplot as plt
from pyleecan.Classes.Arc1 import Arc1
from pyleecan.Classes.Segment import Segment
from pyleecan.Classes.SurfLine import SurfLine
from pyleecan.Functions.labels import HOLEM_LAB
from pyleecan.Classes.LamHole import LamHole
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
from pyleecan.Classes import ParentMissingError


from pyleecan.Classes._check import InitUnKnowClassError


class HoleM58(HoleMag):
    """One magnet with circular notches"""

    VERSION = 1
    IS_SYMMETRICAL = 1
    MAGNET_COLOR = config_dict["PLOT"]["COLOR_DICT"]["MAGNET_COLOR"]

    # cf Methods.Slot.HoleM58._comp_point_coordinate
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

        point_dict = dict()
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

    # cf Methods.Slot.HoleM58.build_geometry
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

        surf_list = list()

        surf_list = list()
        # Create all the surfaces for all the cases
        # Air surface Zc1 with magnet_0
        curve_list = list()
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
        curve_list = list()
        curve_list.append(Segment(Z1, Z6))
        curve_list.append(Segment(Z6, Z7))
        curve_list.append(Segment(Z7, Z12))
        curve_list.append(Segment(Z12, Z1))
        point_ref = (Z1 + Z6 + Z7 + Z12) / 4

        S2 = SurfLine(
            line_list=curve_list, label=mag_label + "T0-S0", point_ref=point_ref
        )

        # Air surface Zc2 with magnet_0
        curve_list = list()
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
        curve_list = list()
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

    # cf Methods.Slot.HoleM58.check
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

    # cf Methods.Slot.HoleM58.comp_magnetization_dict
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

        mag_dict = dict()
        S0 = Segment(point_dict["Z6"], point_dict["Z7"])
        mag_dict["magnet_0"] = S0.comp_normal()

        if not is_north:
            mag_dict["magnet_0"] += np.pi

        if self.magnetization_dict_offset is not None:
            for key, value in self.magnetization_dict_offset:
                mag_dict[key] += value

        return mag_dict

    # cf Methods.Slot.HoleM58.comp_radius
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

    # cf Methods.Slot.HoleM58.comp_surface_magnet_id
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

    # cf Methods.Slot.HoleM58.has_magnet
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

    # cf Methods.Slot.HoleM58.plot_schematics
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

    # cf Methods.Slot.HoleM58.remove_magnet
    def remove_magnet(self):
        """Remove the magnet (set to None) of the Hole

        Parameters
        ----------
        self : HoleM58
            a HoleM58 object
        """

        self.magnet_0 = None

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        H0=0.003,
        W0=0.003,
        H1=0,
        W1=0.013,
        H2=0.02,
        W2=0.01,
        W3=0.01,
        R0=0.01,
        magnet_0=-1,
        Zh=36,
        mat_void=-1,
        magnetization_dict_offset=None,
        Alpha0=0,
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
            if "H0" in list(init_dict.keys()):
                H0 = init_dict["H0"]
            if "W0" in list(init_dict.keys()):
                W0 = init_dict["W0"]
            if "H1" in list(init_dict.keys()):
                H1 = init_dict["H1"]
            if "W1" in list(init_dict.keys()):
                W1 = init_dict["W1"]
            if "H2" in list(init_dict.keys()):
                H2 = init_dict["H2"]
            if "W2" in list(init_dict.keys()):
                W2 = init_dict["W2"]
            if "W3" in list(init_dict.keys()):
                W3 = init_dict["W3"]
            if "R0" in list(init_dict.keys()):
                R0 = init_dict["R0"]
            if "magnet_0" in list(init_dict.keys()):
                magnet_0 = init_dict["magnet_0"]
            if "Zh" in list(init_dict.keys()):
                Zh = init_dict["Zh"]
            if "mat_void" in list(init_dict.keys()):
                mat_void = init_dict["mat_void"]
            if "magnetization_dict_offset" in list(init_dict.keys()):
                magnetization_dict_offset = init_dict["magnetization_dict_offset"]
            if "Alpha0" in list(init_dict.keys()):
                Alpha0 = init_dict["Alpha0"]
        # Set the properties (value check and convertion are done in setter)
        self.H0 = H0
        self.W0 = W0
        self.H1 = H1
        self.W1 = W1
        self.H2 = H2
        self.W2 = W2
        self.W3 = W3
        self.R0 = R0
        self.magnet_0 = magnet_0
        # Call HoleMag init
        super(HoleM58, self).__init__(
            Zh=Zh,
            mat_void=mat_void,
            magnetization_dict_offset=magnetization_dict_offset,
            Alpha0=Alpha0,
        )
        # The class is frozen (in HoleMag init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        HoleM58_str = ""
        # Get the properties inherited from HoleMag
        HoleM58_str += super(HoleM58, self).__str__()
        HoleM58_str += "H0 = " + str(self.H0) + linesep
        HoleM58_str += "W0 = " + str(self.W0) + linesep
        HoleM58_str += "H1 = " + str(self.H1) + linesep
        HoleM58_str += "W1 = " + str(self.W1) + linesep
        HoleM58_str += "H2 = " + str(self.H2) + linesep
        HoleM58_str += "W2 = " + str(self.W2) + linesep
        HoleM58_str += "W3 = " + str(self.W3) + linesep
        HoleM58_str += "R0 = " + str(self.R0) + linesep
        if self.magnet_0 is not None:
            tmp = self.magnet_0.__str__().replace(linesep, linesep + "\t").rstrip("\t")
            HoleM58_str += "magnet_0 = " + tmp
        else:
            HoleM58_str += "magnet_0 = None" + linesep + linesep
        return HoleM58_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from HoleMag
        if not super(HoleM58, self).__eq__(other):
            return False
        if other.H0 != self.H0:
            return False
        if other.W0 != self.W0:
            return False
        if other.H1 != self.H1:
            return False
        if other.W1 != self.W1:
            return False
        if other.H2 != self.H2:
            return False
        if other.W2 != self.W2:
            return False
        if other.W3 != self.W3:
            return False
        if other.R0 != self.R0:
            return False
        if other.magnet_0 != self.magnet_0:
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()

        # Check the properties inherited from HoleMag
        diff_list.extend(
            super(HoleM58, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
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
            other._R0 is not None
            and self._R0 is not None
            and np.isnan(other._R0)
            and np.isnan(self._R0)
        ):
            pass
        elif other._R0 != self._R0:
            if is_add_value:
                val_str = " (self=" + str(self._R0) + ", other=" + str(other._R0) + ")"
                diff_list.append(name + ".R0" + val_str)
            else:
                diff_list.append(name + ".R0")
        if (other.magnet_0 is None and self.magnet_0 is not None) or (
            other.magnet_0 is not None and self.magnet_0 is None
        ):
            diff_list.append(name + ".magnet_0 None mismatch")
        elif self.magnet_0 is not None:
            diff_list.extend(
                self.magnet_0.compare(
                    other.magnet_0,
                    name=name + ".magnet_0",
                    ignore_list=ignore_list,
                    is_add_value=is_add_value,
                )
            )
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from HoleMag
        S += super(HoleM58, self).__sizeof__()
        S += getsizeof(self.H0)
        S += getsizeof(self.W0)
        S += getsizeof(self.H1)
        S += getsizeof(self.W1)
        S += getsizeof(self.H2)
        S += getsizeof(self.W2)
        S += getsizeof(self.W3)
        S += getsizeof(self.R0)
        S += getsizeof(self.magnet_0)
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

        # Get the properties inherited from HoleMag
        HoleM58_dict = super(HoleM58, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        HoleM58_dict["H0"] = self.H0
        HoleM58_dict["W0"] = self.W0
        HoleM58_dict["H1"] = self.H1
        HoleM58_dict["W1"] = self.W1
        HoleM58_dict["H2"] = self.H2
        HoleM58_dict["W2"] = self.W2
        HoleM58_dict["W3"] = self.W3
        HoleM58_dict["R0"] = self.R0
        if self.magnet_0 is None:
            HoleM58_dict["magnet_0"] = None
        else:
            HoleM58_dict["magnet_0"] = self.magnet_0.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs
            )
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        HoleM58_dict["__class__"] = "HoleM58"
        return HoleM58_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        H0_val = self.H0
        W0_val = self.W0
        H1_val = self.H1
        W1_val = self.W1
        H2_val = self.H2
        W2_val = self.W2
        W3_val = self.W3
        R0_val = self.R0
        if self.magnet_0 is None:
            magnet_0_val = None
        else:
            magnet_0_val = self.magnet_0.copy()
        Zh_val = self.Zh
        if self.mat_void is None:
            mat_void_val = None
        else:
            mat_void_val = self.mat_void.copy()
        if self.magnetization_dict_offset is None:
            magnetization_dict_offset_val = None
        else:
            magnetization_dict_offset_val = self.magnetization_dict_offset.copy()
        Alpha0_val = self.Alpha0
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(
            H0=H0_val,
            W0=W0_val,
            H1=H1_val,
            W1=W1_val,
            H2=H2_val,
            W2=W2_val,
            W3=W3_val,
            R0=R0_val,
            magnet_0=magnet_0_val,
            Zh=Zh_val,
            mat_void=mat_void_val,
            magnetization_dict_offset=magnetization_dict_offset_val,
            Alpha0=Alpha0_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.H0 = None
        self.W0 = None
        self.H1 = None
        self.W1 = None
        self.H2 = None
        self.W2 = None
        self.W3 = None
        self.R0 = None
        if self.magnet_0 is not None:
            self.magnet_0._set_None()
        # Set to None the properties inherited from HoleMag
        super(HoleM58, self)._set_None()

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
        doc="""Slot depth

        :Type: float
        :min: 0
        """,
    )

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
        doc="""Slot width

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
        doc="""Distance from the lamination Bore

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
        doc="""Magnet width

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
        doc="""Magnet Height

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
        doc="""Distance Magnet to side of the notch

        :Type: float
        :min: 0
        """,
    )

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
        doc="""Tooth angular opening width

        :Type: float
        :min: 0
        """,
    )

    def _get_R0(self):
        """getter of R0"""
        return self._R0

    def _set_R0(self, value):
        """setter of R0"""
        check_var("R0", value, "float", Vmin=0)
        self._R0 = value

    R0 = property(
        fget=_get_R0,
        fset=_set_R0,
        doc="""Notch radius

        :Type: float
        :min: 0
        """,
    )

    def _get_magnet_0(self):
        """getter of magnet_0"""
        return self._magnet_0

    def _set_magnet_0(self, value):
        """setter of magnet_0"""
        if isinstance(value, str):  # Load from file
            try:
                value = load_init_dict(value)[1]
            except Exception as e:
                self.get_logger().error(
                    "Error while loading " + value + ", setting None instead"
                )
                value = None
        if isinstance(value, dict) and "__class__" in value:
            class_obj = import_class(
                "pyleecan.Classes", value.get("__class__"), "magnet_0"
            )
            value = class_obj(init_dict=value)
        elif type(value) is int and value == -1:  # Default constructor
            Magnet = import_class("pyleecan.Classes", "Magnet", "magnet_0")
            value = Magnet()
        check_var("magnet_0", value, "Magnet")
        self._magnet_0 = value

        if self._magnet_0 is not None:
            self._magnet_0.parent = self

    magnet_0 = property(
        fget=_get_magnet_0,
        fset=_set_magnet_0,
        doc="""Magnet

        :Type: Magnet
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

    class S58_WCheckError(SlotCheckError):
        """ """

        pass

    class S58_NoneError(SlotCheckError):
        """Raised when a propery of HoleM58 is None"""

        pass


MachineCheckError = HoleM58.MachineCheckError

LaminationCheckError = HoleM58.LaminationCheckError

SlotCheckError = HoleM58.SlotCheckError

S58_WCheckError = HoleM58.S58_WCheckError

S58_NoneError = HoleM58.S58_NoneError
