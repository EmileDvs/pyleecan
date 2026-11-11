# Experimental dataclass generated from Generator/ClassesRef/Machine/LamSlotMulti.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field
from typing import Any

import numpy as np
from matplotlib.patches import Patch

from ..Functions_new.init_fig import init_fig
from ..Functions_new.Plot.get_color_legend_from_surface import (
    get_color_legend_from_surface,
)
from ._error import LaminationCheckError
from .lamination import Lamination
from .slot import Slot


@dataclass(eq=False)
class LamSlotMulti(Lamination):
    """Lamination with list of Slot

    Attributes
    ----------
    slot_list : [Slot] or None
        List of lamination Slot
        Default: []
    alpha : ndarray or None
        Angular position of the Slots
        Unit: [rad]; Default: None
    sym_dict_enforced : dict or None
        Dictionary to enforce the lamination symmetry
        Default: {}
    """

    slot_list: list[Slot] | None = field(default_factory=list)
    """List of lamination Slot"""
    alpha: np.ndarray | None = None
    """Angular position of the Slots"""
    sym_dict_enforced: dict[str, Any] | None = field(default_factory=dict)
    """Dictionary to enforce the lamination symmetry"""

    # Inlined from Methods.Machine.LamSlotMulti.check
    def check(self):
        """Check that the Lamination object is correct

        Parameters
        ----------
        self : LamSlotMulti
            A LamSlotMulti object

        Returns
        -------
        None
        """

        super(type(self), self).check()

        # Check all the slots
        for slot in self.slot_list:
            slot.check()

        #
        if len(self.alpha.shape) > 1:
            raise self.LamSlotMultiAlphaError(
                "Alpha should have be a vector (1D array)"
            )
        if len(self.alpha) != len(self.slot_list):
            raise self.LamSlotMultiAlphaError(
                "Alpha should have the same length as slot_list"
            )
        if self.alpha[0] < 0:
            raise self.LamSlotMultiAlphaError(
                "Alpha should be an ordered array with values between 0 and 2*pi"
            )
        for ii in range(len(self.alpha) - 1):
            if self.alpha[ii] > self.alpha[ii + 1]:
                raise self.LamSlotMultiAlphaError(
                    "Alpha should be an ordered array with values between 0 and 2*pi"
                )
        if self.alpha[-1] > 2 * np.pi:
            raise self.LamSlotMultiAlphaError(
                "Alpha should be an ordered array with values between 0 and 2*pi"
            )

    # Inlined from Methods.Machine.LamSlotMulti.comp_height_yoke
    def comp_height_yoke(self):
        """Compute the yoke height

        Parameters
        ----------
        self : LamSlotMulti
            A LamSlotMulti object

        Returns
        -------
        Hy: float
            yoke height [m]

        """
        H = 0
        for slot in self.slot_list:
            H = max(H, slot.comp_height())
        return self.Rext - self.Rint - H

    # Inlined from Methods.Machine.LamSlotMulti.comp_periodicity_spatial
    def comp_periodicity_spatial(self):
        """Compute the periodicity factor of the lamination

        Parameters
        ----------
        self : LamSlotMulti
            A LamSlotMulti object

        Returns
        -------
        per_a : int
            Number of spatial periodicities of the lamination
        is_antiper_a : bool
            True if an spatial anti-periodicity is possible after the periodicities
        """

        if self.sym_dict_enforced is not None:
            self.get_logger().debug("Enforcing symmetry for LamSlotMulti")
            return (
                self.sym_dict_enforced["per_a"],
                self.sym_dict_enforced["is_antiper_a"],
            )
        else:
            # Zs = self.get_Zs()
            is_aper = False
            # TODO compute it
            self.get_logger().debug("Symmetry not available yet for LamSlotMulti")
            return 1, is_aper

    # Inlined from Methods.Machine.LamSlotMulti.comp_surfaces
    def comp_surfaces(self):
        """Compute the Lamination surfaces (Lamination, Ventilation, Slot).

        Parameters
        ----------
        self : LamSlotMulti
            A LamSlotMulti object

        Returns
        -------
        S_dict: dict
            Lamination surface dictionary (Slam, Svent, Sslot) [m**2]

        """

        S_dict = Lamination.comp_surfaces(self)
        Sslot = 0
        for slot in self.slot_list:
            Sslot += slot.comp_surface()

        S_dict["Sslot"] = Sslot
        S_dict["Slam"] -= Sslot
        return S_dict

    # Inlined from Methods.Machine.LamSlotMulti.get_pole_pair_number
    def get_pole_pair_number(self):
        """Return the number of pair of pole of the Lamination

        Parameters
        ----------
        self : LamSlotMulti
            A LamSlotMulti object

        Returns
        -------
        p: int
            Number of pair of pole

        """

        return self.get_Zs() // 2

    # Inlined from Methods.Machine.LamSlotMulti.get_slot_desc_list
    def get_slot_desc_list(self, sym=1, is_bore=True):
        """Returns an ordered description of the slot

        Parameters
        ----------
        self : LamSlotMulti
            A LamSlotMulti object
        sym: int
            Number of symmetry
        is_bore : bool
            True generate desc of bore, else yoke

        Returns
        -------
        slot_desc : list
            trigo ordered list of dictionary with key:
                "begin_angle" : float [rad]
                "end_angle" : float [rad]
                "obj" : Slot / None for Radius
                "lines : lines corresponding to the radius part
                "label" : Radius/Notch/Slot
        """

        slot_list = []
        for ii in range(len(self.slot_list) // sym):
            if self.slot_list[ii].is_bore == is_bore:
                slot = self.slot_list[ii]
                op = slot.comp_angle_opening()
                lines = slot.build_geometry()
                # Apply rotation
                for line in lines:
                    line.rotate(self.alpha[ii])
                bore_dict = {}
                bore_dict["begin_angle"] = self.alpha[ii] - op / 2
                bore_dict["end_angle"] = self.alpha[ii] + op / 2
                bore_dict["obj"] = slot
                bore_dict["lines"] = lines
                bore_dict["label"] = "Slot"
                slot_list.append(bore_dict)

        return slot_list

    # Inlined from Methods.Machine.LamSlotMulti.get_Zs
    def get_Zs(self):
        """Return the number of Slot of the Lamination

        Parameters
        ----------
        self : LamSlotMulti
            a LamSlotMulti object

        Returns
        -------
        Zs : float
            Number of Slot

        """

        return len(self.slot_list)

    # Inlined from Methods.Machine.LamSlotMulti.has_slot
    def has_slot(self, is_bore=True):
        """Return if the lamination has slot on the requested radius
        (notches not taken into account, cf has_notch)

        Parameters
        ----------
        self : LamSlotMulti
            A LamSlotMulti object
        is_bore : bool
            True check if there are slots on the bore, else yoke

        Returns
        -------
        has_slot : bool
            True if the lamination has slot on the requested radius
        """

        if self.slot_list is None or len(self.slot_list) == 0:
            return False

        # notch_shape.is_bore = None => Default is True
        if is_bore:
            return any([slot.is_bore in [None, True] for slot in self.slot_list])
        else:
            return any([slot.is_bore == False for slot in self.slot_list])

    # Inlined from Methods.Machine.LamSlotMulti.plot
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
        is_display=True,
        is_show_fig=True,
        is_clean_plot=False,
        is_winding_connection=False,
    ):
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
        is_clean_plot : bool
            True to remove title, legend, axis (only machine on plot with white background)
        is_winding_connection : bool
            True to display winding connections (not used)

        Returns
        -------
        fig : Matplotlib.figure.Figure
            Figure containing the plot
        ax : Matplotlib.axes.Axes object
            Axis containing the plot
        """

        (fig, ax, patch_leg, label_leg) = init_fig(fig=fig, ax=ax, shape="rectangle")

        surf_list = self.build_geometry(sym=sym, alpha=alpha, delta=delta)
        patches = []
        for surf in surf_list:
            color, legend = get_color_legend_from_surface(surf, is_lam_only)

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

            # The Lamination is centered in the figure
            Lim = self.Rext * 1.5
            ax.set_xlim(-Lim, Lim)
            ax.set_ylim(-Lim, Lim)

            # Add the legend
            if not is_edge_only:
                if self.is_stator:
                    ax.set_title("Stator with empty slot")
                else:
                    ax.set_title("Rotor with empty slot")

                ax.legend(patch_leg, label_leg)
            # Clean figure
            if is_clean_plot:
                ax.set_axis_off()
                ax.axis("equal")
                if ax.get_legend() is not None:
                    ax.get_legend().remove()
                ax.set_title("")
            if is_show_fig:
                fig.show()
            return fig, ax
        else:
            return patches

    class LamSlotMultiAlphaError(LaminationCheckError):
        """ """
