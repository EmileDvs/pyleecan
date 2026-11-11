# Experimental dataclass generated from Generator/ClassesRef/Slot/HoleMLSRPM.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field
from typing import ClassVar

import matplotlib.pyplot as plt
import numpy as np

from ..definitions import config_dict
from ..Functions_new.labels import HOLEM_LAB, update_RTS_index
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
from .hole_mag import HoleMag
from .lam_hole import LamHole
from .magnet import Magnet
from .segment import Segment
from .surf_line import SurfLine


@dataclass(eq=False)
class HoleMLSRPM(HoleMag):
    """V shape slot for buried magnet

    Attributes
    ----------
    H1 : float
        Magnet depth
        Unit: m; Default: 0.002373479; Minimum: 0
    W0 : float
        Magnet top width
        Unit: m; Default: 0.00388; Minimum: 0
    W1 : float
        Magnet width angular 1
        Unit: rad; Default: 0.219911482; Minimum: 0
    W2 : float
        Small distance
        Unit: m; Default: 0.0007; Minimum: 0
    R1 : float
        Rounding radius
        Unit: m; Default: 0.0003; Minimum: 0
    R2 : float
        Radius 2
        Unit: m; Default: 0.019327
    R3 : float
        Radius 3
        Unit: m; Default: 0.0165
    magnet_0 : Magnet or None
        Magnet of the hole
        Default: Magnet()
    """

    IS_SYMMETRICAL: ClassVar = 1
    MAGNET_COLOR = config_dict["PLOT"]["COLOR_DICT"]["MAGNET_COLOR"]
    H1: float = 0.002373479
    """Magnet depth"""
    W0: float = 0.00388
    """Magnet top width"""
    W1: float = 0.219911482
    """Magnet width angular 1 """
    W2: float = 0.0007
    """Small distance"""
    R1: float = 0.0003
    """Rounding radius"""
    R2: float = 0.019327
    """Radius 2"""
    R3: float = 0.0165
    """Radius 3"""
    magnet_0: Magnet | None = field(
        default_factory=lambda: Magnet(), metadata={"default_class": "Magnet"}
    )
    """Magnet of the hole"""

    # Inlined from Methods.Slot.HoleMLSRPM._comp_point_coordinate
    def _comp_point_coordinate(self):
        """Compute the point coordinates needed to plot the Slot.

        Parameters
        ----------
        self : HoleMLSRPM
            A HoleMLSRPM object

        Returns
        -------
        point_dict: dict
            A dict of the slot coordinates
        """
        Rbo = self.get_Rbo()
        # Z1
        delta1 = np.arcsin((self.R1 + self.W2) / (self.R1 + self.R3))
        alpha1 = self.W1 - delta1
        Z1 = self.R3 * np.exp(-1j * alpha1)

        # Zc1
        Zc1 = (self.R3 + self.R1) * np.exp(-1j * alpha1)
        xc1 = (self.R3 + self.R1) * np.cos(alpha1)
        yc1 = -(self.R3 + self.R1) * np.sin(alpha1)

        # Z2
        x2 = (-1 / np.tan(self.W1) * xc1 + yc1 - self.W2 / np.cos(self.W1)) / -(
            np.tan(self.W1) + 1 / np.tan(self.W1)
        )
        y2 = -np.tan(self.W1) * x2 + self.W2 / np.cos(self.W1)
        Z2 = x2 + 1j * y2

        # Z3
        a3 = 1 + np.tan(self.W1) ** 2
        b3 = -2 * np.tan(self.W1) * self.W2 / np.cos(self.W1)
        c3 = (self.W2 / np.cos(self.W1)) ** 2 - self.R2**2

        x3 = (-b3 + np.sqrt(b3**2 - 4 * a3 * c3)) / (2 * a3)
        y3 = -np.tan(self.W1) * x3 + self.W2 / np.cos(self.W1)
        Z3 = x3 + 1j * y3
        # Z5
        x5 = Rbo - self.H1
        y5 = -self.W0 / 2
        Z5 = x5 + 1j * y5
        # Zc2
        xc2 = Rbo - self.H1 - self.R1
        yc2 = -self.W0 / 2
        Zc2 = xc2 + 1j * yc2
        # Z4
        a4 = (xc2 - x3) ** 2 - self.R1**2
        b4 = 2 * (xc2 - x3) * (y3 - yc2)
        c4 = (y3 - yc2) ** 2 - self.R1**2
        alpha2 = (-b4 - np.sqrt(b4**2 - 4 * a4 * c4)) / (2 * a4)
        x4 = (xc2 / alpha2 + yc2 + alpha2 * x3 - y3) / (alpha2 + 1 / alpha2)
        y4 = alpha2 * (x4 - x3) + y3
        Z4 = x4 + 1j * y4
        Zw1 = self.R2 * np.exp(1j * self.W1)
        Zw2 = Zw1 + self.W2 * np.exp(1j * -(np.pi / 2 - self.W1))
        # symmetry
        Z6 = Z5.conjugate()
        Z7 = Z4.conjugate()
        Z8 = Z3.conjugate()
        Z9 = Z2.conjugate()
        Z10 = Z1.conjugate()

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
        point_dict["Zc1"] = Zc1
        point_dict["Zc2"] = Zc2
        point_dict["Zw1"] = Zw1
        point_dict["Zw2"] = Zw2
        return point_dict

    # Inlined from Methods.Slot.HoleMLSRPM.build_geometry
    def build_geometry(self, alpha=0, delta=0, is_simplified=False):
        """Compute the curve (Line) needed to plot the Slot.
        The ending point of a curve is the starting point of the next curve in
        the list

        Parameters
        ----------
        self : HoleMLSRPM
            A HoleMLSRPM object
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
        vent_label = lam_label + "_" + surf_type + "_R" + str(R_id) + "-T0-S0"
        mag_label = lam_label + "_" + HOLEM_LAB + "_R" + str(R_id) + "-T0-S0"

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

        surf_list = []
        curve_list_mag = []
        curve_list_mag.append(Segment(Z3, Z4))
        curve_list_mag.append(Segment(Z4, Z7))
        curve_list_mag.append(Segment(Z7, Z8))
        curve_list_mag.append(Segment(Z8, Z3))

        point_ref = (Z3 + Z4 + Z7 + Z8) / 4

        # curve_list_mag = list()
        # curve_list_mag.append(
        #     Arc1(begin=Z1, end=Z2, radius=self.R1, is_trigo_direction=True)
        # )
        # curve_list_mag.append(Segment(Z2, Z3))
        # curve_list_mag.append(Segment(Z3, Z4))
        # curve_list_mag.append(
        #     Arc1(begin=Z4, end=Z5, radius=self.R1, is_trigo_direction=True)
        # )
        # curve_list_mag.append(Segment(Z5, Z6))
        # curve_list_mag.append(
        #     Arc1(begin=Z6, end=Z7, radius=self.R1, is_trigo_direction=True)
        # )
        # curve_list_mag.append(Segment(Z7, Z8))
        # curve_list_mag.append(Segment(Z8, Z9))
        # curve_list_mag.append(
        #     Arc1(begin=Z9, end=Z10, radius=self.R1, is_trigo_direction=True)
        # )
        # curve_list_mag.append(
        #     Arc1(begin=Z10, end=Z1, radius=-self.R3, is_trigo_direction=False)
        # )
        # point_ref = (Z1 + Z2 + Z3 + Z4 + Z5 + Z6 + Z7 + Z8 + Z9 + Z10) / 10
        # Defining type of magnetization of the magnet

        # if self.magnet_0:
        #     S1 = SurfLine(line_list=curve_list_mag, label=magnet_label, point_ref=point_ref)

        # else:
        #     S1 = SurfLine(line_list=curve_list_mag, label="Hole", point_ref=point_ref)

        # surf_list = [S1]

        S1 = SurfLine(line_list=curve_list_mag, label=mag_label, point_ref=point_ref)

        # Creation of the air curve (bottom)

        curve_list_air = []
        curve_list_air.append(
            Arc1(begin=Z1, end=Z2, radius=self.R1, is_trigo_direction=True)
        )
        curve_list_air.append(Segment(Z2, Z3))
        curve_list_air.append(Segment(Z3, Z8))
        curve_list_air.append(Segment(Z8, Z9))
        curve_list_air.append(
            Arc1(begin=Z9, end=Z10, radius=self.R1, is_trigo_direction=True)
        )
        curve_list_air.append(
            Arc1(begin=Z10, end=Z1, radius=-self.R3, is_trigo_direction=False)
        )
        point_ref = (Z1 + Z2 + Z3 + Z8 + Z9 + Z10) / 6

        S2 = SurfLine(line_list=curve_list_air, label=vent_label, point_ref=point_ref)

        # Creation of the second air curve (top)
        curve_list_air = []
        curve_list_air.append(
            Arc1(begin=Z4, end=Z5, radius=self.R1, is_trigo_direction=True)
        )
        curve_list_air.append(Segment(Z5, Z6))

        curve_list_air.append(
            Arc1(begin=Z6, end=Z7, radius=self.R1, is_trigo_direction=True)
        )
        curve_list_air.append(Segment(Z7, Z4))

        point_ref = (Z4 + Z5 + Z6 + Z7) / 4

        S3 = SurfLine(line_list=curve_list_air, label=vent_label, point_ref=point_ref)

        # Air without magnet (S4=S1+S2+S3)
        curve_list_air = []
        curve_list_air.append(
            Arc1(begin=Z1, end=Z2, radius=self.R1, is_trigo_direction=True)
        )
        curve_list_air.append(Segment(Z2, Z3))
        curve_list_air.append(Segment(Z3, Z4))
        curve_list_air.append(
            Arc1(begin=Z4, end=Z5, radius=self.R1, is_trigo_direction=True)
        )
        curve_list_air.append(Segment(Z5, Z6))
        curve_list_air.append(
            Arc1(begin=Z6, end=Z7, radius=self.R1, is_trigo_direction=True)
        )
        curve_list_air.append(Segment(Z7, Z8))
        curve_list_air.append(Segment(Z8, Z9))
        curve_list_air.append(
            Arc1(begin=Z9, end=Z10, radius=self.R1, is_trigo_direction=True)
        )
        curve_list_air.append(
            Arc1(begin=Z10, end=Z1, radius=-self.R3, is_trigo_direction=False)
        )
        point_ref = (Z1 + Z2 + Z3 + Z4 + Z5 + Z6 + Z7 + Z8 + Z9 + Z10) / 10

        S4 = SurfLine(line_list=curve_list_air, label=vent_label, point_ref=point_ref)

        if self.magnet_0:
            S2.label = update_RTS_index(S2.label, T_id=0)
            S3.label = update_RTS_index(S3.label, T_id=1)
            surf_list = [S1, S2, S3]
        else:
            S4.label = update_RTS_index(S4.label, T_id=0)
            surf_list = [S4]

        # Apply the transformations
        for surf in surf_list:
            surf.rotate(alpha)
            surf.translate(delta)

        return surf_list

    # Inlined from Methods.Slot.HoleMLSRPM.check
    def check(self):
        """Check that the HoleMLSRPM object is correct

        Parameters
        ----------
        self : HoleMLSRPM
            A HoleMLSRPM object

        Returns
        -------
        None

        Raises
        -------

        """

        # Check that everything is set
        if self.W0 is None:
            raise self.SLSRPM_NoneError("You must set W0 !")
        elif self.W1 is None:
            raise self.SLSRPM_NoneError("You must set W1 !")
        elif self.W2 is None:
            raise self.SLSRPM_NoneError("You must set W2 !")
        elif self.H1 is None:
            raise self.SLSRPM_NoneError("You must set H1 !")
        elif self.R1 is None:
            raise self.SLSRPM_NoneError("You must set R1 !")
        elif self.R2 is None:
            raise self.SLSRPM_NoneError("You must set R2 !")
        elif self.R3 is None:
            raise self.SLSRPM_NoneError("You must set R3 !")
        elif self.magnet_0 is None:
            raise self.SLSRPM_NoneError("You must set magnet_0 !")

    # Inlined from Methods.Slot.HoleMLSRPM.comp_magnetization_dict
    def comp_magnetization_dict(self, is_north=True):
        """Compute the dictionary of the magnetization direction of the magnets (key=magnet_X, value=angle[rad])
        Mangetization angle with Hole centered on Ox axis

        Parameters
        ----------
        self : HoleMLSRPM
            a HoleMLSRPM object
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
        Z3 = point_dict["Z3"]
        Z4 = point_dict["Z4"]
        Z7 = point_dict["Z7"]
        Z8 = point_dict["Z8"]

        Zch = (Z3 + Z4) / 2
        Zcl = (Z7 + Z8) / 2
        S0 = Segment(Zch, Zcl)
        mag_dict["magnet_0"] = S0.comp_normal()

        ####Comp_normal direction?

        if not is_north:
            mag_dict["magnet_0"] += np.pi

        if self.magnetization_dict_offset is not None:
            for key, value in self.magnetization_dict_offset:
                mag_dict[key] += value

        return mag_dict

    # Inlined from Methods.Slot.HoleMLSRPM.comp_mass_magnet
    def comp_mass_magnet(self):
        """Compute the mass of the magnet (if any)

        Parameters
        ----------
        self : HoleMLSRPM
            A HoleMLSRPM object

        Returns
        -------
        Mmag: float
            mass of the magnet [kg]

        """

        # Simplify the calculate of the magnet surface
        V_magnet = self.comp_volume_magnet()

        if self.magnet_0:
            return V_magnet * self.magnet_0.mat_type.struct.rho
        else:
            return 0

    # Inlined from Methods.Slot.HoleMLSRPM.comp_surface_magnet
    def comp_surface_magnet(self):
        """Compute the surface of the Hole

        Parameters
        ----------
        self : HoleMLSRPM
            A HoleMLSRPM object

        Returns
        -------
        S: float
            Surface of the Magnet. [m**2]

        """

        point_dict = self._comp_point_coordinate()
        Z3 = point_dict["Z3"]
        Z4 = point_dict["Z4"]
        Z7 = point_dict["Z7"]
        Z8 = point_dict["Z8"]

        # symmetry

        x3 = Z3.real
        y3 = Z3.imag
        x4 = Z4.real
        y4 = Z4.imag

        x7 = Z7.real
        y7 = Z7.imag
        x8 = Z8.real
        y8 = Z8.imag

        S_magnet_1 = x3 * y4 + x4 * y7 + x7 * y8 + x8 * y3
        S_magnet_2 = x3 * y8 + x4 * y3 + x7 * y4 + x8 * y7

        S_magnet = 0.5 * abs(S_magnet_1 - S_magnet_2)

        return S_magnet

    # Inlined from Methods.Slot.HoleMLSRPM.comp_volume_magnet
    def comp_volume_magnet(self):
        """Compute the volume of the magnet (if any)

        Parameters
        ----------
        self : HoleMLSRPM
            A HoleMLSRPM object

        Returns
        -------
        Vmag: float
            Volume of the magnet [m**3]

        """
        S_magnet = self.comp_surface_magnet()

        if self.magnet_0:
            return S_magnet * self.magnet_0.Lmag
        else:
            return 0

    # Inlined from Methods.Slot.HoleMLSRPM.has_magnet
    def has_magnet(self):
        """Return if the Hole has magnets

        Parameters
        ----------
        self : HoleMLSRPM
            A HoleMLSRPM object

        Returns
        -------
        has_magnet : bool
            True if the magnets are not None
        """

        return self.magnet_0 is not None

    # Inlined from Methods.Slot.HoleMLSRPM.plot_schematics
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
        self : HoleMLSRPM
            A HoleMLSRPM object
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
            0: No active surface, 2: active surface as magnet
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
        lam : LamHole / LamSlot
            Default lamination used for the schematics
        """

        # Use some default parameter
        if is_default:
            hole = type(self)(
                Zh=8,
                H1=0.002373479,
                W0=3.88e-03,
                W1=12.6 / 180 * np.pi,
                W2=0.0007,
                R1=0.0003,
                R2=0.019327,
                R3=0.0165,
            )
            lam = LamHole(
                Rint=14e-3,
                Rext=50e-3,
                is_internal=True,
                is_stator=False,
                L1=0.105,
                Nrvd=2,
                Wrvd=0.05,
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
            alpha = 0  # To rotate the schematics
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
                # H1
                line = Segment(
                    (point_dict["Z5"] + point_dict["Z6"]) / 2 * np.exp(1j * alpha),
                    Rbo * np.exp(1j * alpha),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="H1",
                    offset_label=self.H1 + 1j * self.H1 * 0.25,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )

                # W0
                line = Segment(
                    point_dict["Z5"] * np.exp(1j * alpha),
                    point_dict["Z6"] * np.exp(1j * alpha),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="W0",
                    offset_label=-0.005,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # R1
                line = Segment(
                    point_dict["Zc1"] * np.exp(1j * alpha),
                    point_dict["Z2"] * np.exp(1j * alpha),
                )

                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="R1",
                    offset_label=self.H1,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # R2
                line = Segment(
                    0 * np.exp(1j * alpha),
                    point_dict["Z8"].real * np.exp(1j * (alpha)),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="R2",
                    offset_label=self.H1,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # R3
                line = Segment(
                    0 * np.exp(1j * alpha),
                    point_dict["Z10"] * np.exp(1j * (alpha)),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="R3",
                    offset_label=-self.H1 * 2,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )

                # W1
                line = Segment(
                    self.R2 * np.exp(1j * alpha),
                    point_dict["Zw1"] * np.exp(1j * (alpha)),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="W1",
                    offset_label=0.00065,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )

                # W2
                line = Segment(
                    (point_dict["Zw2"] + 0.005 * np.exp(1j * self.W1))
                    * np.exp(1j * (alpha)),
                    (point_dict["Zw1"] + 0.005 * np.exp(1j * self.W1))
                    * np.exp(1j * (alpha)),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="W2",
                    offset_label=1j * 0.0015 - 0.003,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )

                ### TODO:W1 W2

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
                # Guide line 1
                line = Segment(
                    0, lam.Rext * 1.5 * np.exp(1j * (alpha + 12.6 / 180 * np.pi))
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # Guide line 2
                line = Segment(
                    0 - 1j * 0.0007 / np.cos(12.6 / 180 * np.pi),
                    lam.Rext * 1.5 * np.exp(1j * (alpha + 12.6 / 180 * np.pi))
                    - 1j * 0.0007 / np.cos(12.6 / 180 * np.pi),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # R1 radius
                line = Arc1(
                    begin=point_dict["Z1"],
                    end=point_dict["Z2"],
                    radius=self.R1,
                    is_trigo_direction=True,
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )

                # W1 radius

                line = Arc1(
                    begin=point_dict["Zw1"] * np.exp(1j * alpha),
                    end=self.R2 * np.exp(1j * alpha),
                    radius=self.R2,
                    is_trigo_direction=True,
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
                    point_dict["Z8"] * np.exp(1j * alpha),
                    point_dict["Z3"] * np.exp(1j * alpha),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                line = Segment(
                    point_dict["Z7"] * np.exp(1j * alpha),
                    point_dict["Z4"] * np.exp(1j * alpha),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )

            # Zooming and cleaning
            W = 4e-3
            Rint = self.R3 * 0.9
            Rext = self.parent.Rext * 1.2

            # ax.axis("equal")
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

    # Inlined from Methods.Slot.HoleMLSRPM.remove_magnet
    def remove_magnet(self):
        """Remove the magnet (set to None) of the Hole

        Parameters
        ----------
        self : HoleMLSRPM
            a HoleMLSRPM object
        """

        self.magnet_0 = None

    class SLSRPM_NoneError(SlotCheckError):
        """Raised when a propery of HoleM52 is None"""
