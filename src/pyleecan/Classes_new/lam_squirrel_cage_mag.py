# Experimental dataclass generated from Generator/ClassesRef/Machine/LamSquirrelCageMag.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field

import numpy as np

from ..Functions_new.init_fig import init_fig
from ..Functions_new.labels import update_RTS_index
from .hole import Hole
from .lam_slot_wind import LamSlotWind
from .lam_squirrel_cage import LamSquirrelCage


@dataclass(eq=False)
class LamSquirrelCageMag(LamSquirrelCage):
    """Rotor lamination for LSPM

    Attributes
    ----------
    hole : [Hole] or None
        lamination Hole
        Default: []
    """

    hole: list[Hole] | None = field(default_factory=list)
    """lamination Hole"""

    # Inlined from Methods.Machine.LamSquirrelCageMag.build_geometry
    def build_geometry(self, sym=1, alpha=0, delta=0, is_circular_radius=False):
        """Build geometry of the LamSquirrelCage

        Parameters
        ----------
        self : LamSquirrelCageMag
            A LamSquirrelCageMag Object
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

        # Lamination label
        if self.is_stator:
            label = "Lamination_Stator"
        else:
            label = "Lamination_Rotor"

        surf_list = LamSquirrelCage.build_geometry(
            self,
            sym=sym,
            is_circular_radius=is_circular_radius,
            alpha=alpha,
            delta=delta,
        )

        # Holes surface(s)
        for hole in self.get_hole_list():
            Zh = hole.Zh
            assert (Zh % sym) == 0, (
                "ERROR, Wrong symmetry for "
                + label
                + " "
                + str(Zh)
                + " holes and sym="
                + str(sym)
            )  # For now only
            angle = 2 * np.pi / Zh
            # Create the first hole surface(s)
            surf_hole = hole.build_geometry(alpha=np.pi / Zh)

            hole_surf_list = []
            # Copy the hole for Zh / sym
            for ii in range(Zh // sym):
                for surf in surf_hole:
                    new_surf = type(surf)(init_dict=surf.as_dict())
                    new_surf.label = update_RTS_index(label=new_surf.label, S_id=ii)
                    new_surf.rotate(ii * angle)
                    hole_surf_list.append(new_surf)

        # Apply the transformations
        for surf in hole_surf_list:
            surf.rotate(alpha)
            surf.translate(delta)

        surf_list.extend(hole_surf_list)
        return surf_list

    # Inlined from Methods.Machine.LamSquirrelCageMag.check
    def check(self):
        """Check that the Lamination object is correct

        Parameters
        ----------
        self : LamSquirrelCageMag
            A LamSquirrelCageMag object

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

        LamSquirrelCage.check(self)

        # Check p
        p = self.winding.p
        assert len(self.hole) > 1
        for hole in self.hole:
            assert hole.Zh / 2 == p

    # Inlined from Methods.Machine.LamSquirrelCageMag.comp_surfaces
    def comp_surfaces(self):
        """Compute the Lamination surfaces

        Parameters
        ----------
        self : LamSquirrelCageMag
            A LamSquirrelCageMag object

        Returns
        -------
        S_dict: dict
            Lamination surface dictionary (Slam, Svent, Smag, Shole) [m**2]

        """

        S_dict = LamSlotWind.comp_surfaces(self)

        # hole surface
        Shole = 0
        Smag = 0
        for hole in self.hole:
            Shole += hole.Zh * hole.comp_surface()
            if hole.has_magnet():
                Smag += hole.Zh * hole.comp_surface_magnets()

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

        S_dict["Smag"] = Smag
        S_dict["Shole"] = Shole
        S_dict["Slam"] -= Shole  # the magnet surface in included in the hole one
        S_dict["Steeth"] = S_dict["Slam"] - S_dict["Syoke"]

        return S_dict

    # Inlined from Methods.Machine.LamSquirrelCageMag.get_hole_list
    def get_hole_list(self):
        """Return the list of all the holes

        Parameters
        ----------
        self : LamSquirrelCageMag
            A LamSquirrelCageMag object

        Returns
        -------
        hole_list : [Hole]
            List of all the holes
        """
        if self.hole is None:
            self.hole = []
        return self.hole

    # Inlined from Methods.Machine.LamSquirrelCageMag.get_pole_pair_number
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

        p = self.winding.p

        for hole in self.hole:
            assert hole.Zh / 2 == p

        return p

    # Inlined from Methods.Machine.LamSquirrelCageMag.plot
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

        # Plot the lamination (LamSquirrelCage)
        super(type(self), self).plot(
            fig=fig,
            is_lam_only=is_lam_only,
            sym=sym,
            alpha=alpha,
            delta=delta,
            is_edge_only=is_edge_only,
            is_show_fig=is_show_fig,
        )

        # Display the result
        ax.set_xlabel("(m)")
        ax.set_ylabel("(m)")
        ax.set_title("Squirrel Cage Rotor with Magnets")

        # Axis Setup
        ax.axis("equal")
        Lim = self.Rext * 1.5
        ax.set_xlim(-Lim, Lim)
        if sym == 1:
            ax.set_ylim(-Lim, Lim)
        else:
            ax.set_ylim(-Lim * 0.3, Lim)

        if not is_lam_only:
            ax.legend(patch_leg, label_leg)
        if is_show_fig:
            fig.show()
        return fig, ax

    # Inlined from Methods.Machine.LamSquirrelCageMag.set_pole_pair_number
    def set_pole_pair_number(self, p):
        """Set the number of pair of pole of the Lamination

        Parameters
        ----------
        self : LamSquirrelCageMag
            A LamSquirrelCageMag object
        p: int
            Number of pair of pole

        """

        if self.winding is not None:
            self.winding.p = p
        if self.hole is not None:
            for hole in self.hole:
                hole.Zh = 2 * p
