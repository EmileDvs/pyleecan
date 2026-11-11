# Experimental dataclass generated from Generator/ClassesRef/Machine/LamHoleNS.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field

import numpy as np

from ..Functions_new.Geometry.transform_hole_surf import transform_hole_surf
from ..Functions_new.labels import HOLEM_LAB, decode_label
from .hole import Hole
from .lam_h import LamH
from .lamination import Lamination


@dataclass(eq=False)
class LamHoleNS(LamH):
    """Lamination with Hole with or without magnet or winding with different hole for North/South pole

    Attributes
    ----------
    hole_north : [Hole] or None
        lamination Holes for North pole
        Default: []
    hole_south : [Hole] or None
        lamination Holes for South pole
        Default: []
    """

    hole_north: list[Hole] | None = field(default_factory=list)
    """lamination Holes for North pole"""
    hole_south: list[Hole] | None = field(default_factory=list)
    """lamination Holes for South pole"""

    # Inlined from Methods.Machine.LamHoleNS._plot_arrow_mag
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
        self : LamHoleNS
            A LamHoleNS object
        ax : Matplotlib.axes.Axes object
            Axis on which to plot the arrow
        sym : int
            Symmetry factor (1= plot full machine, 2= half of the machine...)
        alpha : float
            angle for rotation (Default value = 0) [rad]
        delta : complex
            complex for translation (Default value = 0)
        """

        for hole in self.hole_north:
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
                    for ii in range(int(Zh / sym / 2)):
                        off = 0  # All north
                        if mag is not None and mag.type_magnetization == 3:
                            off -= np.pi / 2
                        Z1 = (mag_surf.point_ref + delta) * np.exp(
                            1j * (ii * 4 * np.pi / Zh + np.pi / Zh + alpha)
                        )
                        Z2 = (
                            mag_surf.point_ref
                            + delta
                            + H / 5 * np.exp(1j * (mag_dir + off))
                        ) * np.exp(1j * (ii * 4 * np.pi / Zh + np.pi / Zh + alpha))
                        ax.annotate(
                            text="",
                            xy=(Z2.real, Z2.imag),
                            xytext=(Z1.real, Z1.imag),
                            arrowprops=dict(arrowstyle="->", linewidth=1, color="b"),
                        )

        for hole in self.hole_south:
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
                    for ii in range(int(Zh / sym / 2)):
                        off = np.pi  # All north
                        if mag is not None and mag.type_magnetization == 3:
                            off -= np.pi / 2
                        Z1 = (mag_surf.point_ref + delta) * np.exp(
                            1j * (ii * 4 * np.pi / Zh + 3 * np.pi / Zh + alpha)
                        )
                        Z2 = (
                            mag_surf.point_ref
                            + delta
                            + H / 5 * np.exp(1j * (mag_dir + off))
                        ) * np.exp(1j * (ii * 4 * np.pi / Zh + 3 * np.pi / Zh + alpha))
                        ax.annotate(
                            text="",
                            xy=(Z2.real, Z2.imag),
                            xytext=(Z1.real, Z1.imag),
                            arrowprops=dict(arrowstyle="->", linewidth=1, color="b"),
                        )

    # Inlined from Methods.Machine.LamHoleNS.build_geometry
    def build_geometry(self, sym=1, alpha=0, delta=0, is_circular_radius=False):
        """Build the geometry of the LamHoleNS object

        Parameters
        ----------
        self : LamHoleNS
            The LamHoleNS to build in surface
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
        ii = 0
        for hole in self.hole_north:
            # Create the first hole surface(s)
            surf_hole = hole.build_geometry(alpha=np.pi / hole.Zh)
            surf_list.extend(
                transform_hole_surf(
                    hole_surf_list=surf_hole,
                    Zh=int(hole.Zh / 2),
                    sym=sym,
                    alpha=0,
                    delta=0,
                )
            )
        # Holes surface(s)
        for hole in self.hole_south:
            surf_hole = hole.build_geometry(alpha=2 * np.pi / hole.Zh)
            surf_list.extend(
                transform_hole_surf(
                    hole_surf_list=surf_hole,
                    Zh=int(hole.Zh / 2),
                    sym=sym,
                    alpha=np.pi / hole.Zh,
                    delta=0,
                )
            )

        # Apply the transformations
        for surf in surf_list:
            surf.rotate(alpha)
            surf.translate(delta)

        return surf_list

    # Inlined from Methods.Machine.LamHoleNS.comp_masses
    def comp_masses(self):
        """Compute the Lamination masses

        Parameters
        ----------
        self : LamHoleNS
            A LamHoleNS object

        Returns
        -------
        M_dict: dict
            Lamination mass dictionary (Mtot, Mlam, Mmag) [kg]

        """

        M_dict = LamH.comp_masses(self)

        # Magnets are counted twice (Zh = 2*p for both north and south)
        M_dict["Mmag"] = M_dict["Mmag"] / 2
        M_dict["Mtot"] -= M_dict["Mmag"]

        return M_dict

    # Inlined from Methods.Machine.LamHoleNS.comp_periodicity_geo
    def comp_periodicity_geo(self):
        """Compute the geometric periodicity factor of the lamination

        Parameters
        ----------
        self : LamHoleNS
            A LamHoleNS object

        Returns
        -------
        per_a : int
            Number of spatial periodicities of the lamination
        is_antiper_a : bool
            True if an spatial anti-periodicity is possible after the periodicities
        """

        return self.comp_periodicity_spatial()

    # Inlined from Methods.Machine.LamHoleNS.comp_periodicity_spatial
    def comp_periodicity_spatial(self):
        """Compute the periodicity factor of the lamination

        Parameters
        ----------
        self : LamHoleNS
            A LamHoleNS object

        Returns
        -------
        per_a : int
            Number of spatial periodicities of the lamination
        is_antiper_a : bool
            True if an spatial anti-periodicity is possible after the periodicities
        """

        p = self.get_pole_pair_number()

        nb_list = [p]
        # account for notches and bore
        if self.notch is not None:
            for notch in self.notch:
                nb_list.append(notch.comp_periodicity_spatial()[0])

        if self.bore:
            nb_list.append(self.bore.comp_periodicity_spatial()[0])
        if self.yoke:
            nb_list.append(self.yoke.comp_periodicity_spatial()[0])

        # compute the gcd of the list
        if len(nb_list) == 1:
            per_a = nb_list[0]
        else:
            per_a = np.gcd(nb_list[0], nb_list[1])
            for ii in range(2, len(nb_list)):
                per_a = np.gcd(per_a, nb_list[ii])
        is_antiper_a = False

        # Account for duct periodicity
        per_a, is_antiper_a = self.comp_periodicity_duct_spatial(per_a, is_antiper_a)
        per_a = int(per_a)

        return per_a, is_antiper_a

    # Inlined from Methods.Machine.LamHoleNS.comp_surfaces
    def comp_surfaces(self):
        """Compute the Lamination surfaces

        Parameters
        ----------
        self : LamHoleNS
            A LamHoleNS object

        Returns
        -------
        S_dict: dict
            Lamination surface dictionary (Slam, Svent, Smag, Shole) [m**2]

        """

        S_dict = LamH.comp_surfaces(self)

        # Magnets are counted twice (Zh = 2*p for both north and south)
        S_dict["Smag"] = S_dict["Smag"] / 2
        S_dict["Shole"] = S_dict["Shole"] / 2
        S_dict["Slam"] += S_dict["Shole"]
        S_dict["Steeth"] += S_dict["Shole"]

        return S_dict

    # Inlined from Methods.Machine.LamHoleNS.comp_volumes
    def comp_volumes(self):
        """Compute the Lamination volumes

        Parameters
        ----------
        self : LamHoleNS
            A LamHoleNS object

        Returns
        -------
        V_dict: dict
            Lamination volume dictionary (Vlam, Vvent, Vmag, Vhole) [m**3]

        """

        V_dict = LamH.comp_volumes(self)

        # Magnets are counted twice (Zh = 2*p for both north and south)
        V_dict["Vmag"] = V_dict["Vmag"] / 2
        V_dict["Vhole"] = V_dict["Vhole"] / 2

        return V_dict

    # Inlined from Methods.Machine.LamHoleNS.get_hole_list
    def get_hole_list(self):
        """Return the list of all the holes (North and South)

        Parameters
        ----------
        self : LamHoleNS
            A LamHoleNS object

        Returns
        -------
        hole_list : [Hole]
            List of all the holes (North and South)
        """
        hole_list = []
        hole_list.extend(self.hole_north)
        hole_list.extend(self.hole_south)

        return hole_list

    # Inlined from Methods.Machine.LamHoleNS.get_magnet_number
    def get_magnet_number(self, sym=1):
        """Return the number of magnet on the Lamination

        Parameters
        ----------
        self : LamHoleNS
            A LamHoleNS object
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
        # There are Zs / sym poles
        # get_hole_list returns the hole for one North and one South
        return int((self.get_Zs() / 2) / sym * nb_mag_per_hole)
