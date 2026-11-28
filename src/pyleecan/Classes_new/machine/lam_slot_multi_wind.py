# Experimental dataclass generated from Generator/ClassesRef/Machine/LamSlotMultiWind.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, ClassVar

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch

from ...classes_common.parents import container_or_parent
from ...definitions import config_dict
from ...Functions_new.utils.init_fig import init_fig
from ...Functions_new.utils.labels import BAR_LAB, WIND_LAB, decode_label
from ...Functions_new.Winding.gen_phase_list import gen_name
from .conductor import Conductor
from .lam_slot import LamSlot
from .lam_slot_multi import LamSlotMulti
from .machine import Machine
from .winding import Winding
from .winding_sc import WindingSC

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure

    from ..scidatatool.data_nd import DataND
    from .machine import Machine


@dataclass(eq=False)
class LamSlotMultiWind(LamSlotMulti):
    """Lamination with list of Slot filled with winding

    Attributes
    ----------
    Ksfill : float or None
        Imposed Slot Fill factor (if None, will be computed according to the winding and the slot)
        Default: None; Minimum: 0; Maximum: 1
    winding : Winding or None
        Lamination's Winding
        Default: Winding()
    """

    PHASE_COLORS = config_dict["PLOT"]["COLOR_DICT"]["PHASE_COLORS"]

    Ksfill: float | None = field(default=None, metadata={"min": 0, "max": 1})
    """Imposed Slot Fill factor (if None, will be computed according to the winding and the slot)"""
    winding: Winding = field(
        default_factory=lambda: Winding(), metadata={"default_class": "Winding"}
    )
    """Lamination's Winding"""

    _package: ClassVar[str] = "Machine"
    """Name of the package of the legacy class module"""

    # Inlined from Methods.Machine.LamSlotMultiWind.build_geometry
    def build_geometry(
        self,
        sym=1,
        alpha: float = 0,
        delta: complex = 0,
        is_circular_radius: bool = False,
        machine: Machine | None = None,
    ) -> list:
        """Build the geometry of the LamSlotMulti with winding in slots

        Parameters
        ----------
        self : LamSlotMultiWind
            A LamSlotMultiWind object
        alpha : float
            Angle for rotation [rad]
        delta : complex
            Complex value for translation
        is_circular_radius : bool
            True to add surfaces to "close" the Lamination radii
        machine : Machine, optional
            Machine holding the lamination (default: the parent)

        Returns
        -------
        surf_list : list
            list of surfaces needed to draw the lamination

        """

        # getting the Lamination surface
        surf_lam = LamSlot.build_geometry(
            self,
            sym=sym,
            alpha=alpha,
            delta=delta,
            is_circular_radius=is_circular_radius,
            machine=machine,
        )

        # getting the winding surface
        surf_list = []
        if self.slot_list is not None and self.slot_list[0].Zs != 0:
            if self.is_stator:
                st = "Stator"
            else:
                st = "Rotor"
            # getting angle between Slot
            angle = self.alpha
            # getting Nrad and Ntan
            if self.winding is None or self.winding.conductor is None:
                Nrad, Ntan = 1, 1
                surf_Wind = []
            else:
                try:
                    Nrad, Ntan = self.winding.get_dim_wind(lam=self)
                except Exception:
                    Nrad, Ntan = 1, 1

                for ii in range(int(len(angle) / sym)):  # for each slot
                    # get the winding surface
                    surf_Wind = self.slot_list[ii].build_geometry_active(
                        Nrad=Nrad,
                        Ntan=Ntan,
                        alpha=alpha,
                        delta=delta,
                        lam=self,
                        lam_label=self.get_label(machine=machine),
                    )

                    # for each part of the winding surface in the slot
                    for surf in surf_Wind:
                        new_surf = type(surf)(init_dict=surf.as_dict())
                        # changing the slot reference number
                        new_surf.label = surf.label[:-1] + str(ii)
                        new_surf.rotate(angle[ii])
                        surf_list.append(new_surf)

        surf_list = surf_lam + surf_list

        return surf_list

    # Inlined from Methods.Machine.LamSlotMultiWind.comp_angle_d_axis
    def comp_angle_d_axis(
        self, is_plot: bool = False, machine: Machine | None = None
    ) -> float:
        """Compute the angle between the X axis and the first d+ axis
        By convention a "Tooth" is centered on the X axis

        Parameters
        ----------
        self : LamSlotWind
            A LamSlotWind object
        is_plot : bool
            True to plot d axis position regarding unit mmf
        machine : Machine, optional
            Machine holding the lamination (default: the parent)

        Returns
        -------
        d_angle : float
            angle between the X axis and the first d+ axis
        """

        # Local import: avoids circular imports
        from .lam_slot_wind import LamSlotWind

        d_angle = LamSlotWind.comp_angle_d_axis(self, is_plot=is_plot)

        return d_angle

    # Inlined from Methods.Machine.LamSlotMultiWind.comp_mmf_dir
    def comp_mmf_dir(
        self,
        current_dir: int | None = None,
        phase_dir: int | None = None,
        is_plot: bool = False,
        machine: Machine | None = None,
    ) -> int:
        """Compute the rotation direction of the fundamental magnetomotive force induced by the winding

        Parameters
        ----------
        self : LamSlotMultiWind
            A LamSlotMultiWind object
        felec : float
            Stator current frequency to consider
        current_dir: int
            Stator current rotation direction +/-1
        phase_dir: int
            Stator winding phasor rotation direction +/-1
        is_plot: bool
            True to plot fft2 of stator MMF
        machine : Machine, optional
            Machine holding the lamination (default: the parent)

        Returns
        -------
        mmf_dir : int
            -1 or +1
        """

        # Local import: avoids circular imports
        from .lam_slot_wind import LamSlotWind

        rot_dir = LamSlotWind.comp_mmf_dir(self, current_dir, phase_dir, is_plot)

        return rot_dir

    # Inlined from Methods.Machine.LamSlotMultiWind.comp_mmf_unit
    def comp_mmf_unit(
        self,
        Na: int,
        Nt: int,
        felec: float = 1,
        current_dir: int | None = None,
        phase_dir: int | None = None,
        machine: Machine | None = None,
    ) -> tuple[DataND, DataND]:
        """Compute the winding Unit magnetomotive force

        Parameters
        ----------
        self : LamSlotMultiWind
            an LamSlotMultiWind object
        Na : int
            Space discretization for offline computation (otherwise use out.elec.angle)
        Nt : int
            Time discretization for offline computation (otherwise use out.elec.time)
        felec : float
            Stator current frequency to consider
        current_dir: int
            Stator current rotation direction +/-1
        phase_dir: int
            Stator winding phasor rotation direction +/-1
        machine : Machine, optional
            Machine holding the lamination (default: the parent)

        Returns
        -------
        MMF_U : DataND
            Unit magnetomotive force (Na,Nt)
        WF : DataND
            Winding functions (qs,Na)

        """

        # Local import: avoids circular imports
        from .lam_slot_wind import LamSlotWind

        MMF_U, WF = LamSlotWind.comp_mmf_unit(
            self,
            Na=Na,
            Nt=Nt,
            felec=felec,
            current_dir=current_dir,
            phase_dir=phase_dir,
        )

        return MMF_U, WF

    # Inlined from Methods.Machine.LamSlotMultiWind.comp_wind_function
    def comp_wind_function(
        self,
        angle: np.ndarray | None = None,
        Na: int = 2048,
        alpha_mmf0: float = 0,
        per_a: int = 1,
    ) -> np.ndarray:
        """Computation of the winding function for the lamination.
        By convention a tooth is centered on the X axis

        Parameters
        ----------
        self : LamSlotMultiWind
            A LamSlotMultiWind object
        angle : ndarray
            Space discretization to compute the winding functions
        Na : int
            Number of angular points for the winding function (not used if angle is set)
        alpha_mmf0 : float
            Angle to shift the winding function (Default value = 0)
        per_a : int
            Spatial periodicity factor

        Returns
        -------
        wf: ndarray
            Winding function Matrix (qs,Na)
        """

        # Space discretization

        if angle is None:
            angle = np.linspace(0, np.pi * 2 / per_a, Na, endpoint=False)
        else:
            Na = angle.size

        qs = self.winding.qs  # number of phases
        # Number of point on rad and tan direction
        Nrad, Ntan = self.winding.get_dim_wind(lam=self)
        Zs = self.get_Zs()  # Number of slot
        Zs0 = int(Zs / per_a)

        if self.sym_dict_enforced is not None:
            slot_list = self.slot_list[0:Zs0]
        else:
            slot_list = self.slot_list

        wind_mat = self.winding.get_connection_mat(Zs, lam=self)
        # sum wind_mat along Nlay_rad axis
        wind_mat = np.sum(wind_mat, axis=0)

        # angle of the center of the slots
        # By convention a tooth is centered on the X axis
        alpha_slot = self.alpha[:Zs0]

        if alpha_mmf0 != 0:
            angle = (angle - alpha_mmf0) % (2 * np.pi)

        wf = np.zeros((qs, Na))
        for ii, slot in enumerate(slot_list):
            slot_angle = slot.comp_angle_active_eq()
            slot_opening = slot.comp_angle_opening()
            for n in range(Ntan):
                # [Na, Zs]
                alpha_lay = np.linspace(
                    -slot_angle / 2, slot_angle / 2, Ntan + 1, endpoint=False
                )[1:]
                Xalpha_slot, Xangle = np.meshgrid(alpha_slot[ii] + alpha_lay[n], angle)

                Xwind = np.zeros((1, Zs0, qs))
                Xwind[0, :, :] = wind_mat[n, 0:Zs0, :]
                # Extended winding matrix [Na, Zs, qs]
                Xwind = np.repeat(Xwind, Na, axis=0)
                # Single winding function in every slot and angle for nth layer [Na, Zs]
                Xwf = -0.5 * Conductor.comp_cond_function(
                    Xalpha_slot, slot_opening, Xangle
                )

                for q in range(qs):
                    wf[q, :] += np.sum(Xwind[n, ii, q] * Xwf, axis=1)

        if per_a > 1:
            wf = wf - np.mean(wf, axis=1)[:, None]

        return wf

    # Inlined from Methods.Machine.LamSlotMultiWind.get_pole_pair_number
    def get_pole_pair_number(self) -> int | None:
        """Return the number of pair of pole of the Lamination

        Parameters
        ----------
        self : LamSlotMultiWind
            A LamSlotMultiWind object

        Returns
        -------
        p: int
            Number of pair of pole

        """

        if self.winding is not None:
            return self.winding.p
        else:
            return None

    # Inlined from Methods.Machine.LamSlotMultiWind.plot
    def plot(
        self,
        fig: Figure | None = None,
        ax: Axes | None = None,
        is_lam_only: bool = False,
        sym: int = 1,
        alpha: float = 0,
        delta: complex = 0,
        is_edge_only: bool = False,
        edgecolor: str | None = None,
        is_add_arrow: bool = False,
        is_display: bool = True,
        is_add_sign: bool = False,
        is_show_fig: bool = True,
        save_path: str | None = None,
        win_title: str | None = None,
        is_winding_connection: bool = False,
        machine: Machine | None = None,
    ) -> list | tuple[Figure, Axes]:
        """Plot the Lamination with empty Slots in a matplotlib fig

        Parameters
        ----------
        self : LamSlotMulti
            A LamSlotMulti object
        fig : Matplotlib.figure.Figure
            existing figure to use if None create a new one
        ax : Matplotlib.axes.Axes object
            Axis on which to plot the data
        is_lam_only: bool
            True to plot only the lamination
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
        is_display : bool
            False to return the patches
        is_show_fig : bool
            To call show at the end of the method
        is_winding_connection : bool
            True to display winding connections (not used)
        machine : Machine, optional
            Machine holding the lamination (default: the parent)

        Returns
        -------
        patches : list
            List of Patches
        fig : Matplotlib.figure.Figure
            Figure containing the plot
        ax : Matplotlib.axes.Axes object
            Axis containing the plot
        """
        machine = container_or_parent(self, machine, "machine")

        (fig, ax, patch_leg, label_leg) = init_fig(fig=fig, ax=ax, shape="rectangle")

        # getting the number of phases and winding connection matrix
        if self.winding is not None:
            if isinstance(self.winding, WindingSC):  # plot only one phase for WindingSC
                wind_mat = None
                qs = 1
            else:
                try:
                    wind_mat = self.winding.get_connection_mat(self.get_Zs(), lam=self)
                    qs = self.winding.qs
                except:
                    wind_mat = None
                    qs = 1
        else:
            wind_mat = None
            qs = 1

        # Get the LamSlot surface(s)
        surf_list = self.build_geometry(
            sym=sym, alpha=alpha, delta=delta, machine=machine
        )
        patches = []
        for surf in surf_list:
            label_dict = decode_label(surf.label)
            if (
                WIND_LAB in label_dict["surf_type"]
                or BAR_LAB in label_dict["surf_type"]
            ):
                if not is_lam_only:
                    if wind_mat is None:  # No winding, WindingSC: first phase color
                        color, sign = Winding._find_wind_phase_color(surf.label, None)
                    else:
                        color, sign = self.winding.find_wind_phase_color(
                            label=surf.label, wind_mat=wind_mat, lam=self
                        )
                    if sign == "+" and is_add_sign:
                        hatch = self.PLUS_HATCH
                    elif sign == "-" and is_add_sign:
                        hatch = self.MINUS_HATCH
                    else:
                        hatch = None
                    patches.extend(
                        surf.get_patches(
                            color=color,
                            is_edge_only=is_edge_only,
                            hatch=hatch,
                            edgecolor=edgecolor,
                        )
                    )
            else:
                color, legend = Machine.get_color_legend_from_surface(surf, is_lam_only)

                if color is not None:
                    patches.extend(
                        surf.get_patches(
                            color=color,
                            is_edge_only=is_edge_only,
                            edgecolor=edgecolor,
                        )
                    )
                if not is_edge_only and legend is not None and legend not in label_leg:
                    label_leg.append(legend)
                    patch_leg.append(Patch(color=color))

        # Display the result
        if is_display:
            (fig, ax, patch_leg, label_leg) = init_fig(fig)
            ax.set_xlabel("(m)")
            ax.set_ylabel("(m)")
            for patch in patches:
                ax.add_patch(patch)

            # Axis Setup
            ax.axis("equal")

            # Window title
            if self.is_stator:
                prefix = "Stator "
            else:
                prefix = "Rotor "
            if (
                win_title is None
                and machine is not None
                and machine.name not in [None, ""]
            ):
                win_title = machine.name + " " + prefix[:-1]
            elif win_title is None:
                win_title = prefix[:-1]
            manager = plt.get_current_fig_manager()
            if manager is not None:
                manager.set_window_title(win_title)

            # The Lamination is centered in the figure
            Lim = self.Rext * 1.5
            ax.set_xlim(-Lim, Lim)
            ax.set_ylim(-Lim, Lim)

            # Add the legend
            if not is_edge_only:
                if self.is_stator and "Stator" not in label_leg:
                    ax.set_title("Stator with empty slot")
                elif not self.is_stator and "Rotor" not in label_leg:
                    ax.set_title("Rotor with Winding")
                # Add the winding legend only if needed
                if not is_lam_only:
                    if self.winding is not None:
                        phase_name = [
                            prefix + n for n in gen_name(qs, is_add_phase=True)
                        ]
                        for ii in range(qs):
                            if not phase_name[ii] in label_leg and not is_add_sign:
                                # Avoid adding twice the same label
                                index = ii % len(self.PHASE_COLORS)
                                patch_leg.append(Patch(color=self.PHASE_COLORS[index]))
                                label_leg.append(phase_name[ii])
                            if not "Phase +" in label_leg and is_add_sign:
                                # Avoid adding twice the same label
                                index = ii % len(self.PHASE_COLORS)
                                patch_leg.append(
                                    Patch(
                                        color=self.PHASE_COLORS[index],
                                        hatch=self.PLUS_HATCH,
                                    )
                                )
                                label_leg.append(phase_name[ii] + " +")
                            if not "Phase -" in label_leg and is_add_sign:
                                # Avoid adding twice the same label
                                index = ii % len(self.PHASE_COLORS)
                                patch_leg.append(
                                    Patch(
                                        color=self.PHASE_COLORS[index],
                                        hatch=self.MINUS_HATCH,
                                    )
                                )
                                label_leg.append(phase_name[ii] + " -")
                ax.legend(patch_leg, label_leg)

            if save_path is not None:
                fig.savefig(save_path)
                plt.close(fig=fig)
            if is_show_fig:
                fig.show()
            return fig, ax
        else:
            return patches

    # Inlined from Methods.Machine.LamSlotMultiWind.plot_mmf_unit
    def plot_mmf_unit(
        self,
        r_max=100,
        fig: Figure | None = None,
        save_path: str | None = None,
        is_show_fig: bool = True,
        machine: Machine | None = None,
    ) -> Figure:
        """Plot the winding unit mmf as a function of space
        Parameters
        ----------

        self : LamSlotMultiWind
            an LamSlotMultiWind object
        Na : int
            Space discretization
        fig : Matplotlib.figure.Figure
            existing figure to use if None create a new one
        is_show_fig : bool
            To call show at the end of the method
        machine : Machine, optional
            Machine holding the lamination (default: the parent)

        Returns
        -------
        fig : Matplotlib.figure.Figure
            Figure of the plot

        Notes
        -----
        r_max and fig are not used: LamSlotWind.plot_mmf_unit draws on its own
        figure (the legacy call passed them and raised a TypeError)
        """

        # Local import: avoids circular imports
        from .lam_slot_wind import LamSlotWind

        return LamSlotWind.plot_mmf_unit(
            self, save_path=save_path, is_show_fig=is_show_fig, machine=machine
        )
