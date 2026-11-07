# Experimental dataclass generated from Generator/ClassesRef/Machine/LamSquirrelCage.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch, Rectangle, Wedge

from ..definitions import config_dict
from ..Functions.init_fig import init_fig
from ..Functions.labels import BAR_LAB, WIND_LAB
from ..Functions.load import import_class
from ..Functions.Plot import (
    ARROW_COLOR,
    ARROW_WIDTH,
    MAIN_LINE_COLOR,
    MAIN_LINE_STYLE,
    MAIN_LINE_WIDTH,
    SC_FONT_SIZE,
    plot_quote,
)
from .cond_type_21 import CondType21
from .lam_slot import LamSlot
from .lam_slot_wind import LamSlotWind
from .material import Material
from .segment import Segment
from .slot_w_22 import SlotW22


@dataclass(eq=False)
class LamSquirrelCage(LamSlotWind):
    """squirrel cages lamination

    Attributes
    ----------
    Hscr : float
        short circuit ring section radial height [m]
        Unit: m; Default: 0.03; Minimum: 0
    Lscr : float
        short circuit ring section axial length
        Unit: m; Default: 0.015; Minimum: 0
    ring_mat : Material or None
        Material of the Rotor short circuit ring
        Default: None
    """

    SCR_COLOR = config_dict["PLOT"]["COLOR_DICT"]["SCR_COLOR"]
    MAGNET_COLOR = config_dict["PLOT"]["COLOR_DICT"]["MAGNET_COLOR"]
    ROTOR_COLOR = config_dict["PLOT"]["COLOR_DICT"]["ROTOR_COLOR"]
    STATOR_COLOR = config_dict["PLOT"]["COLOR_DICT"]["STATOR_COLOR"]
    BAR_COLOR = config_dict["PLOT"]["COLOR_DICT"]["BAR_COLOR"]
    Hscr: float = 0.03
    """short circuit ring section radial height [m]"""
    Lscr: float = 0.015
    """short circuit ring section axial length"""
    ring_mat: Material | None = None
    """Material of the Rotor short circuit ring"""

    # Inlined from Methods.Machine.LamSquirrelCage.build_geometry
    def build_geometry(self, sym=1, alpha=0, delta=0, is_circular_radius=False):
        """Build geometry of the LamSquirrelCage

        Parameters
        ----------
        self :
            LamSquirrelCage Object
        sym : int
            Symmetry factor (1= full machine, 2= half of the machine...)
        alpha : float
            Angle for rotation [rad]
        delta : complex
            Complex value for translation
        is_circular_radius : bool
            True to add surfaces to "close" the Lamination radii

        Returns
        -------
        surf_list: list
            list of surfaces

        """
        surf_list = LamSlotWind.build_geometry(
            self,
            sym=sym,
            is_circular_radius=is_circular_radius,
            alpha=alpha,
            delta=delta,
        )

        # Adapt the label
        for surf in surf_list:
            if WIND_LAB in surf.label:
                surf.label = surf.label.replace(WIND_LAB, BAR_LAB)

        return surf_list

    # Inlined from Methods.Machine.LamSquirrelCage.check
    def check(self):
        """Check that the Lamination object is correct

        Parameters
        ----------
        self : LamSquirrelCage
            A LamSquirrelCage object

        Returns
        -------
        None

        Raises
        _______
        SCC_NotARotor
            A LamSquirrelCage Lamination can't be a stator
        SCC_WrongCond
            A LamSquirrelCage's conductor must be a type 2_1
        """

        LamSlotWind.check(self)

        if self.is_stator:
            raise SCC_NotARotor("A LamSquirrelCage Lamination can't be a stator")

        if not isinstance(self.winding.conductor, CondType21):
            raise SCC_WrongCond("A LamSquirrelCage's conductor must be a type 2_1")

    # Inlined from Methods.Machine.LamSquirrelCage.comp_angle_d_axis
    def comp_angle_d_axis(self):
        """Compute the angle between the X axis and the first d+ axis
        By convention a "Tooth" is centered on the X axis

        Parameters
        ----------
        self : LamSquirrelCage
            A LamSquirrelCage object

        Returns
        -------
        d_angle : float
            angle between the X axis and the first d+ axis
        """

        return 0

    # Inlined from Methods.Machine.LamSquirrelCage.comp_length_ring
    def comp_length_ring(self):
        """Computation of the squirrel cage end-ring average perimeter (circumferential length)

        Parameters
        ----------
        self : LamSquirrelCage
            A LamSquirrelCage object

        Returns
        -------
        Lring: float
            Length of the ring [m]

        """

        # calculation of the average radius of the center of the end-ring (distance to z-axis of the electrical machine)
        Rmw = self.slot.comp_radius_mid_active()

        return 2 * np.pi * Rmw

    # Inlined from Methods.Machine.LamSquirrelCage.comp_masses
    def comp_masses(self):
        """Compute the Lamination masses

        Parameters
        ----------
        self : LamSquirrelCage
            A LamSquirrelCage object

        Returns
        -------
        M_dict: dict
            Lamination mass dictionary (Mtot, Mlam, Mwind, Mring) [kg]
        """

        if self.is_stator:
            lam_name = "Stator"
        else:
            lam_name = "Rotor"
        M_dict = LamSlot.comp_masses(self)

        if self.winding is not None:
            # Check
            if self.winding.conductor.cond_mat.struct.rho is None:
                mat_name = str(self.winding.conductor.cond_mat.name)
                raise Exception(
                    "Error: The "
                    + lam_name
                    + " winding conductor material ("
                    + mat_name
                    + ") is not fully defined. Please set struct.rho"
                )
            # Compute
            L_dict = self.comp_lengths_winding()
            Mwind = (
                self.winding.conductor.comp_surface_active()
                * self.get_Zs()
                * self.winding.conductor.cond_mat.struct.rho
                * L_dict["Lwht"]
            )
        else:
            Mwind = 0

        # Adding Short circuit ring
        # Check
        if self.ring_mat.struct.rho is None:
            mat_name = str(self.ring_mat.name)
            raise Exception(
                "Error: The "
                + lam_name
                + " Short circuit ring material ("
                + mat_name
                + ") is not fully defined. Please set struct.rho"
            )
        Sring = self.comp_surface_ring()
        Lring = self.comp_length_ring()
        Mring = Sring * Lring * self.ring_mat.struct.rho

        M_dict["Mtot"] += Mwind + Mring
        M_dict["Mwind"] = Mwind + Mring
        M_dict["Mring"] = Mring

        return M_dict

    # Inlined from Methods.Machine.LamSquirrelCage.comp_number_phase_eq
    def comp_number_phase_eq(self):
        """Compute the equivalent number of phase

        Parameters
        ----------
        self : LamSquirrelCage
            A LamSquirrelCage object

        Returns
        -------
        qb: float
            Zs/p
        """

        return self.slot.Zs / float(self.winding.p)

    # Inlined from Methods.Machine.LamSquirrelCage.comp_periodicity_spatial
    def comp_periodicity_spatial(self):
        """Compute the periodicity factor of the lamination

        Parameters
        ----------
        self : LamSquirrelCage
            A LamSquirrelCage object

        Returns
        -------
        per_a : int
            Number of spatial periodicities of the lamination
        is_antiper_a : bool
            True if an spatial anti-periodicity is possible after the periodicities
        """

        # Reuse method from Lamination instead of LamSlotWind since winding periodicity is given by lamination periodicity
        Lamination = import_class("pyleecan.Classes", "Lamination")

        per_a, is_antiper_a = Lamination.comp_periodicity_spatial(self)

        return per_a, is_antiper_a

    # Inlined from Methods.Machine.LamSquirrelCage.comp_resistance_wind
    def comp_resistance_wind(self, T=20):
        """Computation of the equivalent rotor resistance per phase of a cage winding with 'qs' number of phases

        Parameters
        ----------
        self : LamSquirrelCage
            A LamSquirrelCage object
        T : float
            mean winding temperature [°C], default value is 20°C

        Returns
        -------
        Rrot: float
            resistance of the rotor [Ohm]
        """
        # calculate resistance ring at T degC
        rho = self.ring_mat.elec.get_resistivity(T_op=T, T_ref=20)

        Sring = self.comp_surface_ring()
        lring = self.comp_length_ring()
        Zr = self.get_Zs()
        P = self.get_pole_pair_number()
        # total ring resistance (not yet divided by Zr to take average resistance seen by one bar)
        Rring = rho * lring / Sring

        # calculate resistance rod at T degC
        rho = self.winding.conductor.cond_mat.elec.get_resistivity(T_op=T, T_ref=20)

        # active surface inside slot
        Srod = self.winding.conductor.comp_surface_active()
        # total bar length inside lamination + outside lamination before end ring (#TODO Lewout should be 0 for molded cage, #TODO comp_length() should account for skew shape)
        lrod = self.comp_length() + 2 * self.winding.Lewout
        # bar resistance
        Rrod = rho * lrod / Srod

        # average physical resistance per rotor bar (not yet transfered on stator side, per stator phase)
        Rtot = Rrod + Rring / Zr / (2 * np.sin(np.pi * P / Zr) ** 2)

        return Rtot

    # Inlined from Methods.Machine.LamSquirrelCage.comp_surface_ring
    def comp_surface_ring(self):
        """Computation of the ring cross-section surface area

        Parameters
        ----------
        self : LamSquirrelCage
            A LamSquirrelCage object

        Returns
        -------
        Lring: float
            Surface area of the cross-section of the ring [m^2]

        """
        Hscr = self.Hscr
        Lscr = self.Lscr

        return Lscr * Hscr

    # Inlined from Methods.Machine.LamSquirrelCage.get_name_phase
    def get_name_phase(self):
        """Return the name of the winding phases

        Parameters
        ----------
        self : LamSquirrelCage
            A LamSquirrelCage object

        Returns
        -------
        name_phase: list
            Empty list

        """
        if (
            not hasattr(self, "winding") or self.winding is None
            # or self.winding.conductor is None
        ):
            return []
        qs = 3 if self.winding.qs is None else self.winding.qs

        return ["Bar " + str(ii + 1) for ii in range(qs)]

    # Inlined from Methods.Machine.LamSquirrelCage.plot
    def plot(
        self,
        fig=None,
        ax=None,
        is_lam_only=False,
        sym=1,
        alpha=0,
        delta=0,
        is_edge_only=False,
        edgecolor=None,
        is_add_arrow=False,
        is_show_fig=True,
        is_winding_connection=False,
    ):
        """Plot the Lamination in a matplotlib fig

        Parameters
        ----------
        self : LamSquirrelCage
            A LamSquirrelCage object
        fig : Matplotlib.figure.Figure
            existing figure to use if None create a new one
        ax : Matplotlib.axes.Axes object
            Axis on which to plot the data
        is_lam_only : bool
            True to plot only the lamination (remove the bare)
        sym : int
            Symmetry factor (1= full machine, 2= half of the machine...)
        alpha : float
            Angle for rotation [rad]
        delta : complex
            Complex value for translation
        is_edge_only: bool
            To plot transparent Patches
        edgecolor:
            Color of the edges if is_edge_only=True
        is_show_fig : bool
            To call show at the end of the method
        is_winding_connection : bool
            True to display winding connections (not used)

        Returns
        -------
        fig : Matplotlib.figure.Figure
            Figure containing the plot
        ax : Matplotlib.axes.Axes object
            Axis containing the plot
        """

        # Lamination and ventilation ducts patches
        (fig, ax, patch_leg, label_leg) = init_fig(fig=fig, ax=ax, shape="rectangle")

        # Plot the lamination
        LamSlotWind.plot(
            self,
            fig=fig,
            ax=ax,
            is_lam_only=is_lam_only,
            sym=sym,
            alpha=alpha,
            delta=delta,
            is_edge_only=is_edge_only,
            is_show_fig=is_show_fig,
        )

        # init figure again to get updated label_leg and patch_leg
        (fig, ax, patch_leg, label_leg) = init_fig(fig, ax=ax)

        # setup the patch of the short circuit ring if needed
        patches = []
        if not is_lam_only:
            try:
                Rmw = self.slot.comp_radius_mid_active()
                patches.append(
                    Wedge(
                        (0, 0),
                        Rmw + self.Hscr / 2.0,
                        0,
                        360 / sym,
                        width=self.Hscr,
                        color=self.SCR_COLOR,
                    )
                )  # Full ring
            except:
                pass

        # Display the result
        ax.set_xlabel("(m)")
        ax.set_ylabel("(m)")
        ax.set_title("Squirrel Cage Rotor")

        # Axis Setup
        ax.axis("equal")
        Lim = self.Rext * 1.5
        ax.set_xlim(-Lim, Lim)
        if sym == 1:
            ax.set_ylim(-Lim, Lim)
        else:
            ax.set_ylim(-Lim * 0.3, Lim)

        if not is_lam_only:
            # Add the short ciruit ring to the fig
            for patch in patches:
                ax.add_patch(patch)
            if "Short Circuit Ring" not in label_leg:
                patch_leg.append(Patch(color=self.SCR_COLOR))
                label_leg.append("Short Circuit Ring")

            ax.legend(patch_leg, label_leg)
        if is_show_fig:
            fig.show()
        return fig, ax

    # Inlined from Methods.Machine.LamSquirrelCage.plot_schematics_scr
    def plot_schematics_scr(
        self,
        is_default=False,
        is_add_schematics=True,
        is_add_main_line=True,
        save_path=None,
        is_show_fig=True,
        fig=None,
        ax=None,
    ):
        """Plot the schematics of the short circuit ring

        Parameters
        ----------
        self : LamSquirrelCage
            A LamSquirrelCage object
        is_default : bool
            True: plot default schematics, else use current lamination values
        is_add_schematics : bool
            True to display the schematics information (Hscr, Lscr...)
        is_add_main_line : bool
            True to display "main lines" (dotted lines and Z axis)
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
        """

        # Use some default parameter
        if is_default:
            lam = type(self)(
                is_stator=False,
                is_internal=True,
                Rint=0,
                Rext=0.25,
                L1=1,
                Hscr=0.15,
                Lscr=0.1,
            )
            lam.slot = SlotW22(Zs=12, H0=0.02, H2=0.05)
            lam.winding.Lewout = 0.1
            lam.plot_schematics_scr(
                is_default=False,
                is_add_schematics=is_add_schematics,
                is_add_main_line=is_add_main_line,
                save_path=save_path,
                is_show_fig=is_show_fig,
                fig=fig,
                ax=ax,
            )
        else:
            # Getting the main plot
            fig, ax = self.plot_side(is_show_fig=False, fig=fig, ax=ax)
            Lt = self.comp_length()
            Hs = self.slot.comp_height()
            Ha = self.slot.comp_height_active()
            Ho = Hs - Ha
            Le = self.winding.Lewout
            Lscr = self.Lscr
            Hscr = self.Hscr

            # Adding schematics
            if is_add_schematics:
                # Rext
                line = Segment(Lt / 2 - Lt / 5, Lt / 2 - Lt / 5 + 1j * self.Rext)
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="Rext",
                    offset_label=-Le * 1.05,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # Lewout
                Zbar1 = Lt / 2 + 1j * (self.Rext - Hs + Ha)
                Zbar2 = Lt / 2 + Le + 1j * (self.Rext - Hs + Ha)
                Zlim1 = Zbar1 + 1j * Hs
                Zlim2 = Zbar2 + 1j * Hs
                plot_quote(
                    Zbar1,
                    Zlim1,
                    Zlim2,
                    Zbar2,
                    offset_label=1j * Le * 0.4 - Le * 0.7,
                    fig=fig,
                    ax=ax,
                    label="Lewout",
                )
                # Lscr
                ZL1 = Lt / 2 + Le + 1j * (self.Rext - Hs + Ha / 2 + Hscr / 2)
                ZL2 = Lt / 2 + Le + Lscr + 1j * (self.Rext - Hs + Ha / 2 + Hscr / 2)
                Zlim1 = ZL1 + 1j * Hs
                Zlim2 = ZL2 + 1j * Hs
                plot_quote(
                    ZL1,
                    Zlim1,
                    Zlim2,
                    ZL2,
                    offset_label=1j * Le * 0.4 - Le * 0.3,
                    fig=fig,
                    ax=ax,
                    label="Lscr",
                )
                # Hscr
                line = Segment(ZL2, ZL2 - 1j * Hscr)
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="Hscr",
                    offset_label=Le * 0.3,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )

            if is_add_main_line:
                # Ox axis
                line = Segment(0, Lt + Le + Lscr)
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # Hscr lines
                line = Segment(ZL1 - 1j * Hscr, ZL2 - 1j * Hscr)
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                line = Segment(ZL1.conjugate() + 1j * Hscr, ZL2.conjugate() + 1j * Hscr)
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )

            ax.axis("equal")
            ax.set_xlim(Lt / 4, (Lt / 2 + Le + Lscr) * 1.1)
            # ax.set_ylim(-self.Rext, self.Rext)
            manager = plt.get_current_fig_manager()
            if manager is not None:
                manager.set_window_title(type(self).__name__ + " Schematics")
            ax.set_title("")
            ax.get_legend().remove()
            ax.set_axis_off()

            # Save / Show
            if save_path is not None:
                fig.savefig(save_path)
                plt.close(fig=fig)

            if is_show_fig:
                fig.show()
            return fig, ax

    # Inlined from Methods.Machine.LamSquirrelCage.plot_side
    def plot_side(self, fig=None, ax=None, is_show_fig=True, save_path=None):
        """Plot the side view of the Lamination in a matplotlib fig
        (Z axis left to right)

        Parameters
        ----------
        self : LamSquirrelCage
            A LamSquirrelCage object
        fig : Matplotlib.figure.Figure
            existing figure to use if None create a new one
        ax : Matplotlib.axes.Axes object
            Axis on which to plot the data
        is_show_fig : bool
            To call show at the end of the method
        save_path : str
            full path including folder, name and extension of the file to save if save_path is not None

        Returns
        -------
        fig : Matplotlib.figure.Figure
            Figure containing the plot
        ax : Matplotlib.axes.Axes object
            Axis containing the plot
        """

        # Lamination and ventilation ducts patches
        (fig, ax, patch_leg, label_leg) = init_fig(fig=fig, ax=ax)

        patches = []  # List of patches to draw the lamination
        if self.is_stator:
            lam_color = self.STATOR_COLOR
        else:
            lam_color = self.ROTOR_COLOR

        # Comp all dimensions
        Lt = self.comp_length()
        Hs = self.slot.comp_height()
        Ha = self.slot.comp_height_active()
        Ho = Hs - Ha
        Le = self.winding.Lewout
        Lscr = self.Lscr
        Hscr = self.Hscr

        # Comp point coordinates
        ZLamExt = -Lt / 2 - 1j * self.Rext  # Bottom Lamination Ext
        ZLamInt = -Lt / 2 + 1j * self.Rint  # Bottom Lamination Int
        ZBarTopR = Lt / 2 + 1j * (self.Rext - Hs)  # Top bar right
        ZBarBotR = Lt / 2 + 1j * (-self.Rext + Ho)  # Bottom bar right
        ZBarTopL = -Lt / 2 - Le + 1j * (self.Rext - Hs)  # Top bar left
        ZBarBotL = -Lt / 2 - Le + 1j * (-self.Rext + Ho)  # Bottom bar left
        ZscrRight = (
            Lt / 2 + Le + 1j * (-self.Rext + Ho + Ha / 2 - Hscr / 2)
        )  # Short Circuit Ring Right
        ZscrLeft = (
            -Lt / 2 - Le - Lscr + 1j * (-self.Rext + Ho + Ha / 2 - Hscr / 2)
        )  # Short Circuit Ring Right

        # Draw Lamination rectangle(s)
        if self.Rint == 0:
            patches.append(
                Rectangle(
                    xy=(ZLamExt.real, ZLamExt.imag),
                    width=Lt,
                    height=2 * self.Rext,
                    color=lam_color,
                )
            )
        else:
            patches.append(  # Left
                Rectangle(
                    xy=(ZLamExt.real, ZLamExt.imag),
                    width=Lt,
                    height=self.Rext - self.Rint,
                    color=lam_color,
                )
            )
            patches.append(  # Right
                Rectangle(
                    xy=(ZLamInt.real, ZLamInt.imag),
                    width=Lt,
                    height=self.Rext - self.Rint,
                    color=lam_color,
                )
            )

        # Add Lewout rectangles
        patches.append(  # Top Right
            Rectangle(
                xy=(ZBarTopR.real, ZBarTopR.imag),
                width=Le,
                height=Ha,
                color=self.BAR_COLOR,
            )
        )
        patches.append(  # Bot Right
            Rectangle(
                xy=(ZBarBotR.real, ZBarBotR.imag),
                width=Le,
                height=Ha,
                color=self.BAR_COLOR,
            )
        )
        patches.append(  # Top Left
            Rectangle(
                xy=(ZBarTopL.real, ZBarTopL.imag),
                width=Le,
                height=Ha,
                color=self.BAR_COLOR,
            )
        )
        patches.append(  # Bot Left
            Rectangle(
                xy=(ZBarBotL.real, ZBarBotL.imag),
                width=Le,
                height=Ha,
                color=self.BAR_COLOR,
            )
        )
        # Add short circuit ring rectangles
        patches.append(
            Rectangle(
                xy=(ZscrRight.real, ZscrRight.imag),
                width=Lscr,
                height=abs(2 * ZscrRight.imag),
                color=self.SCR_COLOR,
            )
        )
        patches.append(
            Rectangle(
                xy=(ZscrLeft.real, ZscrLeft.imag),
                width=Lscr,
                height=abs(2 * ZscrLeft.imag),
                color=self.SCR_COLOR,
            )
        )

        # Display the result
        ax.set_xlabel("[m]")
        ax.set_ylabel("[m]")
        for patch in patches:
            ax.add_patch(patch)

        # Axis Setup
        ax.axis("equal")
        ax.set_title("Squirrel Cage Rotor side view")
        # Set legend
        if self.is_stator:
            patch_leg.append(Patch(color=self.STATOR_COLOR))
            label_leg.append("Stator")
        elif not self.is_stator and "Rotor" not in label_leg:
            patch_leg.append(Patch(color=self.ROTOR_COLOR))
            label_leg.append("Rotor")
        patch_leg.append(Patch(color=self.BAR_COLOR))
        label_leg.append("Bar")
        patch_leg.append(Patch(color=self.SCR_COLOR))
        label_leg.append("Short Circuit Ring")
        ax.legend(patch_leg, label_leg)
        if is_show_fig:
            fig.show()
        if save_path is not None:
            fig.savefig(save_path)
            plt.close(fig=fig)
        return fig, ax

    class MachineCheckError(Exception):
        """ """

    class LaminationCheckError(MachineCheckError):
        """ """

    class Lam_WindCheckError(LaminationCheckError):
        """ """

    class SquirrelCageCheckError(Lam_WindCheckError):
        """ """

    class SCC_WrongCond(SquirrelCageCheckError):
        """ """

    class SCC_NotARotor(SquirrelCageCheckError):
        """ """


MachineCheckError = LamSquirrelCage.MachineCheckError
LaminationCheckError = LamSquirrelCage.LaminationCheckError
Lam_WindCheckError = LamSquirrelCage.Lam_WindCheckError
SquirrelCageCheckError = LamSquirrelCage.SquirrelCageCheckError
SCC_WrongCond = LamSquirrelCage.SCC_WrongCond
SCC_NotARotor = LamSquirrelCage.SCC_NotARotor
