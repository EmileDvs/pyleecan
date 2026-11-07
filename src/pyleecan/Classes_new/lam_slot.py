# Experimental dataclass generated from Generator/ClassesRef/Machine/LamSlot.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

import numpy as np
from matplotlib.patches import Patch

from ..Functions.init_fig import init_fig
from ..Functions.labels import update_RTS_index
from ..Functions.Plot.get_color_legend_from_surface import get_color_legend_from_surface
from .lamination import Lamination
from .slot import Slot


@dataclass(eq=False)
class LamSlot(Lamination):
    """Lamination with empty Slot

    Attributes
    ----------
    slot : Slot or None
        lamination Slot
        Default: None
    """

    slot: Slot | None = None
    """lamination Slot"""

    # Inlined from Methods.Machine.LamSlot.check
    def check(self):
        """Check that the Lamination object is correct

        Parameters
        ----------
        self : LamSlot
            A LamSlot object

        Returns
        -------
        None

        Raises
        _______
        LSC_SlotTooLong
            The Slot is too long for the lamination (HYoke <0)

        LSC_OverlappingSlot
            The Lamination has overlapping slot

        """

        super(type(self), self).check()

        self.slot.check()

        if self.comp_height_yoke() < 0:
            raise LSC_SlotTooLong("The Slot is too long for the lamination (HYoke <0)")

        """
        Wt = self.slot.comp_tooth_widths()["WTooth_min"]

        if Wt < 0:
            raise LSC_OverlappingSlot("The Lamination has overlapping slot")
        """

    # Inlined from Methods.Machine.LamSlot.comp_angle_d_axis
    def comp_angle_d_axis(self):
        """Compute the angle between the X axis and the first d+ axis
        By convention a "Tooth" is centered on the X axis
        By convention the first magnet is +

        Parameters
        ----------
        self : LamSlot
            A LamSlot object

        Returns
        -------
        d_angle : float
            angle between the X axis and the first d+ axis
        """

        return 0

    # Inlined from Methods.Machine.LamSlot.comp_height_yoke
    def comp_height_yoke(self):
        """Compute the yoke height

        Parameters
        ----------
        self : LamSlot
            A LamSlot object

        Returns
        -------
        Hy: float
            yoke height [m]

        """
        if self.slot is not None and self.slot.Zs > 0:
            return self.Rext - self.Rint - self.slot.comp_height()
        else:
            return self.Rext - self.Rint

    # Inlined from Methods.Machine.LamSlot.comp_radius_mec
    def comp_radius_mec(self):
        """Compute the mechanical radius of the Lamination [m]

        Parameters
        ----------
        self : LamSlot
            A LamSlot object

        Returns
        -------
        Rmec: float
            Mechanical radius [m]
        """

        Rmec = self.get_Rbo()
        if self.slot.is_airgap_active():
            # Part of the active surface is in the airgap
            # => Reduce mechanical airgap
            (Rmin, Rmax) = self.slot.comp_radius()
            if self.is_internal:  # inward Slot
                # Top radius of the magnet
                Rmec = max(Rmec, Rmax)
            else:
                Rmec = min(Rmec, Rmin)

        # Handles key in the airgap
        if self.notch is not None:
            for notch in self.notch:
                if notch.has_key():
                    (Rmin, Rmax) = notch.notch_shape.comp_radius()
                    if self.is_internal:  # inward Slot
                        Rmec = max(Rmec, Rmax)
                    else:
                        Rmec = min(Rmec, Rmin)
        return Rmec

    # Inlined from Methods.Machine.LamSlot.comp_surfaces
    def comp_surfaces(self):
        """Compute the Lamination surfaces (Lamination, Ventilation, Slot).

        Parameters
        ----------
        self : LamSlot
            A LamSlot object

        Returns
        -------
        S_dict: dict
            Lamination surface dictionary (Slam, Svent, Sslot, Syoke, Steeth) [m**2]

        """

        S_dict = Lamination.comp_surfaces(self)
        if self.slot is None:
            Sslot = 0
        else:
            Sslot = self.get_Zs() * self.slot.comp_surface()

        Ryoke = self.get_Ryoke()
        Hyoke = self.comp_height_yoke()
        if self.is_internal:
            S_dict["Syoke"] = (
                np.pi * ((Ryoke + Hyoke) ** 2 - Ryoke**2) - S_dict["Svent"]
            )
        else:
            S_dict["Syoke"] = (
                np.pi * (Ryoke**2 - (Ryoke - Hyoke) ** 2) - S_dict["Svent"]
            )

        S_dict["Sslot"] = Sslot
        S_dict["Slam"] -= Sslot
        S_dict["Steeth"] = S_dict["Slam"] - S_dict["Syoke"]
        return S_dict

    # Inlined from Methods.Machine.LamSlot.get_pole_pair_number
    def get_pole_pair_number(self):
        """Return the number of pair of pole of the Lamination

        Parameters
        ----------
        self : LamSlot
            A LamSlot object

        Returns
        -------
        p: int
            Number of pair of pole

        """

        return self.slot.Zs // 2

    # Inlined from Methods.Machine.LamSlot.get_slot_desc_list
    def get_slot_desc_list(self, sym=1, is_bore=True):
        """Returns an ordered description of the slot

        Parameters
        ----------
        self : LamSlot
            A LamSlot object
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

        if self.slot.is_bore != is_bore:
            return []

        slot_list = []
        op = self.slot.comp_angle_opening()
        Zs = self.slot.Zs

        for ii in range(Zs // sym):
            slot_dict = {}
            slot_dict["begin_angle"] = 2 * np.pi / Zs * ii - op / 2 + np.pi / Zs
            slot_dict["end_angle"] = 2 * np.pi / Zs * ii + op / 2 + np.pi / Zs
            slot_dict["obj"] = self.slot
            slot_dict["lines"] = self.slot.build_geometry()
            # Apply rotation
            for line in slot_dict["lines"]:
                line.rotate((slot_dict["begin_angle"] + slot_dict["end_angle"]) / 2)
            slot_dict["label"] = "slot"
            slot_list.append(slot_dict)

        return slot_list

    # Inlined from Methods.Machine.LamSlot.get_surfaces_closing
    def get_surfaces_closing(self, sym=1):
        """Return the surfaces needed to close the radii of the Lamination

        Parameters
        ----------
        self : LamSlot
            A LamSlot object
        sym : int
            Symmetry factor (1= full machine, 2= half of the machine...)

        Returns
        -------
        surf_list : list
            List of the closing surfaces
        """

        # Get notches closing surfaces
        close_list = Lamination.get_surfaces_closing(self=self, sym=sym)
        if not hasattr(self.slot, "get_surface_opening"):
            return close_list
        else:  # Get slot closing surfaces (no surface if wedges)
            slot_pitch = 2 * np.pi / self.slot.Zs
            # for slot to draw
            for ii in range(self.slot.Zs // sym):
                slot_surf = self.slot.get_surface_opening(
                    alpha=slot_pitch * ii + slot_pitch * 0.5
                )
                for jj, surf in enumerate(slot_surf):
                    # Adapt the label
                    surf.label = update_RTS_index(
                        label=surf.label, R_id=None, T_id=jj, S_id=ii
                    )
                    close_list.append(surf)

            return close_list

    # Inlined from Methods.Machine.LamSlot.get_Zs
    def get_Zs(self):
        """Return the number of Slot of the Lamination

        Parameters
        ----------
        self : LamSlot
            a LamSlot object

        Returns
        -------
        Zs : float
            Number of Slot
        """

        if self.slot is None:
            return 0
        else:
            return self.slot.Zs

    # Inlined from Methods.Machine.LamSlot.has_magnet
    def has_magnet(self):
        """Return if LamSlot has magnets

        Parameters
        ----------
        self : LamSlot
            A LamSlot object

        Returns
        -------
        has_magnet : bool
            True if LamSlot has magnets
        """

        return (
            hasattr(self, "magnet")
            or hasattr(self, "magnet_north")
            or hasattr(self, "magnet_south")
        )

    # Inlined from Methods.Machine.LamSlot.has_slot
    def has_slot(self, is_bore=True):
        """Return if the lamination has slot on the requested radius
        (notches not taken into account, cf has_notch)

        Parameters
        ----------
        self : LamSlot
            A LamSlot object
        is_bore : bool
            True check if there are slots on the bore, else yoke

        Returns
        -------
        has_slot : bool
            True if the lamination has slot on the requested radius
        """

        if self.slot is None:
            return False
        if self.slot.is_bore is None:
            self.slot.is_bore = True  # Default value
        return self.slot.Zs != 0 and self.slot.is_bore == is_bore

    # Inlined from Methods.Machine.LamSlot.plot
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
        is_winding_connection=False,
    ):
        """Plot the Lamination with empty Slots in a matplotlib fig

        Parameters
        ----------
        self : LamSlot
            A LamSlot object
        fig : Matplotlib.figure.Figure
            existing figure to use if None create a new one
        ax : Matplotlib.axes.Axes object
            Axis on which to plot the data
        is_lam_only: bool
            True to plot only the lamination (No effect for LamSlot)
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

        Returns
        -------
        patches : list
            List of Patches

        or

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
                if self.is_stator and "Stator" not in label_leg:
                    ax.set_title("Stator with empty slot")
                elif not self.is_stator and "Rotor" not in label_leg:
                    ax.set_title("Rotor with empty slot")

                ax.legend(patch_leg, label_leg)
            if is_show_fig:
                fig.show()
            return fig, ax
        else:
            return patches

    # Inlined from Methods.Machine.LamSlot.set_pole_pair_number
    def set_pole_pair_number(self, p):
        """Set the number of pair of pole of the Lamination

        Parameters
        ----------
        self : LamSlot
            A LamSlot object
        p: int
            Number of pair of pole

        """

        self.slot.Zs = 2 * p

    class MachineCheckError(Exception):
        """ """

    class LaminationCheckError(MachineCheckError):
        """ """

    class Lam_SlotCheckError(LaminationCheckError):
        """ """

    class LSC_SlotTooLong(Lam_SlotCheckError):
        """ """


MachineCheckError = LamSlot.MachineCheckError
LaminationCheckError = LamSlot.LaminationCheckError
Lam_SlotCheckError = LamSlot.Lam_SlotCheckError
LSC_SlotTooLong = LamSlot.LSC_SlotTooLong
