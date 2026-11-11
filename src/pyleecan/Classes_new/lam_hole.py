# Experimental dataclass generated from Generator/ClassesRef/Machine/LamHole.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

import numpy as np

from ..Functions_new.Geometry.transform_hole_surf import transform_hole_surf
from ..Functions_new.labels import HOLEM_LAB, decode_label
from .hole import Hole
from .lam_h import LamH
from .lamination import Lamination


@dataclass(eq=False)
class LamHole(LamH):
    """Lamination with Hole with or without magnet or winding

    Attributes
    ----------
    hole : [Hole] or None
        lamination Hole
        Default: None
    """

    hole: list[Hole] | None = None
    """lamination Hole"""

    # Inlined from Methods.Machine.LamHole._plot_arrow_mag
    def _plot_arrow_mag(
        self,
        ax=None,
        sym=1,
        alpha=0,
        delta=0,
    ):
        """Plot the magnetization direction as arrow on top of the lamination
        (meant to be called by LamHole.plot)

        Parameters
        ----------
        self : LamHole
            A LamHole object
        ax : Matplotlib.axes.Axes object
            Axis on which to plot the arrow
        sym : int
            Symmetry factor (1= plot full machine, 2= half of the machine...)
        alpha : float
            angle for rotation (Default value = 0) [rad]
        delta : complex
            complex for translation (Default value = 0)
        """

        for hole in self.hole:
            H = hole.comp_height()
            mag_dict = hole.comp_magnetization_dict()
            for magnet_name, mag_dir in mag_dict.items():
                # Get the correct surface
                mag_surf = None
                mag_id = int(magnet_name.split("_")[-1])
                mag = hole.get_magnet_by_id(mag_id)
                if mag is not None:
                    for surf in hole.build_geometry():
                        label_dict = decode_label(surf.label)
                        if (
                            HOLEM_LAB in label_dict["surf_type"]
                            and label_dict["T_id"] == mag_id
                        ):
                            mag_surf = surf
                            break
                    # Create arrow coordinates
                    Zh = hole.Zh
                    for ii in range(int(Zh / sym)):
                        off = np.pi if ii % 2 == 1 else 0
                        if mag is not None and mag.type_magnetization == 3:
                            off -= np.pi / 2
                        Z1 = (mag_surf.point_ref + delta) * np.exp(
                            1j * (ii * 2 * np.pi / Zh + np.pi / Zh + alpha)
                        )
                        Z2 = (
                            mag_surf.point_ref
                            + delta
                            + H / 5 * np.exp(1j * (mag_dir + off))
                        ) * np.exp(1j * (ii * 2 * np.pi / Zh + np.pi / Zh + alpha))
                        ax.annotate(
                            text="",
                            xy=(Z2.real, Z2.imag),
                            xytext=(Z1.real, Z1.imag),
                            arrowprops=dict(arrowstyle="->", linewidth=1, color="b"),
                        )

    # Inlined from Methods.Machine.LamHole.build_geometry
    def build_geometry(self, sym=1, alpha=0, delta=0, is_circular_radius=False):
        """Build the geometry of the LamHole object

        Parameters
        ----------
        self : LamHole
            The LamHole to build in surface
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
        surf_list : list
            list of surfaces needed to draw the lamination

        """

        # getting the Lamination surface
        surf_list = Lamination.build_geometry(
            self,
            sym=sym,
            alpha=alpha,
            delta=delta,
            is_circular_radius=is_circular_radius,
        )

        # Holes surface(s)
        for hole in self.hole:
            # Create the first hole surface(s)
            surf_hole = hole.build_geometry(alpha=np.pi / hole.Zh)
            surf_list.extend(
                transform_hole_surf(
                    hole_surf_list=surf_hole, Zh=hole.Zh, sym=sym, alpha=0, delta=0
                )
            )

        # Apply the transformations
        for surf in surf_list:
            surf.rotate(alpha)
            surf.translate(delta)

        return surf_list

    # Inlined from Methods.Machine.LamHole.get_hole_list
    def get_hole_list(self):
        """Return the list of all the holes

        Parameters
        ----------
        self : LamHole
            A LamHole object

        Returns
        -------
        hole_list : [Hole]
            List of all the holes
        """
        if self.hole is None:
            self.hole = []
        return self.hole

    # Inlined from Methods.Machine.LamHole.get_magnet_number
    def get_magnet_number(self, sym=1):
        """Return the number of magnet on the Lamination

        Parameters
        ----------
        self : LamHole
            A LamHole object
        sym : int
            Symmetry factor (1= full machine, 2= half of the machine...)

        Returns
        -------
        N_mag : int
            Number of magnets on the lamination
        """

        # Each hole can have several magnets
        nb_mag_per_hole = 0
        for hole in self.get_hole_list():
            nb_mag_per_hole += len(hole.get_magnet_dict())
        # There are Zs / sym holes of each set
        return int(self.get_Zs() / sym * nb_mag_per_hole)
