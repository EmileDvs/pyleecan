# Experimental dataclass generated from Generator/ClassesRef/Slot/HoleM57.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field
from typing import ClassVar

import matplotlib.pyplot as plt
import numpy as np

from ..definitions import config_dict
from ..Functions_new.Geometry.inter_line_line import inter_line_line
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
from .hole_mag import HoleMag
from .lam_hole import LamHole
from .magnet import Magnet
from .segment import Segment
from .surf_line import SurfLine


@dataclass(eq=False)
class HoleM57(HoleMag):
    """V shape slot for buried magnet

    Attributes
    ----------
    W0 : float
        V angle
        Unit: rad; Default: 0.2; Minimum: 0; Maximum: 3.15
    H1 : float
        Distance from the lamination Bore
        Unit: m; Default: 0; Minimum: 0
    W1 : float
        Tooth width (at V bottom)
        Unit: m; Default: 0.013; Minimum: 0
    H2 : float
        Magnet height
        Unit: m; Default: 0.02; Minimum: 0
    W2 : float
        Distance Magnet to top of the V
        Unit: m; Default: 0.01; Minimum: 0
    W3 : float
        Tooth width (at V top)
        Unit: m; Default: 0.01; Minimum: 0
    W4 : float
        Magnet Width
        Unit: m; Default: 0.01; Minimum: 0
    magnet_0 : Magnet or None
        First Magnet
        Default: Magnet()
    magnet_1 : Magnet or None
        Second Magnet
        Default: Magnet()
    """

    IS_SYMMETRICAL: ClassVar = 1
    MAGNET_COLOR = config_dict["PLOT"]["COLOR_DICT"]["MAGNET_COLOR"]
    W0: float = 0.2
    """V angle"""
    H1: float = 0
    """Distance from the lamination Bore"""
    W1: float = 0.013
    """Tooth width (at V bottom)"""
    H2: float = 0.02
    """Magnet height"""
    W2: float = 0.01
    """Distance Magnet to top of the V"""
    W3: float = 0.01
    """Tooth width (at V top)"""
    W4: float = 0.01
    """Magnet Width"""
    magnet_0: Magnet | None = field(
        default_factory=lambda: Magnet(), metadata={"default_class": "Magnet"}
    )
    """First Magnet"""
    magnet_1: Magnet | None = field(
        default_factory=lambda: Magnet(), metadata={"default_class": "Magnet"}
    )
    """Second Magnet"""

    # Inlined from Methods.Slot.HoleM57._comp_point_coordinate
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

        # "Tooth" angle (P1',0,P1)
        alpha_T = 2 * np.arcsin(self.W3 / (2 * (Rext - self.H1)))
        # magnet pole pitch angle (Z1,0,Z1')
        alpha_S = (2 * np.pi / self.Zh) - alpha_T
        # Angle (P1,P1',P4') and (P5',P4', )
        alpha = (np.pi - self.W0) / 2
        # Half slot pitch
        hssp = np.pi / self.Zh

        Z1 = (Rext - self.H1) * np.exp(-1j * alpha_S / 2)
        x11 = 2 * np.sin(alpha_S / 2) * (Rext - self.H1)  # Distance from P1 to P1'
        # In rect triangle P4, P1, perp (P1,P1') with P4
        H = np.tan(alpha) * (x11 / 2 - self.W1 / 2)
        Z4 = Z1.real - H - 1j * self.W1 / 2

        x45 = self.H2 / np.cos(alpha)  # distance from P4 to P5
        Z5 = Z4 - x45

        # Get coordinates of "random" points on (P5,P8) and (P1,P8)
        # In ref P4 center and P1 on X+ axis
        Z58 = (self.W4 - 1j * self.H2) * np.exp(1j * np.angle(Z1 - Z4)) + Z4
        # In the tooth ref
        Z18 = (Rext - self.H1 - self.H2 + 1j * self.W3 / 2) * np.exp(-1j * hssp)
        Z8 = inter_line_line(Z5, Z58, Z1, Z18)[0]

        # In ref "b" P4 center and P1 on X+ axis
        Z8b = (Z8 - Z4) * np.exp(-1j * np.angle(Z1 - Z4))
        Z9 = (Z8b + 1j * self.H2) * np.exp(1j * np.angle(Z1 - Z4)) + Z4
        Z2 = (Z8b + 1j * self.H2 - self.W2) * np.exp(1j * np.angle(Z1 - Z4)) + Z4
        Z3 = (Z8b + 1j * self.H2 - self.W2 - self.W4) * np.exp(
            1j * np.angle(Z1 - Z4)
        ) + Z4
        Z7 = (Z8b - self.W2) * np.exp(1j * np.angle(Z1 - Z4)) + Z4
        Z6 = (Z8b - self.W2 - self.W4) * np.exp(1j * np.angle(Z1 - Z4)) + Z4

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

        # Symmetry
        point_dict["Z1s"] = Z1.conjugate()
        point_dict["Z2s"] = Z2.conjugate()
        point_dict["Z3s"] = Z3.conjugate()
        point_dict["Z4s"] = Z4.conjugate()
        point_dict["Z5s"] = Z5.conjugate()
        point_dict["Z6s"] = Z6.conjugate()
        point_dict["Z7s"] = Z7.conjugate()
        point_dict["Z8s"] = Z8.conjugate()
        point_dict["Z9s"] = Z9.conjugate()
        point_dict["Zc0"] = inter_line_line(
            Z3, Z2, point_dict["Z3s"], point_dict["Z2s"]
        )[0]
        return point_dict

    # Inlined from Methods.Slot.HoleM57.build_geometry
    def build_geometry(self, alpha=0, delta=0, is_simplified=False):
        """Compute the curve (Segment) needed to plot the Slot.
        The ending point of a curve is the starting point of the next curve in
        the list

        Parameters
        ----------
        self : HoleM57
            A HoleM57 object
        alpha : float
            Angle to rotate the slot (Default value = 0) [rad]
        delta : complex
            Complex to translate the slot (Default value = 0)
        is_simplified : bool
           True to avoid line superposition

        Returns
        -------
        surf_list: list
            List of SurfLine needed to draw the HoleM57

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
        Z3 = point_dict["Z3"]
        Z4 = point_dict["Z4"]
        Z5 = point_dict["Z5"]
        Z6 = point_dict["Z6"]
        Z7 = point_dict["Z7"]
        Z8 = point_dict["Z8"]

        Z1s = point_dict["Z1s"]
        Z2s = point_dict["Z2s"]
        Z3s = point_dict["Z3s"]
        Z4s = point_dict["Z4s"]
        Z5s = point_dict["Z5s"]
        Z6s = point_dict["Z6s"]
        Z7s = point_dict["Z7s"]
        Z8s = point_dict["Z8s"]

        surf_list = []
        # Z_list = array([Z1, Z2, Z3, Z4, Z5, Z6, Z7, Z8])
        # plt.plot(Z_list.real, Z_list.imag, "x r")
        # for ii in range(8):
        #     plt.text(Z_list[ii].real, Z_list[ii].imag, "Z" + str(ii + 1))
        # plt.show()
        # Check schematics:
        assert abs(abs(Z7 - Z8) - self.W2) < 1e-6
        assert abs(abs(Z6 - Z7) - self.W4) < 1e-6
        assert abs(abs(Z2 - Z3) - self.W4) < 1e-6
        assert abs(abs(Z2 - Z7) - self.H2) < 1e-6
        assert abs(abs(Z4 - Z4s) - self.W1) < 1e-6
        assert abs(abs(Z5 - Z5s) - self.W1) < 1e-6
        # TODO: Create all the surfaces for all the cases
        # (with/without magnet W1>0 or W1=0)
        # Air surface (W3) with magnet_0
        curve_list = []
        curve_list.append(Segment(begin=Z1, end=Z2))
        curve_list.append(Segment(begin=Z2, end=Z7))
        if self.W2 > 0:
            curve_list.append(Segment(begin=Z7, end=Z8))
        curve_list.append(Segment(begin=Z8, end=Z1))

        # initiating the label of the line on the air surface
        # curve_list = set_name_line(curve_list, "hole_1_line")
        point_ref = (Z1 + Z2 + Z7 + Z8) / 4
        S1 = SurfLine(
            line_list=curve_list, label=vent_label + "T0-S0", point_ref=point_ref
        )

        # Magnet_0 surface
        curve_list = []
        if is_simplified:
            curve_list.append(Segment(begin=Z7, end=Z2))
            curve_list.append(Segment(begin=Z3, end=Z6))
        else:
            curve_list.append(Segment(begin=Z2, end=Z3))
            curve_list.append(Segment(begin=Z3, end=Z6))
            curve_list.append(Segment(begin=Z6, end=Z7))
            curve_list.append(Segment(begin=Z7, end=Z2))

        # initiating the label of the line of the magnet surface
        # curve_list = set_name_line(curve_list, "magnet_1_line")
        point_ref = (Z2 + Z3 + Z6 + Z7) / 4
        S2 = SurfLine(
            line_list=curve_list,
            label=mag_label + "T0-S0",
            point_ref=point_ref,
        )

        # Air surface with magnet_0 and W1 > 0
        curve_list = []
        curve_list.append(Segment(begin=Z4, end=Z5))
        curve_list.append(Segment(begin=Z5, end=Z6))
        curve_list.append(Segment(begin=Z6, end=Z3))
        if abs(Z4 - Z3) > 1e-6:
            curve_list.append(Segment(begin=Z3, end=Z4))

        # initiating the label of the line on the air surface
        # curve_list = set_name_line(curve_list, "hole_2_line")
        point_ref = (Z6 + Z5 + Z4) / 3

        S3 = SurfLine(
            line_list=curve_list, label=vent_label + "T1-S0", point_ref=point_ref
        )

        # Symmetry Air surface (W3) with magnet_1
        curve_list = []
        curve_list.append(Segment(begin=Z2s, end=Z1s))
        curve_list.append(Segment(begin=Z1s, end=Z8s))
        if self.W2 > 0:
            curve_list.append(Segment(begin=Z8s, end=Z7s))
        curve_list.append(Segment(begin=Z7s, end=Z2s))
        point_ref = (Z1s + Z2s + Z8s + Z7s) / 4
        # initiating the label of the line on the air surface
        # curve_list = set_name_line(curve_list, "hole_3_line")
        S4 = SurfLine(
            line_list=curve_list, label=vent_label + "T2-S0", point_ref=point_ref
        )

        # magnet_1 surface
        curve_list = []
        if is_simplified:
            curve_list.append(Segment(begin=Z2s, end=Z7s))
            curve_list.append(Segment(begin=Z6s, end=Z3s))
        else:
            curve_list.append(Segment(begin=Z3s, end=Z2s))
            curve_list.append(Segment(begin=Z2s, end=Z7s))
            curve_list.append(Segment(begin=Z7s, end=Z6s))
            curve_list.append(Segment(begin=Z6s, end=Z3s))
        point_ref = (Z3s + Z2s + Z7s + Z6s) / 4

        # initiating the label of the line on the magnet surface
        # curve_list = set_name_line(curve_list, "magnet_2_line")
        S5 = SurfLine(
            line_list=curve_list,
            label=mag_label + "T1-S0",
            point_ref=point_ref,
        )

        # Air surface with magnet_1 and W1 > 0
        curve_list = []
        curve_list.append(Segment(begin=Z3s, end=Z6s))
        curve_list.append(Segment(begin=Z6s, end=Z5s))
        curve_list.append(Segment(begin=Z5s, end=Z4s))
        if abs(Z4 - Z3) > 1e-6:
            curve_list.append(Segment(begin=Z4s, end=Z3s))

        point_ref = (Z3s + Z6s + Z5s) / 3

        # initiating the label of the line on the air surface
        # curve_list = set_name_line(curve_list, "hole_4_line")
        S6 = SurfLine(
            line_list=curve_list, label=vent_label + "T1-S0", point_ref=point_ref
        )

        # Air surface between magnet_0 and magnet_1 with W1 == 0
        curve_list = []
        curve_list.append(Segment(begin=Z3, end=Z4))
        curve_list.append(Segment(begin=Z4, end=Z3s))
        curve_list.append(Segment(begin=Z3s, end=Z6s))
        curve_list.append(Segment(begin=Z6s, end=Z5))
        curve_list.append(Segment(begin=Z5, end=Z6))
        curve_list.append(Segment(begin=Z6, end=Z3))

        # initiating the label of the line on the air surface
        # curve_list = set_name_line(curve_list, "hole_2_line")
        point_ref = (Z5 + Z4) / 2

        S7 = SurfLine(
            line_list=curve_list, label=vent_label + "T2-S0", point_ref=point_ref
        )

        # Air surface without magnet_0 and W1 > 0
        curve_list = []
        curve_list.append(Segment(begin=Z1, end=Z8))
        curve_list.append(Segment(begin=Z8, end=Z5))
        curve_list.append(Segment(begin=Z5, end=Z4))
        curve_list.append(Segment(begin=Z4, end=Z1))

        # initiating the label of the line on the air surface
        # curve_list = set_name_line(curve_list, "hole_1_line")
        point_ref = (Z5 + Z1) / 2

        S8 = SurfLine(
            line_list=curve_list, label=vent_label + "T1-S0", point_ref=point_ref
        )

        # Air surface without magnet_1 and W1 > 0
        curve_list = []
        curve_list.append(Segment(begin=Z1s, end=Z8s))
        curve_list.append(Segment(begin=Z8s, end=Z5s))
        curve_list.append(Segment(begin=Z5s, end=Z4s))
        curve_list.append(Segment(begin=Z4s, end=Z1s))

        # initiating the label of the line on the air surface
        # curve_list = set_name_line(curve_list, "hole_2_line")
        point_ref = (Z5s + Z1s) / 2

        S9 = SurfLine(
            line_list=curve_list, label=vent_label + "T0-S0", point_ref=point_ref
        )

        # Air surface No magnet and W1 == 0
        curve_list = []
        curve_list.append(Segment(begin=Z4, end=Z1))
        curve_list.append(Segment(begin=Z1, end=Z8))
        curve_list.append(Segment(begin=Z8, end=Z5))
        curve_list.append(Segment(begin=Z5, end=Z8s))
        curve_list.append(Segment(begin=Z8s, end=Z1s))
        curve_list.append(Segment(begin=Z1s, end=Z4))

        # initiating the label of the line on the air surface
        # curve_list = set_name_line(curve_list, "hole_1_line")
        point_ref = (Z4 + Z5) / 2

        S12 = SurfLine(
            line_list=curve_list, label=vent_label + "T0-S0", point_ref=point_ref
        )

        # TODO correct vent_label TX id
        # Create the surface list by selecting the correct ones
        if self.magnet_0 and self.magnet_1 and self.W1 > 0:
            surf_list = [S1, S2, S3, S6, S5, S4]
        elif self.magnet_0 and self.magnet_1 and self.W1 == 0:
            surf_list = [S1, S2, S7, S5, S4]
        # elif self.magnet_0 and not self.magnet_1 and self.W1 > 0:
        #     surf_list = [S1, S2, S3, S9]
        # elif self.magnet_0 and not self.magnet_1 and self.W1 == 0:
        #     surf_list = [S1, S2, S10]
        # elif not self.magnet_0 and self.magnet_1 and self.W1 > 0:
        #     surf_list = [S8, S6, S5, S4]
        # elif not self.magnet_0 and self.magnet_1 and self.W1 == 0:
        #     surf_list = [S11, S5, S4]
        elif not self.magnet_0 and not self.magnet_1 and self.W1 > 0:
            surf_list = [S8, S9]
        elif not self.magnet_0 and not self.magnet_1 and self.W1 == 0:
            surf_list = [S12]
        else:
            raise Exception("Not implemented Yet")

        # Apply the transformations
        for surf in surf_list:
            surf.rotate(alpha)
            surf.translate(delta)

        return surf_list

    # Inlined from Methods.Slot.HoleM57.check
    def check(self):
        """Check that the HoleM57 object is correct

        Parameters
        ----------
        self : HoleM57
            A HoleM57 object

        Returns
        -------
        None

        Raises
        _______
        """
        # Check that everything is set
        if self.W0 is None:
            raise self.S57_NoneError("You must set W0 !")
        elif self.W1 is None:
            raise self.S57_NoneError("You must set W1 !")
        elif self.W2 is None:
            raise self.S57_NoneError("You must set W2 !")
        elif self.W3 is None:
            raise self.S57_NoneError("You must set W3 !")
        elif self.W4 is None:
            raise self.S57_NoneError("You must set W4 !")
        elif self.H1 is None:
            raise self.S57_NoneError("You must set H1 !")
        elif self.H2 is None:
            raise self.S57_NoneError("You must set H2 !")

    # Inlined from Methods.Slot.HoleM57.comp_magnetization_dict
    def comp_magnetization_dict(self, is_north=True):
        """Compute the dictionary of the magnetization direction of the magnets (key=magnet_X, value=angle[rad])
        Mangetization angle with Hole centered on Ox axis

        Parameters
        ----------
        self : HoleM57
            a HoleM57 object
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
        S0 = Segment(begin=point_dict["Z6"], end=point_dict["Z7"])
        mag_dict["magnet_0"] = S0.comp_normal()
        S1 = Segment(begin=point_dict["Z7s"], end=point_dict["Z6s"])
        mag_dict["magnet_1"] = S1.comp_normal()

        if not is_north:
            mag_dict["magnet_0"] += np.pi
            mag_dict["magnet_1"] += np.pi

        if self.magnetization_dict_offset is not None:
            for key, value in self.magnetization_dict_offset:
                mag_dict[key] += value

        return mag_dict

    # Inlined from Methods.Slot.HoleM57.comp_radius
    def comp_radius(self):
        """Compute the radius of the min and max circle that contains the slot

        Parameters
        ----------
        self : HoleM57
            A HoleM57 object

        Returns
        -------
        (Rmin,Rmax): tuple
            Radius of the circle that contains the slot [m]
        """
        Rext = self.get_Rext()

        Rmax = Rext - self.H1
        Rmin = abs(self._comp_point_coordinate()["Z5"])

        return (Rmin, Rmax)

    # Inlined from Methods.Slot.HoleM57.comp_surface_magnet_id
    def comp_surface_magnet_id(self, index):
        """Compute the surface of the hole magnet of the corresponding index

        Parameters
        ----------
        self : HoleM57
            A HoleM57 object
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
            return self.H2 * self.W4
        return 0

    # Inlined from Methods.Slot.HoleM57.has_magnet
    def has_magnet(self):
        """Return if the Hole has magnets

        Parameters
        ----------
        self : HoleM57
            A HoleM57 object

        Returns
        -------
        has_magnet : bool
            True if the magnets are not None
        """

        return self.magnet_0 is not None or self.magnet_1 is not None

    # Inlined from Methods.Slot.HoleM57.plot_schematics
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
        self : HoleM57
            A HoleM57 object
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
        lam : LamHole  / LamSlot
            Default lamination used for the schematics
        """

        # Use some default parameter
        if is_default:
            hole = type(self)(
                Zh=8,
                W0=np.pi * 0.8,
                W1=10e-3,
                W2=7.5e-3,
                W3=5e-3,
                W4=15e-3,
                H1=3e-3,
                H2=5e-3,
            )
            lam = LamHole(
                Rint=0.078, Rext=0.104, is_internal=True, is_stator=False, hole=[hole]
            )
            if is_return_default:
                return lam
            else:
                return hole.plot_schematics(
                    is_default=False,
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
                # W0
                line = Arc1(
                    begin=point_dict["Z3"] * np.exp(1j * alpha),
                    end=point_dict["Z3s"] * np.exp(1j * alpha),
                    radius=abs(point_dict["Z3"] - point_dict["Zc0"]),
                    is_trigo_direction=True,
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="W0",
                    offset_label=(1 + 1j) * self.H1 * 0.5,
                    fontsize=SC_FONT_SIZE,
                )
                # W1
                line = Segment(
                    begin=(point_dict["Z4"] + point_dict["Z5"])
                    / 2
                    * np.exp(1j * alpha),
                    end=(point_dict["Z4s"] + point_dict["Z5s"])
                    / 2
                    * np.exp(1j * alpha),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="W1",
                    offset_label=-1j * self.H1,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )

                if type_add_active != 0:
                    # W2
                    line = Segment(
                        begin=(point_dict["Z9"] + point_dict["Z8"])
                        / 2
                        * np.exp(1j * alpha),
                        end=(point_dict["Z2"] + point_dict["Z7"])
                        / 2
                        * np.exp(1j * alpha),
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
                    # W4
                    line = Segment(
                        begin=(point_dict["Z3"] + point_dict["Z6"])
                        / 2
                        * np.exp(1j * alpha),
                        end=(point_dict["Z2"] + point_dict["Z7"])
                        / 2
                        * np.exp(1j * alpha),
                    )
                    line.plot(
                        fig=fig,
                        ax=ax,
                        color=ARROW_COLOR,
                        linewidth=ARROW_WIDTH,
                        label="W4",
                        offset_label=-1j * self.H1,
                        is_arrow=True,
                        fontsize=SC_FONT_SIZE,
                    )

                # W3
                line = Segment(
                    begin=(point_dict["Z1"] + point_dict["Z8"])
                    / 2
                    * np.exp(1j * alpha),
                    end=(point_dict["Z1s"] + point_dict["Z8s"])
                    / 2
                    * np.exp(-1j * sp)
                    * np.exp(1j * alpha),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="W3",
                    offset_label=-1j * self.H1 * 1.3,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )

                # H1
                line = Segment(
                    begin=(lam.Rext - self.H1)
                    * np.exp(1j * sp / 2)
                    * np.exp(1j * alpha),
                    end=lam.Rext * np.exp(1j * sp / 2) * np.exp(1j * alpha),
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
                # H2
                line = Segment(
                    begin=point_dict["Z2s"] * np.exp(1j * alpha),
                    end=point_dict["Z7s"] * np.exp(1j * alpha),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="H2",
                    offset_label=self.H1 * 0.7,
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
                    begin=0,
                    end=lam.Rext * 1.5 * np.exp(1j * sp / 2) * np.exp(1j * alpha),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                line = Segment(
                    begin=0,
                    end=lam.Rext * 1.5 * np.exp(-1j * sp / 2) * np.exp(1j * alpha),
                )
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
                    * np.exp(-1j * np.pi / 2 * 0.9)
                    * np.exp(1j * alpha),
                    end=(Rbo - self.H1)
                    * np.exp(1j * np.pi / 2 * 0.9)
                    * np.exp(1j * alpha),
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
                # W2 lines
                line = Segment(
                    begin=point_dict["Z9"] * np.exp(1j * alpha),
                    end=point_dict["Z8"] * np.exp(1j * alpha),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                line = Segment(
                    begin=point_dict["Z9s"] * np.exp(1j * alpha),
                    end=point_dict["Z8s"] * np.exp(1j * alpha),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # Zc0 lines
                line = Segment(
                    begin=point_dict["Zc0"] * np.exp(1j * alpha),
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
                    begin=point_dict["Zc0"] * np.exp(1j * alpha),
                    end=point_dict["Z4s"] * np.exp(1j * alpha),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )

            # Zooming and cleaning
            W = (point_dict["Z1"] * np.exp(1j * sp)).imag
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

    # Inlined from Methods.Slot.HoleM57.remove_magnet
    def remove_magnet(self):
        """Remove the magnet (set to None) of the Hole

        Parameters
        ----------
        self : HoleM57
            a HoleM57 object
        """

        self.magnet_0 = None
        self.magnet_1 = None

    class S57_NoneError(SlotCheckError):
        """Raised when a propery of HoleM57 is None"""
