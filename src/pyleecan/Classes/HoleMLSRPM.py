# File generated according to Generator/ClassesRef/Slot/HoleMLSRPM.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Slot/HoleMLSRPM"""

from os import linesep
from sys import getsizeof

import matplotlib.pyplot as plt
import numpy as np
from pyleecan.Classes import ParentMissingError
from pyleecan.Classes.Arc1 import Arc1
from pyleecan.Classes.HoleMag import HoleMag
from pyleecan.Classes.LamHole import LamHole
from pyleecan.Classes.Segment import Segment
from pyleecan.Classes.SurfLine import SurfLine
from pyleecan.Classes._check import check_var
from pyleecan.definitions import config_dict
from pyleecan.Functions.Load.import_class import import_class
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
from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.labels import HOLEM_LAB, update_RTS_index
from pyleecan.Functions.load import load_init_dict
from pyleecan.Functions.save import save


class HoleMLSRPM(HoleMag):
    """V shape slot for buried magnet"""

    VERSION = 1
    IS_SYMMETRICAL = 1
    MAGNET_COLOR = config_dict["PLOT"]["COLOR_DICT"]["MAGNET_COLOR"]

    # cf Methods.Slot.HoleMLSRPM._comp_point_coordinate
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
        point_dict["Zc1"] = Zc1
        point_dict["Zc2"] = Zc2
        point_dict["Zw1"] = Zw1
        point_dict["Zw2"] = Zw2
        return point_dict

    # cf Methods.Slot.HoleMLSRPM.build_geometry
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

        surf_list = list()
        curve_list_mag = list()
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

        curve_list_air = list()
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
        curve_list_air = list()
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
        curve_list_air = list()
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

    # cf Methods.Slot.HoleMLSRPM.check
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
            raise SLSRPM_NoneError("You must set W0 !")
        elif self.W1 is None:
            raise SLSRPM_NoneError("You must set W1 !")
        elif self.W2 is None:
            raise SLSRPM_NoneError("You must set W2 !")
        elif self.H1 is None:
            raise SLSRPM_NoneError("You must set H1 !")
        elif self.R1 is None:
            raise SLSRPM_NoneError("You must set R1 !")
        elif self.R2 is None:
            raise SLSRPM_NoneError("You must set R2 !")
        elif self.R3 is None:
            raise SLSRPM_NoneError("You must set R3 !")
        elif self.magnet_0 is None:
            raise SLSRPM_NoneError("You must set magnet_0 !")

    # cf Methods.Slot.HoleMLSRPM.comp_magnetization_dict
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

        mag_dict = dict()
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

    # cf Methods.Slot.HoleMLSRPM.comp_mass_magnet
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

    # cf Methods.Slot.HoleMLSRPM.comp_surface_magnet
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

    # cf Methods.Slot.HoleMLSRPM.comp_volume_magnet
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

    # cf Methods.Slot.HoleMLSRPM.has_magnet
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

    # cf Methods.Slot.HoleMLSRPM.plot_schematics
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

    # cf Methods.Slot.HoleMLSRPM.remove_magnet
    def remove_magnet(self):
        """Remove the magnet (set to None) of the Hole

        Parameters
        ----------
        self : HoleMLSRPM
            a HoleMLSRPM object
        """

        self.magnet_0 = None

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        H1=0.002373479,
        W0=0.00388,
        W1=0.219911482,
        W2=0.0007,
        R1=0.0003,
        R2=0.019327,
        R3=0.0165,
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
            if "H1" in list(init_dict.keys()):
                H1 = init_dict["H1"]
            if "W0" in list(init_dict.keys()):
                W0 = init_dict["W0"]
            if "W1" in list(init_dict.keys()):
                W1 = init_dict["W1"]
            if "W2" in list(init_dict.keys()):
                W2 = init_dict["W2"]
            if "R1" in list(init_dict.keys()):
                R1 = init_dict["R1"]
            if "R2" in list(init_dict.keys()):
                R2 = init_dict["R2"]
            if "R3" in list(init_dict.keys()):
                R3 = init_dict["R3"]
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
        self.H1 = H1
        self.W0 = W0
        self.W1 = W1
        self.W2 = W2
        self.R1 = R1
        self.R2 = R2
        self.R3 = R3
        self.magnet_0 = magnet_0
        # Call HoleMag init
        super(HoleMLSRPM, self).__init__(
            Zh=Zh,
            mat_void=mat_void,
            magnetization_dict_offset=magnetization_dict_offset,
            Alpha0=Alpha0,
        )
        # The class is frozen (in HoleMag init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        HoleMLSRPM_str = ""
        # Get the properties inherited from HoleMag
        HoleMLSRPM_str += super(HoleMLSRPM, self).__str__()
        HoleMLSRPM_str += "H1 = " + str(self.H1) + linesep
        HoleMLSRPM_str += "W0 = " + str(self.W0) + linesep
        HoleMLSRPM_str += "W1 = " + str(self.W1) + linesep
        HoleMLSRPM_str += "W2 = " + str(self.W2) + linesep
        HoleMLSRPM_str += "R1 = " + str(self.R1) + linesep
        HoleMLSRPM_str += "R2 = " + str(self.R2) + linesep
        HoleMLSRPM_str += "R3 = " + str(self.R3) + linesep
        if self.magnet_0 is not None:
            tmp = self.magnet_0.__str__().replace(linesep, linesep + "\t").rstrip("\t")
            HoleMLSRPM_str += "magnet_0 = " + tmp
        else:
            HoleMLSRPM_str += "magnet_0 = None" + linesep + linesep
        return HoleMLSRPM_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from HoleMag
        if not super(HoleMLSRPM, self).__eq__(other):
            return False
        if other.H1 != self.H1:
            return False
        if other.W0 != self.W0:
            return False
        if other.W1 != self.W1:
            return False
        if other.W2 != self.W2:
            return False
        if other.R1 != self.R1:
            return False
        if other.R2 != self.R2:
            return False
        if other.R3 != self.R3:
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
            super(HoleMLSRPM, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
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
            other._R1 is not None
            and self._R1 is not None
            and np.isnan(other._R1)
            and np.isnan(self._R1)
        ):
            pass
        elif other._R1 != self._R1:
            if is_add_value:
                val_str = " (self=" + str(self._R1) + ", other=" + str(other._R1) + ")"
                diff_list.append(name + ".R1" + val_str)
            else:
                diff_list.append(name + ".R1")
        if (
            other._R2 is not None
            and self._R2 is not None
            and np.isnan(other._R2)
            and np.isnan(self._R2)
        ):
            pass
        elif other._R2 != self._R2:
            if is_add_value:
                val_str = " (self=" + str(self._R2) + ", other=" + str(other._R2) + ")"
                diff_list.append(name + ".R2" + val_str)
            else:
                diff_list.append(name + ".R2")
        if (
            other._R3 is not None
            and self._R3 is not None
            and np.isnan(other._R3)
            and np.isnan(self._R3)
        ):
            pass
        elif other._R3 != self._R3:
            if is_add_value:
                val_str = " (self=" + str(self._R3) + ", other=" + str(other._R3) + ")"
                diff_list.append(name + ".R3" + val_str)
            else:
                diff_list.append(name + ".R3")
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
        S += super(HoleMLSRPM, self).__sizeof__()
        S += getsizeof(self.H1)
        S += getsizeof(self.W0)
        S += getsizeof(self.W1)
        S += getsizeof(self.W2)
        S += getsizeof(self.R1)
        S += getsizeof(self.R2)
        S += getsizeof(self.R3)
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
        HoleMLSRPM_dict = super(HoleMLSRPM, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        HoleMLSRPM_dict["H1"] = self.H1
        HoleMLSRPM_dict["W0"] = self.W0
        HoleMLSRPM_dict["W1"] = self.W1
        HoleMLSRPM_dict["W2"] = self.W2
        HoleMLSRPM_dict["R1"] = self.R1
        HoleMLSRPM_dict["R2"] = self.R2
        HoleMLSRPM_dict["R3"] = self.R3
        if self.magnet_0 is None:
            HoleMLSRPM_dict["magnet_0"] = None
        else:
            HoleMLSRPM_dict["magnet_0"] = self.magnet_0.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs
            )
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        HoleMLSRPM_dict["__class__"] = "HoleMLSRPM"
        return HoleMLSRPM_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        H1_val = self.H1
        W0_val = self.W0
        W1_val = self.W1
        W2_val = self.W2
        R1_val = self.R1
        R2_val = self.R2
        R3_val = self.R3
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
            H1=H1_val,
            W0=W0_val,
            W1=W1_val,
            W2=W2_val,
            R1=R1_val,
            R2=R2_val,
            R3=R3_val,
            magnet_0=magnet_0_val,
            Zh=Zh_val,
            mat_void=mat_void_val,
            magnetization_dict_offset=magnetization_dict_offset_val,
            Alpha0=Alpha0_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.H1 = None
        self.W0 = None
        self.W1 = None
        self.W2 = None
        self.R1 = None
        self.R2 = None
        self.R3 = None
        if self.magnet_0 is not None:
            self.magnet_0._set_None()
        # Set to None the properties inherited from HoleMag
        super(HoleMLSRPM, self)._set_None()

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
        doc="""Magnet depth

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
        doc="""Magnet top width

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
        doc="""Magnet width angular 1 

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
        doc="""Small distance

        :Type: float
        :min: 0
        """,
    )

    def _get_R1(self):
        """getter of R1"""
        return self._R1

    def _set_R1(self, value):
        """setter of R1"""
        check_var("R1", value, "float", Vmin=0)
        self._R1 = value

    R1 = property(
        fget=_get_R1,
        fset=_set_R1,
        doc="""Rounding radius

        :Type: float
        :min: 0
        """,
    )

    def _get_R2(self):
        """getter of R2"""
        return self._R2

    def _set_R2(self, value):
        """setter of R2"""
        check_var("R2", value, "float")
        self._R2 = value

    R2 = property(
        fget=_get_R2,
        fset=_set_R2,
        doc="""Radius 2

        :Type: float
        """,
    )

    def _get_R3(self):
        """getter of R3"""
        return self._R3

    def _set_R3(self, value):
        """setter of R3"""
        check_var("R3", value, "float")
        self._R3 = value

    R3 = property(
        fget=_get_R3,
        fset=_set_R3,
        doc="""Radius 3

        :Type: float
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
        doc="""Magnet of the hole

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

    class SLSRPM_NoneError(SlotCheckError):
        """Raised when a propery of HoleM52 is None"""

        pass


MachineCheckError = HoleMLSRPM.MachineCheckError

LaminationCheckError = HoleMLSRPM.LaminationCheckError

SlotCheckError = HoleMLSRPM.SlotCheckError

SLSRPM_NoneError = HoleMLSRPM.SLSRPM_NoneError
