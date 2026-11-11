# Experimental dataclass generated from Generator/ClassesRef/Slot/HoleM60.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field
from typing import ClassVar

import matplotlib.pyplot as plt
import numpy as np

from ..definitions import config_dict
from ..Functions_new.labels import HOLEM_LAB
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
from .arc_3 import Arc3
from .hole_mag import HoleMag
from .lam_hole import LamHole
from .magnet import Magnet
from .segment import Segment
from .surf_line import SurfLine


@dataclass(eq=False)
class HoleM60(HoleMag):
    """V shape slot for buried magnet

    Attributes
    ----------
    W0 : float or None
        Hole angular width
        Unit: rad; Default: None; Minimum: 0
    W1 : float or None
        Magnet width
        Unit: m; Default: None; Minimum: 0
    W2 : float or None
        Hole width
        Unit: m; Default: None; Minimum: 0
    W3 : float or None
        Tooth width
        Unit: m; Default: None; Minimum: 0
    H0 : float or None
        Magnet height
        Unit: m; Default: None; Minimum: 0
    H1 : float or None
        Distance from the lamination bore
        Unit: m; Default: None; Minimum: 0
    magnet_0 : Magnet or None
        First Magnet
        Default: Magnet()
    magnet_1 : Magnet or None
        Second Magnet
        Default: Magnet()
    """

    IS_SYMMETRICAL: ClassVar = 1
    MAGNET_COLOR = config_dict["PLOT"]["COLOR_DICT"]["MAGNET_COLOR"]
    W0: float | None = None
    """Hole angular width"""
    W1: float | None = None
    """Magnet width"""
    W2: float | None = None
    """Hole width"""
    W3: float | None = None
    """Tooth width"""
    H0: float | None = None
    """Magnet height"""
    H1: float | None = None
    """Distance from the lamination bore"""
    magnet_0: Magnet | None = field(
        default_factory=lambda: Magnet(), metadata={"default_class": "Magnet"}
    )
    """First Magnet"""
    magnet_1: Magnet | None = field(
        default_factory=lambda: Magnet(), metadata={"default_class": "Magnet"}
    )
    """Second Magnet"""

    # Inlined from Methods.Slot.HoleM60._comp_point_coordinate
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

        point_dict = {}
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

    # Inlined from Methods.Slot.HoleM60.build_geometry
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

        surf_list = []
        # Create all the surfaces for all the cases
        # Upper surface without magnet_1
        curve_list = []
        curve_list.append(Segment(begin=Z1, end=Z2))
        curve_list.append(Arc3(begin=Z2, end=Z4, is_trigo_direction=True))
        curve_list.append(Segment(begin=Z4, end=Z5))
        curve_list.append(Arc3(begin=Z5, end=Z1, is_trigo_direction=True))
        point_ref = (Z1 + Z4) / 2
        S1 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # Lower surface without magnet_0
        curve_list = []
        curve_list.append(Arc3(begin=Z1s, end=Z5s, is_trigo_direction=True))
        curve_list.append(Segment(begin=Z5s, end=Z4s))
        curve_list.append(Arc3(begin=Z4s, end=Z2s, is_trigo_direction=True))
        curve_list.append(Segment(begin=Z2s, end=Z1s))
        point_ref = (Z1s + Z4s) / 2
        S0 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # Air surface 1 with magnet_1
        curve_list = []
        curve_list.append(Segment(begin=Z1, end=ZM1))
        curve_list.append(Segment(begin=ZM1, end=ZM4))
        curve_list.append(Segment(begin=ZM4, end=Z5))
        curve_list.append(Arc3(begin=Z5, end=Z1, is_trigo_direction=True))
        point_ref = (ZM1 + Z5) / 2
        SM11 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # Air surface 2 with magnet_1
        curve_list = []
        curve_list.append(Segment(begin=ZM2, end=Z2))
        curve_list.append(Arc3(begin=Z2, end=Z4, is_trigo_direction=True))
        curve_list.append(Segment(begin=Z4, end=ZM3))
        curve_list.append(Segment(begin=ZM3, end=ZM2))
        point_ref = (Z2 + ZM3) / 2
        SM12 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # Magnet_1 surface
        curve_list = []
        curve_list.append(Segment(begin=ZM1, end=ZM2))
        curve_list.append(Segment(begin=ZM2, end=ZM3))
        curve_list.append(Segment(begin=ZM3, end=ZM4))
        curve_list.append(Segment(begin=ZM4, end=ZM1))
        point_ref = (ZM1 + ZM3) / 2
        SM1 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # Air surface 1 with magnet_0
        curve_list = []
        curve_list.append(Segment(begin=Z1s, end=ZM1s))
        curve_list.append(Segment(begin=ZM1s, end=ZM4s))
        curve_list.append(Segment(begin=ZM4s, end=Z5s))
        curve_list.append(Arc3(begin=Z5s, end=Z1s, is_trigo_direction=False))
        point_ref = (ZM1s + Z5s) / 2
        SM01 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # Air surface 2 with magnet_0
        curve_list = []
        curve_list.append(Segment(begin=ZM2s, end=Z2s))
        curve_list.append(Arc3(begin=Z2s, end=Z4s, is_trigo_direction=False))
        curve_list.append(Segment(begin=Z4s, end=ZM3s))
        curve_list.append(Segment(begin=ZM3s, end=ZM2s))
        point_ref = (Z2s + ZM3s) / 2
        SM02 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # Magnet_0 surface
        curve_list = []
        curve_list.append(Segment(begin=ZM1s, end=ZM4s))
        curve_list.append(Segment(begin=ZM4s, end=ZM3s))
        curve_list.append(Segment(begin=ZM3s, end=ZM2s))
        curve_list.append(Segment(begin=ZM2s, end=ZM1s))
        point_ref = (ZM1s + ZM3s) / 2
        SM0 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # Create the surface list by selecting the correct ones
        surf_list = []
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

    # Inlined from Methods.Slot.HoleM60.check
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
            raise self.S60_NoneError("You must set W0 !")
        elif self.W1 is None:
            raise self.S60_NoneError("You must set W1 !")
        elif self.W2 is None:
            raise self.S60_NoneError("You must set W2 !")
        elif self.W3 is None:
            raise self.S60_NoneError("You must set W3 !")
        elif self.H0 is None:
            raise self.S60_NoneError("You must set H0 !")
        elif self.H1 is None:
            raise self.S60_NoneError("You must set H1 !")

        if (self.W1 + self.H0) > self.W2:
            raise self.S60_WCheckError("You must have (W1 + H0) <= W2")

    # Inlined from Methods.Slot.HoleM60.comp_magnetization_dict
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

        mag_dict = {}
        S0 = Segment(begin=point_dict["ZM4s"], end=point_dict["ZM3s"])
        mag_dict["magnet_0"] = S0.comp_normal()
        S1 = Segment(begin=point_dict["ZM3"], end=point_dict["ZM4"])
        mag_dict["magnet_1"] = S1.comp_normal()

        if not is_north:
            mag_dict["magnet_0"] += np.pi
            mag_dict["magnet_1"] += np.pi

        if self.magnetization_dict_offset is not None:
            for key, value in self.magnetization_dict_offset:
                mag_dict[key] += value

        return mag_dict

    # Inlined from Methods.Slot.HoleM60.comp_radius
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

        point_list = []
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

    # Inlined from Methods.Slot.HoleM60.comp_surface_magnet_id
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

    # Inlined from Methods.Slot.HoleM60.has_magnet
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

    # Inlined from Methods.Slot.HoleM60.plot_schematics
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
                    begin=point_dict["ZM1"] * np.exp(1j * alpha),
                    end=point_dict["ZM2"] * np.exp(1j * alpha),
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
                begin=point_dict["Z3s"] * np.exp(1j * alpha),
                end=point_dict["Z6s"] * np.exp(1j * alpha),
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
                begin=point_dict["Z1"] * np.exp(1j * alpha),
                end=point_dict["Z1s"] * np.exp(1j * alpha),
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
                begin=point_dict["Z2s"] * np.exp(1j * alpha),
                end=point_dict["Z4s"] * np.exp(1j * alpha),
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
                begin=Rbo * np.exp(1j * A) * np.exp(1j * alpha),
                end=(Rbo - self.H1) * np.exp(1j * A) * np.exp(1j * alpha),
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
            line = Segment(begin=0, end=lam.Rext * 1.5 * np.exp(1j * alpha))
            line.plot(
                fig=fig,
                ax=ax,
                color=MAIN_LINE_COLOR,
                linestyle=MAIN_LINE_STYLE,
                linewidth=MAIN_LINE_WIDTH,
            )
            # Tooth axis
            line = Segment(
                begin=0, end=lam.Rext * 1.5 * np.exp(1j * sp / 2) * np.exp(1j * alpha)
            )
            line.plot(
                fig=fig,
                ax=ax,
                color=MAIN_LINE_COLOR,
                linestyle=MAIN_LINE_STYLE,
                linewidth=MAIN_LINE_WIDTH,
            )
            line = Segment(
                begin=0, end=lam.Rext * 1.5 * np.exp(-1j * sp / 2) * np.exp(1j * alpha)
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
            line = Segment(begin=0, end=Rbo * np.exp(1j * A) * np.exp(1j * alpha))
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
                begin=point_dict["Z2"] * np.exp(1j * alpha),
                end=point_dict["Z4"] * np.exp(1j * alpha),
            )
            line.plot(
                fig=fig,
                ax=ax,
                color=MAIN_LINE_COLOR,
                linestyle=MAIN_LINE_STYLE,
                linewidth=MAIN_LINE_WIDTH,
            )
            line = Segment(
                begin=point_dict["Z1"] * np.exp(1j * alpha),
                end=point_dict["Z5"] * np.exp(1j * alpha),
            )
            line.plot(
                fig=fig,
                ax=ax,
                color=MAIN_LINE_COLOR,
                linestyle=MAIN_LINE_STYLE,
                linewidth=MAIN_LINE_WIDTH,
            )
            line = Segment(
                begin=point_dict["Z1s"] * np.exp(1j * alpha),
                end=point_dict["Z5s"] * np.exp(1j * alpha),
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

    # Inlined from Methods.Slot.HoleM60.remove_magnet
    def remove_magnet(self):
        """Remove the magnet (set to None) of the Hole

        Parameters
        ----------
        self : HoleM60
            a HoleM60 object
        """

        self.magnet_0 = None
        self.magnet_1 = None

    class S60_NoneError(SlotCheckError):
        """Raised when a propery of HoleM58 is None"""

    class S60_WCheckError(SlotCheckError):
        """ """
