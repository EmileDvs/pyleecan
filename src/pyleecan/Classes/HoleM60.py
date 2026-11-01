# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Slot/HoleM60.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Slot/HoleM60
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
from pyleecan.Classes.Arc3 import Arc3
from pyleecan.Classes.Segment import Segment
from pyleecan.Classes.SurfLine import SurfLine
from pyleecan.Functions.labels import HOLEM_LAB
from pyleecan.Methods.Slot.HoleM60 import S60_WCheckError, S60_NoneError
from pyleecan.Classes.Arc1 import Arc1
from pyleecan.Classes.LamHole import LamHole
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


class HoleM60(HoleMag):
    """V shape slot for buried magnet"""

    VERSION = 1
    IS_SYMMETRICAL = 1

    # cf Methods.Slot.HoleM60._comp_point_coordinate
    def _comp_point_coordinate(self):
        """Compute the point coordinates needed to plot the Slot.

        Parameters
        ----------
        self : HoleM60
            A HoleM60 object

        Returns
        -------
        point_dict: dict
            A dict of the slot coordinates
        """

        Rbo = self.get_Rbo()

        # comp point coordinate (in complex)
        # Draw the left side with center P
        Z0 = 1j * self.H0 / (2 * np.sin(self.W0 / 2))
        Z1 = -self.W3 / 2 + 1j * (Z0.imag + (self.W3 / 2) / np.tan(self.W0 / 2))
        Z2 = (
            Z1.real
            - np.sin(self.W0 / 2) * (self.W2 - self.H0)
            + 1j * (Z1.imag + np.cos(self.W0 / 2) * (self.W2 - self.H0))
        )

        # Draw the left hole with center P2
        Z3h = -self.H0 / 2 - 1j * self.H0 / 2
        Z4h = -1j * self.H0
        Z5h = self.W2 - self.H0 - 1j * self.H0
        Z6h = self.W2 - self.H0 / 2 - 1j * (self.H0 / 2)
        w = self.W2 - self.H0
        ZM1h = (w - self.W1) / 2 + self.W1
        ZM2h = (w - self.W1) / 2
        ZM4h = (w - self.W1) / 2 + self.W1 - 1j * self.H0
        ZM3h = (w - self.W1) / 2 - 1j * self.H0

        # Revert translation and rotation to center left hole in P
        Z3 = Z3h * np.exp(1j * np.angle(Z1 - Z2)) + Z2
        Z4 = Z4h * np.exp(1j * np.angle(Z1 - Z2)) + Z2
        Z5 = Z5h * np.exp(1j * np.angle(Z1 - Z2)) + Z2
        Z6 = Z6h * np.exp(1j * np.angle(Z1 - Z2)) + Z2
        ZM1 = ZM1h * np.exp(1j * np.angle(Z1 - Z2)) + Z2
        ZM2 = ZM2h * np.exp(1j * np.angle(Z1 - Z2)) + Z2
        ZM3 = ZM3h * np.exp(1j * np.angle(Z1 - Z2)) + Z2
        ZM4 = ZM4h * np.exp(1j * np.angle(Z1 - Z2)) + Z2

        # Revert translation to center left hole in machine's center
        Z = 1j * (np.sqrt((Rbo - self.H1) ** 2 - Z3.real**2) - Z3.imag)
        Z0 += Z
        Z1 += Z
        Z2 += Z
        Z3 += Z
        Z4 += Z
        Z5 += Z
        Z6 += Z
        ZM1 += Z
        ZM2 += Z
        ZM3 += Z
        ZM4 += Z

        # Rotation of angle -pi / 2 to respect slot conventions
        Z *= np.exp(-1j * np.pi / 2)
        Z0 *= np.exp(-1j * np.pi / 2)
        Z1 *= np.exp(-1j * np.pi / 2)
        Z2 *= np.exp(-1j * np.pi / 2)
        Z3 *= np.exp(-1j * np.pi / 2)
        Z4 *= np.exp(-1j * np.pi / 2)
        Z5 *= np.exp(-1j * np.pi / 2)
        Z6 *= np.exp(-1j * np.pi / 2)
        ZM1 *= np.exp(-1j * np.pi / 2)
        ZM2 *= np.exp(-1j * np.pi / 2)
        ZM3 *= np.exp(-1j * np.pi / 2)
        ZM4 *= np.exp(-1j * np.pi / 2)

        # Draw the right hole by symmetry
        Z1s = Z1.conjugate()
        Z2s = Z2.conjugate()
        Z3s = Z3.conjugate()
        Z4s = Z4.conjugate()
        Z5s = Z5.conjugate()
        Z6s = Z6.conjugate()
        ZM1s = ZM1.conjugate()
        ZM2s = ZM2.conjugate()
        ZM3s = ZM3.conjugate()
        ZM4s = ZM4.conjugate()

        point_dict = dict()
        point_dict["Z"] = Z
        point_dict["Z0"] = Z0
        point_dict["Z1"] = Z1
        point_dict["Z2"] = Z2
        point_dict["Z3"] = Z3
        point_dict["Z4"] = Z4
        point_dict["Z5"] = Z5
        point_dict["Z6"] = Z6
        point_dict["ZM1"] = ZM1
        point_dict["ZM2"] = ZM2
        point_dict["ZM3"] = ZM3
        point_dict["ZM4"] = ZM4
        point_dict["Z1s"] = Z1s
        point_dict["Z2s"] = Z2s
        point_dict["Z3s"] = Z3s
        point_dict["Z4s"] = Z4s
        point_dict["Z5s"] = Z5s
        point_dict["Z6s"] = Z6s
        point_dict["ZM1s"] = ZM1s
        point_dict["ZM2s"] = ZM2s
        point_dict["ZM3s"] = ZM3s
        point_dict["ZM4s"] = ZM4s

        return point_dict

    # cf Methods.Slot.HoleM60.build_geometry
    def build_geometry(self, alpha=0, delta=0, is_simplified=False):
        """Compute the curve (Segment) needed to plot the Slot.
        The ending point of a curve is the starting point of the next curve in
        the list

        Parameters
        ----------
        self : HoleM60
            A HoleM60 object
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

        # Get all the points
        point_dict = self._comp_point_coordinate()
        Z1 = point_dict["Z1"]
        Z2 = point_dict["Z2"]
        # Z3 = point_dict["Z3"]
        Z4 = point_dict["Z4"]
        Z5 = point_dict["Z5"]
        # Z6 = point_dict["Z6"]
        Z1s = point_dict["Z1s"]
        Z2s = point_dict["Z2s"]
        # Z3s = point_dict["Z3s"]
        Z4s = point_dict["Z4s"]
        Z5s = point_dict["Z5s"]
        # Z6s = point_dict["Z6s"]
        ZM1 = point_dict["ZM1"]
        ZM2 = point_dict["ZM2"]
        ZM3 = point_dict["ZM3"]
        ZM4 = point_dict["ZM4"]
        ZM1s = point_dict["ZM1s"]
        ZM2s = point_dict["ZM2s"]
        ZM3s = point_dict["ZM3s"]
        ZM4s = point_dict["ZM4s"]

        surf_list = list()
        # Create all the surfaces for all the cases
        # Upper surface without magnet_1
        curve_list = list()
        curve_list.append(Segment(Z1, Z2))
        curve_list.append(Arc3(begin=Z2, end=Z4, is_trigo_direction=True))
        curve_list.append(Segment(Z4, Z5))
        curve_list.append(Arc3(begin=Z5, end=Z1, is_trigo_direction=True))
        point_ref = (Z1 + Z4) / 2
        S1 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # Lower surface without magnet_0
        curve_list = list()
        curve_list.append(Arc3(begin=Z1s, end=Z5s, is_trigo_direction=True))
        curve_list.append(Segment(Z5s, Z4s))
        curve_list.append(Arc3(begin=Z4s, end=Z2s, is_trigo_direction=True))
        curve_list.append(Segment(Z2s, Z1s))
        point_ref = (Z1s + Z4s) / 2
        S0 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # Air surface 1 with magnet_1
        curve_list = list()
        curve_list.append(Segment(Z1, ZM1))
        curve_list.append(Segment(ZM1, ZM4))
        curve_list.append(Segment(ZM4, Z5))
        curve_list.append(Arc3(begin=Z5, end=Z1, is_trigo_direction=True))
        point_ref = (ZM1 + Z5) / 2
        SM11 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # Air surface 2 with magnet_1
        curve_list = list()
        curve_list.append(Segment(ZM2, Z2))
        curve_list.append(Arc3(begin=Z2, end=Z4, is_trigo_direction=True))
        curve_list.append(Segment(Z4, ZM3))
        curve_list.append(Segment(ZM3, ZM2))
        point_ref = (Z2 + ZM3) / 2
        SM12 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # Magnet_1 surface
        curve_list = list()
        curve_list.append(Segment(ZM1, ZM2))
        curve_list.append(Segment(ZM2, ZM3))
        curve_list.append(Segment(ZM3, ZM4))
        curve_list.append(Segment(ZM4, ZM1))
        point_ref = (ZM1 + ZM3) / 2
        SM1 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # Air surface 1 with magnet_0
        curve_list = list()
        curve_list.append(Segment(Z1s, ZM1s))
        curve_list.append(Segment(ZM1s, ZM4s))
        curve_list.append(Segment(ZM4s, Z5s))
        curve_list.append(Arc3(begin=Z5s, end=Z1s, is_trigo_direction=False))
        point_ref = (ZM1s + Z5s) / 2
        SM01 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # Air surface 2 with magnet_0
        curve_list = list()
        curve_list.append(Segment(ZM2s, Z2s))
        curve_list.append(Arc3(begin=Z2s, end=Z4s, is_trigo_direction=False))
        curve_list.append(Segment(Z4s, ZM3s))
        curve_list.append(Segment(ZM3s, ZM2s))
        point_ref = (Z2s + ZM3s) / 2
        SM02 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # Magnet_0 surface
        curve_list = list()
        curve_list.append(Segment(ZM1s, ZM4s))
        curve_list.append(Segment(ZM4s, ZM3s))
        curve_list.append(Segment(ZM3s, ZM2s))
        curve_list.append(Segment(ZM2s, ZM1s))
        point_ref = (ZM1s + ZM3s) / 2
        SM0 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # Create the surface list by selecting the correct ones
        surf_list = list()
        if self.magnet_0:
            SM01.label = vent_label + "T0-S0"
            SM0.label = mag_label + "T0-S0"
            SM02.label = vent_label + "T1-S0"
            surf_list += [SM0, SM01, SM02]
            if self.magnet_1:
                SM11.label = vent_label + "T2-S0"
                SM1.label = mag_label + "T1-S0"
                SM12.label = vent_label + "T3-S0"
                surf_list += [SM1, SM11, SM12]
            else:
                S1.label = vent_label + "T2-S0"
                surf_list += [S1]
        else:
            S0.label = vent_label + "T0-S0"
            surf_list += [S0]
            if self.magnet_1:
                SM11.label = vent_label + "T1-S0"
                SM1.label = mag_label + "T1-S0"
                SM12.label = vent_label + "T2-S0"
                surf_list += [SM1, SM11, SM12]
            else:
                S1.label = vent_label + "T1-S0"
                surf_list += [S1]

        # Apply the transformations
        for surf in surf_list:
            surf.rotate(alpha)
            surf.translate(delta)

        return surf_list

    # cf Methods.Slot.HoleM60.check
    def check(self):
        """Check that the HoleM60 object is correct

        Parameters
        ----------
        self : HoleM60
            A HoleM60 object

        Returns
        -------
        None

        Raises
        _______
        S60_WCheckError
            You must have W1+H0 <= W2
        """
        # Check that everything is set
        if self.W0 is None:
            raise S60_NoneError("You must set W0 !")
        elif self.W1 is None:
            raise S60_NoneError("You must set W1 !")
        elif self.W2 is None:
            raise S60_NoneError("You must set W2 !")
        elif self.W3 is None:
            raise S60_NoneError("You must set W3 !")
        elif self.H0 is None:
            raise S60_NoneError("You must set H0 !")
        elif self.H1 is None:
            raise S60_NoneError("You must set H1 !")

        if (self.W1 + self.H0) > self.W2:
            raise S60_WCheckError("You must have (W1 + H0) <= W2")

    # cf Methods.Slot.HoleM60.comp_magnetization_dict
    def comp_magnetization_dict(self, is_north=True):
        """Compute the dictionary of the magnetization direction of the magnets (key=magnet_X, value=angle[rad])
        Mangetization angle with Hole centered on Ox axis

        Parameters
        ----------
        self : HoleM60
            a HoleM60 object
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
        S0 = Segment(point_dict["ZM4s"], point_dict["ZM3s"])
        mag_dict["magnet_0"] = S0.comp_normal()
        S1 = Segment(point_dict["ZM3"], point_dict["ZM4"])
        mag_dict["magnet_1"] = S1.comp_normal()

        if not is_north:
            mag_dict["magnet_0"] += np.pi
            mag_dict["magnet_1"] += np.pi

        if self.magnetization_dict_offset is not None:
            for key, value in self.magnetization_dict_offset:
                mag_dict[key] += value

        return mag_dict

    # cf Methods.Slot.HoleM60.comp_radius
    def comp_radius(self):
        """Compute the radius of the min and max circle that contains the slot

        Parameters
        ----------
        self : HoleM60
            A HoleM60 object

        Returns
        -------
        (Rmin,Rmax): tuple
            Radius of the circle that contains the slot [m]
        """
        point_dict = self._comp_point_coordinate()

        point_list = list()
        # Discretize arcs to get the higher point and the lower point
        curve = Arc3(
            begin=point_dict["Z2"], end=point_dict["Z4"], is_trigo_direction=True
        )
        point_list.extend(curve.discretize())
        curve = Arc3(
            begin=point_dict["Z5"], end=point_dict["Z1"], is_trigo_direction=True
        )
        point_list.extend(curve.discretize())

        abs_list = [np.abs(point) for point in point_list]
        Rmax = max(abs_list)
        Rmin = min(abs_list)

        return (Rmin, Rmax)

    # cf Methods.Slot.HoleM60.comp_surface_magnet_id
    def comp_surface_magnet_id(self, index):
        """Compute the surface of the hole magnet of the corresponding index

        Parameters
        ----------
        self : HoleM60
            A HoleM60 object
        index : int
            Index of the magnet to compute the surface

        Returns
        -------
        Smag: float
            Surface of the Magnet [m**2]
        """

        # all magnet has the same surface
        label = "magnet_" + str(index)
        if index in [0, 1] and getattr(self, label) is not None:
            return self.W1 * self.H0
        return 0

    # cf Methods.Slot.HoleM60.has_magnet
    def has_magnet(self):
        """Return if the Hole has magnets

        Parameters
        ----------
        self : HoleM60
            A HoleM60 object

        Returns
        -------
        has_magnet : bool
            True if the magnets are not None
        """

        return self.magnet_0 is not None or self.magnet_1 is not None

    # cf Methods.Slot.HoleM60.plot_schematics
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
        self : HoleM60
            A HoleM60 object
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
                Zh=4,
                W0=np.pi * 0.5,
                W1=2e-2,
                W2=7e-2,
                W3=8e-3,
                H0=12e-3,
                H1=10e-3,
            )
            lam = LamHole(
                Rint=0.03, Rext=0.12, is_internal=True, is_stator=False, hole=[hole]
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
            # W0
            line = Arc1(
                begin=point_dict["ZM1s"] * np.exp(1j * alpha),
                end=point_dict["ZM1"] * np.exp(1j * alpha),
                radius=abs(
                    (point_dict["ZM1"] + point_dict["Z1"]) / 2
                    - (point_dict["ZM1s"] + point_dict["Z1s"]) / 2
                ),
                is_trigo_direction=True,
            )
            line.plot(
                fig=fig,
                ax=ax,
                color=ARROW_COLOR,
                linewidth=ARROW_WIDTH,
                label="W0",
                offset_label=(1 + 1j) * self.H1 * 0.4,
                fontsize=SC_FONT_SIZE,
            )
            # W1, magnet width only if magnet is visible
            if type_add_active == 2:
                line = Segment(
                    point_dict["ZM1"] * np.exp(1j * alpha),
                    point_dict["ZM2"] * np.exp(1j * alpha),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="W1",
                    offset_label=(1 + 1j) * self.H1 * 0.25,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
            # W2
            line = Segment(
                point_dict["Z3s"] * np.exp(1j * alpha),
                point_dict["Z6s"] * np.exp(1j * alpha),
            )
            line.plot(
                fig=fig,
                ax=ax,
                color=ARROW_COLOR,
                linewidth=ARROW_WIDTH,
                label="W2",
                offset_label=-1j * self.H1,
                is_arrow=True,
                fontsize=SC_FONT_SIZE,
            )
            # W3
            line = Segment(
                point_dict["Z1"] * np.exp(1j * alpha),
                point_dict["Z1s"] * np.exp(1j * alpha),
            )
            line.plot(
                fig=fig,
                ax=ax,
                color=ARROW_COLOR,
                linewidth=ARROW_WIDTH,
                label="W3",
                offset_label=1j * self.H1 * 0.5,
                is_arrow=True,
                fontsize=SC_FONT_SIZE,
            )
            # H0
            line = Segment(
                point_dict["Z2s"] * np.exp(1j * alpha),
                point_dict["Z4s"] * np.exp(1j * alpha),
            )
            line.plot(
                fig=fig,
                ax=ax,
                color=ARROW_COLOR,
                linewidth=ARROW_WIDTH,
                label="H0",
                offset_label=-1j * self.H1,
                is_arrow=True,
                fontsize=SC_FONT_SIZE,
            )
            # H1
            A = np.angle(point_dict["Z3"])
            line = Segment(
                Rbo * np.exp(1j * A) * np.exp(1j * alpha),
                (Rbo - self.H1) * np.exp(1j * A) * np.exp(1j * alpha),
            )
            line.plot(
                fig=fig,
                ax=ax,
                color=ARROW_COLOR,
                linewidth=ARROW_WIDTH,
                label="H1",
                offset_label=self.H1 * 0.5,
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
            line = Segment(0, lam.Rext * 1.5 * np.exp(1j * sp / 2) * np.exp(1j * alpha))
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
            # H1 radius
            A = np.angle(point_dict["Z3"])
            line = Segment(0, Rbo * np.exp(1j * A) * np.exp(1j * alpha))
            line.plot(
                fig=fig,
                ax=ax,
                color=MAIN_LINE_COLOR,
                linestyle=MAIN_LINE_STYLE,
                linewidth=MAIN_LINE_WIDTH,
            )
            line = Arc1(
                begin=(Rbo - self.H1)
                * np.exp(-1j * np.pi / 2 * 0.9)
                * np.exp(1j * alpha),
                end=(Rbo - self.H1) * np.exp(1j * np.pi / 2 * 0.9) * np.exp(1j * alpha),
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
            # H0 lines
            line = Segment(
                point_dict["Z2"] * np.exp(1j * alpha),
                point_dict["Z4"] * np.exp(1j * alpha),
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
                point_dict["Z1s"] * np.exp(1j * alpha),
                point_dict["Z5s"] * np.exp(1j * alpha),
            )
            line.plot(
                fig=fig,
                ax=ax,
                color=MAIN_LINE_COLOR,
                linestyle=MAIN_LINE_STYLE,
                linewidth=MAIN_LINE_WIDTH,
            )

        # Zooming and cleaning
        W = (point_dict["Z"] * np.exp(1j * sp)).imag
        Rint = self.parent.Rint
        Rext = self.parent.Rext

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

    # cf Methods.Slot.HoleM60.remove_magnet
    def remove_magnet(self):
        """Remove the magnet (set to None) of the Hole

        Parameters
        ----------
        self : HoleM60
            a HoleM60 object
        """

        self.magnet_0 = None
        self.magnet_1 = None

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        W0=None,
        W1=None,
        W2=None,
        W3=None,
        H0=None,
        H1=None,
        magnet_0=-1,
        magnet_1=-1,
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
            if "W0" in list(init_dict.keys()):
                W0 = init_dict["W0"]
            if "W1" in list(init_dict.keys()):
                W1 = init_dict["W1"]
            if "W2" in list(init_dict.keys()):
                W2 = init_dict["W2"]
            if "W3" in list(init_dict.keys()):
                W3 = init_dict["W3"]
            if "H0" in list(init_dict.keys()):
                H0 = init_dict["H0"]
            if "H1" in list(init_dict.keys()):
                H1 = init_dict["H1"]
            if "magnet_0" in list(init_dict.keys()):
                magnet_0 = init_dict["magnet_0"]
            if "magnet_1" in list(init_dict.keys()):
                magnet_1 = init_dict["magnet_1"]
            if "Zh" in list(init_dict.keys()):
                Zh = init_dict["Zh"]
            if "mat_void" in list(init_dict.keys()):
                mat_void = init_dict["mat_void"]
            if "magnetization_dict_offset" in list(init_dict.keys()):
                magnetization_dict_offset = init_dict["magnetization_dict_offset"]
            if "Alpha0" in list(init_dict.keys()):
                Alpha0 = init_dict["Alpha0"]
        # Set the properties (value check and convertion are done in setter)
        self.W0 = W0
        self.W1 = W1
        self.W2 = W2
        self.W3 = W3
        self.H0 = H0
        self.H1 = H1
        self.magnet_0 = magnet_0
        self.magnet_1 = magnet_1
        # Call HoleMag init
        super(HoleM60, self).__init__(
            Zh=Zh,
            mat_void=mat_void,
            magnetization_dict_offset=magnetization_dict_offset,
            Alpha0=Alpha0,
        )
        # The class is frozen (in HoleMag init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        HoleM60_str = ""
        # Get the properties inherited from HoleMag
        HoleM60_str += super(HoleM60, self).__str__()
        HoleM60_str += "W0 = " + str(self.W0) + linesep
        HoleM60_str += "W1 = " + str(self.W1) + linesep
        HoleM60_str += "W2 = " + str(self.W2) + linesep
        HoleM60_str += "W3 = " + str(self.W3) + linesep
        HoleM60_str += "H0 = " + str(self.H0) + linesep
        HoleM60_str += "H1 = " + str(self.H1) + linesep
        if self.magnet_0 is not None:
            tmp = self.magnet_0.__str__().replace(linesep, linesep + "\t").rstrip("\t")
            HoleM60_str += "magnet_0 = " + tmp
        else:
            HoleM60_str += "magnet_0 = None" + linesep + linesep
        if self.magnet_1 is not None:
            tmp = self.magnet_1.__str__().replace(linesep, linesep + "\t").rstrip("\t")
            HoleM60_str += "magnet_1 = " + tmp
        else:
            HoleM60_str += "magnet_1 = None" + linesep + linesep
        return HoleM60_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from HoleMag
        if not super(HoleM60, self).__eq__(other):
            return False
        if other.W0 != self.W0:
            return False
        if other.W1 != self.W1:
            return False
        if other.W2 != self.W2:
            return False
        if other.W3 != self.W3:
            return False
        if other.H0 != self.H0:
            return False
        if other.H1 != self.H1:
            return False
        if other.magnet_0 != self.magnet_0:
            return False
        if other.magnet_1 != self.magnet_1:
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
            super(HoleM60, self).compare(
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
        if (other.magnet_1 is None and self.magnet_1 is not None) or (
            other.magnet_1 is not None and self.magnet_1 is None
        ):
            diff_list.append(name + ".magnet_1 None mismatch")
        elif self.magnet_1 is not None:
            diff_list.extend(
                self.magnet_1.compare(
                    other.magnet_1,
                    name=name + ".magnet_1",
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
        S += super(HoleM60, self).__sizeof__()
        S += getsizeof(self.W0)
        S += getsizeof(self.W1)
        S += getsizeof(self.W2)
        S += getsizeof(self.W3)
        S += getsizeof(self.H0)
        S += getsizeof(self.H1)
        S += getsizeof(self.magnet_0)
        S += getsizeof(self.magnet_1)
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
        HoleM60_dict = super(HoleM60, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        HoleM60_dict["W0"] = self.W0
        HoleM60_dict["W1"] = self.W1
        HoleM60_dict["W2"] = self.W2
        HoleM60_dict["W3"] = self.W3
        HoleM60_dict["H0"] = self.H0
        HoleM60_dict["H1"] = self.H1
        if self.magnet_0 is None:
            HoleM60_dict["magnet_0"] = None
        else:
            HoleM60_dict["magnet_0"] = self.magnet_0.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs
            )
        if self.magnet_1 is None:
            HoleM60_dict["magnet_1"] = None
        else:
            HoleM60_dict["magnet_1"] = self.magnet_1.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs
            )
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        HoleM60_dict["__class__"] = "HoleM60"
        return HoleM60_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        W0_val = self.W0
        W1_val = self.W1
        W2_val = self.W2
        W3_val = self.W3
        H0_val = self.H0
        H1_val = self.H1
        if self.magnet_0 is None:
            magnet_0_val = None
        else:
            magnet_0_val = self.magnet_0.copy()
        if self.magnet_1 is None:
            magnet_1_val = None
        else:
            magnet_1_val = self.magnet_1.copy()
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
            W0=W0_val,
            W1=W1_val,
            W2=W2_val,
            W3=W3_val,
            H0=H0_val,
            H1=H1_val,
            magnet_0=magnet_0_val,
            magnet_1=magnet_1_val,
            Zh=Zh_val,
            mat_void=mat_void_val,
            magnetization_dict_offset=magnetization_dict_offset_val,
            Alpha0=Alpha0_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.W0 = None
        self.W1 = None
        self.W2 = None
        self.W3 = None
        self.H0 = None
        self.H1 = None
        if self.magnet_0 is not None:
            self.magnet_0._set_None()
        if self.magnet_1 is not None:
            self.magnet_1._set_None()
        # Set to None the properties inherited from HoleMag
        super(HoleM60, self)._set_None()

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
        doc="""Hole angular width

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
        doc="""Hole width

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
        doc="""Tooth width

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
        doc="""Magnet height

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
        doc="""Distance from the lamination bore

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
        doc="""First Magnet

        :Type: Magnet
        """,
    )

    def _get_magnet_1(self):
        """getter of magnet_1"""
        return self._magnet_1

    def _set_magnet_1(self, value):
        """setter of magnet_1"""
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
                "pyleecan.Classes", value.get("__class__"), "magnet_1"
            )
            value = class_obj(init_dict=value)
        elif type(value) is int and value == -1:  # Default constructor
            Magnet = import_class("pyleecan.Classes", "Magnet", "magnet_1")
            value = Magnet()
        check_var("magnet_1", value, "Magnet")
        self._magnet_1 = value

        if self._magnet_1 is not None:
            self._magnet_1.parent = self

    magnet_1 = property(
        fget=_get_magnet_1,
        fset=_set_magnet_1,
        doc="""Second Magnet

        :Type: Magnet
        """,
    )
