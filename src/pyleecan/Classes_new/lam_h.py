# Experimental dataclass generated from Generator/ClassesRef/Machine/LamH.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch

from ..Functions_new.init_fig import init_fig
from ..Functions_new.Plot.get_color_legend_from_surface import (
    get_color_legend_from_surface,
)
from .hole import Hole
from .lamination import Lamination


@dataclass(eq=False)
class LamH(Lamination):
    """Lamination with Hole (Abstract class)

    Attributes
    ----------
    """

    # Inlined from Methods.Machine.LamH.comp_angle_d_axis
    def comp_angle_d_axis(self):
        """Compute the angle between the X axis and the first d+ axis
        By convention a "Tooth" is centered on the X axis
        By convention the first magnet is +

        Parameters
        ----------
        self : LamH
            A LamH object

        Returns
        -------
        d_angle : float
            angle between the X axis and the first d+ axis
        """

        p = self.get_pole_pair_number()
        if self.has_magnet():
            return np.pi / p / 2
        else:
            return 0

    # Inlined from Methods.Machine.LamH.comp_height_yoke
    def comp_height_yoke(self):
        """Compute the yoke height

        Parameters
        ----------
        self : LamH
            A LamH object

        Returns
        -------
        Hy: float
            yoke height [m]

        """

        if self.is_internal:
            R = self.Rext
        else:
            R = self.Rint

        # The yoke is define the greater cylinder without holes
        for hole in self.get_hole_list():
            (Rmin, Rmax) = hole.comp_radius()
            if self.is_internal:
                R = min(R, Rmin)
            else:
                R = max(R, Rmax)

        if self.is_internal:
            return R - self.Rint
        else:
            return self.Rext - R

    # Inlined from Methods.Machine.LamH.comp_masses
    def comp_masses(self):
        """Compute the Lamination masses

        Parameters
        ----------
        self : LamH
            A LamH object

        Returns
        -------
        M_dict: dict
            Lamination mass dictionary (Mtot, Mlam, Mmag) [kg]

        """

        M_dict = Lamination.comp_masses(self)

        Mmag = 0
        for hole in self.get_hole_list():
            if hole.has_magnet():
                Mmag += hole.Zh * hole.comp_mass_magnets()

        M_dict["Mmag"] = Mmag
        M_dict["Mtot"] += Mmag

        return M_dict

    # Inlined from Methods.Machine.LamH.comp_radius_mid_yoke
    def comp_radius_mid_yoke(self):
        """Compute the Lamination middle of the yoke radius

        Parameters
        ----------
        self : LamH
            A LamH object

        Returns
        -------
        Ry: float
            middle of the yoke radius [m]

        """

        Rmin = self.Rext
        Rmax = self.Rint
        for hole in self.get_hole_list():
            if type(hole) is not Hole:
                (Rmin_hole, Rmax_hole) = hole.comp_radius()
                Rmin = min(Rmin, Rmin_hole)
                Rmax = max(Rmax, Rmax_hole)
        if self.is_internal:
            return (self.Rint + Rmin) / 2
        else:
            return (self.Rext + Rmax) / 2

    # Inlined from Methods.Machine.LamH.comp_surfaces
    def comp_surfaces(self):
        """Compute the Lamination surfaces

        Parameters
        ----------
        self : LamH
            A LamH object

        Returns
        -------
        S_dict: dict
            Lamination surface dictionary (Slam, Svent, Smag, Shole) [m**2]

        """

        S_dict = Lamination.comp_surfaces(self)

        # hole surface
        Shole = 0
        Smag = 0
        for hole in self.get_hole_list():
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

    # Inlined from Methods.Machine.LamH.comp_volumes
    def comp_volumes(self):
        """Compute the Lamination volumes

        Parameters
        ----------
        self : LamH
            A LamH object

        Returns
        -------
        V_dict: dict
            Lamination volume dictionary (Vlam, Vvent, Vmag, Vhole) [m**3]

        """

        V_dict = Lamination.comp_volumes(self)
        Lt = self.comp_length()

        Vhole = 0
        Vmag = 0
        for hole in self.get_hole_list():
            Vhole += hole.Zh * hole.comp_surface() * Lt
            if hole.has_magnet():
                Vmag += hole.Zh * hole.comp_volume_magnets()

        V_dict["Vmag"] = Vmag
        V_dict["Vhole"] = Vhole

        return V_dict

    # Inlined from Methods.Machine.LamH.get_pole_pair_number
    def get_pole_pair_number(self):
        """Return the number of pair of pole of the Lamination

        Parameters
        ----------
        self : LamH
            A LamH object

        Returns
        -------
        p: int
            Number of pair of pole

        """

        hole_list = self.get_hole_list()
        if len(hole_list) > 0:
            return hole_list[0].Zh // 2
        else:
            return None

    # Inlined from Methods.Machine.LamH.get_Zs
    def get_Zs(self):
        """Return the number of holes in the lamination

        Parameters
        ----------
        self : LamH
            A LamH object

        Returns
        -------
        p: int
            Number of pair of pole

        """

        return self.get_pole_pair_number() * 2

    # Inlined from Methods.Machine.LamH.has_magnet
    def has_magnet(self):
        """Return if any of the Holes have magnets

        Parameters
        ----------
        self : LamH
            A LamH object

        Returns
        -------
        has_magnet : bool
            True if any of the Holes have magnets
        """

        has_mag = [hole.has_magnet() for hole in self.get_hole_list()]
        return any(has_mag)

    # Inlined from Methods.Machine.LamH.plot
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
        save_path=None,
        win_title=None,
        is_clean_plot=False,
        is_winding_connection=False,
    ):
        """Plot a Lamination with Buried Magnets in a matplotlib fig

        Parameters
        ----------
        self : LamH
            A LamH object
        fig : Matplotlib.figure.Figure
            existing figure to use if None create a new one
        ax : Matplotlib.axes.Axes object
            Axis on which to plot the data
        is_lam_only: bool
            True to plot only the lamination (remove the magnets)
        sym : int
            Symmetry factor (1= plot full machine, 2= half of the machine...)
        alpha : float
            angle for rotation (Default value = 0) [rad]
        delta : complex
            complex for translation (Default value = 0)
        is_edge_only: bool
            To plot transparent Patches
        edgecolor:
            Color of the edges if is_edge_only=True
        is_add_arrow : bool
            To add an arrow for the magnetization
        is_show_fig : bool
            To call show at the end of the method
        save_path : str
            full path including folder, name and extension of the file to save if save_path is not None
        win_title : str
            Window title
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

        # Lamination bore
        if self.is_stator:
            lam_name = "Stator"
        else:
            lam_name = "Rotor"

        # List of surface to plot the lamination
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

        ax.set_xlabel("(m)")
        ax.set_ylabel("(m)")

        for patch in patches:
            ax.add_patch(patch)

        # Add Magnetization arrow
        if is_add_arrow:
            self._plot_arrow_mag(ax=ax, sym=sym, alpha=alpha, delta=delta)

        # Axis Setup
        ax.axis("equal")

        # The Lamination is centered in the figure
        Lim = self.Rext * 1.5
        ax.set_xlim(-Lim, Lim)
        ax.set_ylim(-Lim, Lim)

        # Window title
        if (
            win_title is None
            and self.parent is not None
            and self.parent.name not in [None, ""]
        ):
            win_title = self.parent.name + " " + lam_name
        elif win_title is None:
            win_title = lam_name
        manager = plt.get_current_fig_manager()
        if manager is not None:
            manager.set_window_title(win_title)

        # Set legend
        if not is_edge_only:
            ax.set_title(f"{lam_name} with Interior Magnet")
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
        if save_path is not None:
            fig.savefig(save_path)
            plt.close(fig=fig)
        return fig, ax

    # Inlined from Methods.Machine.LamH.set_Lmag
    def set_Lmag(self, value):
        """Set the Length of the magnet

        Parameters
        ----------
        self : LamH
            A LamH object
        value : float
            Value to set [m]
        """

        for hole in self.get_hole_list():
            mag_dict = hole.get_magnet_dict()
            for mag in mag_dict.values():
                mag.Lmag = value

    # Inlined from Methods.Machine.LamH.set_pole_pair_number
    def set_pole_pair_number(self, p):
        """Set the number of pair of pole of the Lamination

        Parameters
        ----------
        self : LamH
            A LamH object
        p: int
            Number of pair of pole

        """

        for hole in self.get_hole_list():
            hole.Zh = 2 * p
