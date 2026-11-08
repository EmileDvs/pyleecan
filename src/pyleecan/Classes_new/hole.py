# Experimental dataclass generated from Generator/ClassesRef/Slot/Hole.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field
from typing import Any

import numpy as np
from matplotlib.patches import Patch

from ..definitions import config_dict
from ..Functions.Geometry.transform_hole_surf import transform_hole_surf
from ..Functions.init_fig import init_fig
from ..Functions.labels import HOLEM_LAB, HOLEV_LAB, VENT_LAB, decode_label
from ._error import ParentMissingError
from ._import import import_class
from ._pyleecan_class import PyleecanClass
from .material import Material


@dataclass(eq=False)
class Hole(PyleecanClass):
    """Holes for lamination (abstract)

    Attributes
    ----------
    Zh : int
        Number of Hole around the circumference
        Default: 36; Minimum: 0
    mat_void : Material or None
        Material of the void part of the hole (Air in general)
        Default: None
    magnetization_dict_offset : dict or None
        Dictionary add an offset to the magnetization direction of the magnets (key=magnet_X, value=angle[rad])
        Default: {}
    Alpha0 : float
        Shift angle of the holes around circumference
        Unit: rad; Default: 0; Minimum: 0; Maximum: 6.29
    """

    MAGNET_COLOR = config_dict["PLOT"]["COLOR_DICT"]["MAGNET_COLOR"]
    ARROW_COLOR = config_dict["PLOT"]["COLOR_DICT"]["STATOR_COLOR"]
    Zh: int = 36
    """Number of Hole around the circumference"""
    mat_void: Material | None = None
    """Material of the void part of the hole (Air in general)"""
    magnetization_dict_offset: dict[str, Any] | None = field(default_factory=dict)
    """Dictionary add an offset to the magnetization direction of the magnets (key=magnet_X, value=angle[rad])"""
    Alpha0: float = 0
    """Shift angle of the holes around circumference"""

    # Inlined from Methods.Slot.Hole.comp_height
    def comp_height(self):
        """Compute the height of the Hole (Rmax-Rmin)

        Parameters
        ----------
        self : Hole
            A Hole object

        Returns
        -------
        H : float
            Height of the hole

        """

        (Rmin, Rmax) = self.comp_radius()
        return Rmax - Rmin

    # Inlined from Methods.Slot.Hole.comp_magnetization_dict
    def comp_magnetization_dict(self, is_north=True):
        """Compute the dictionary of the magnetization direction of the magnets (key=magnet_X, value=angle[rad])
        Mangetization angle with Hole centered on Ox axis

        Parameters
        ----------
        self : Hole
            a Hole object
        is_north: True
            True: comp north magnetization, else add pi [rad]

        Returns
        -------
        mag_dict: dict
            magnetization dictionary (key=magnet_X, value=angle[rad])
        """

        if self.magnetization_dict_offset is not None:
            mag_dict = self.magnetization_dict_offset.copy()
            if not is_north:
                for key in mag_dict.keys():
                    mag_dict[key] += np.pi
            return mag_dict
        else:
            return {}

    # Inlined from Methods.Slot.Hole.comp_radius
    def comp_radius(self):
        """Compute the radius of the min and max circle that contains the hole

        Parameters
        ----------
        self : Hole
            A Hole object

        Returns
        -------
        (Rmin,Rmax): tuple
            Radius of the circle that contains the hole

        """

        surf_list = self.build_geometry()
        point_list = []
        for surf in surf_list:
            for curve in surf.get_lines():
                point_list.extend(curve.discretize())

        abs_list = [np.abs(point) for point in point_list]
        Rmax = max(abs_list)
        Rmin = min(abs_list)
        return (Rmin, Rmax)

    # Inlined from Methods.Slot.Hole.comp_surface
    def comp_surface(self):
        """Compute the Hole total surface (by numerical computation).

        Parameters
        ----------
        self : Hole
            A Hole object

        Returns
        -------
        S : float
            Slot total surface [m**2]

        """

        surf_list = self.build_geometry()
        S = 0
        for surf in surf_list:
            S += surf.comp_surface()

        return S

    # Inlined from Methods.Slot.Hole.convert_to_UD
    def convert_to_UD(self):
        """Convert the hole to HoleUD"""
        HoleUD = import_class("HoleUD")
        surf_list = self.build_geometry()
        magnet_dict = self.get_magnet_dict()
        magnetization_dict = self.comp_magnetization_dict()

        return HoleUD(
            surf_list=surf_list,
            magnet_dict=magnet_dict,
            Zh=self.Zh,
            mat_void=self.mat_void,
            magnetization_dict_offset=magnetization_dict,
        )

    # Inlined from Methods.Slot.Hole.get_is_stator
    def get_is_stator(self):
        """Return True if the parent lamination is stator and False if is a rotor

        Parameters
        ----------
        self : Hole
            A Hole object

        Returns
        -------
        is_stator: bool
            True if the Lamination is a stator and False if not
        """

        if self.parent is not None:
            return self.parent.is_stator
        else:
            raise ParentMissingError("Error: The hole is not inside a Lamination")

    # Inlined from Methods.Slot.Hole.get_magnet_by_id
    def get_magnet_by_id(self, index):
        """Return the magnet at the corresponding index
        returns None is the magnet is None
        Raise error if the hole doesn't have a magnet for the corresponding index

        Parameters
        ----------
        self : Hole
            A Hole object
        index : int
            Index of the magnet to return
        Returns
        -------
        magnet : Magnet
            Magnet object (or None)
        """

        label = "magnet_" + str(index)
        if hasattr(self, label):
            return getattr(self, label)
        elif hasattr(self, "magnet_dict") and label in self.magnet_dict:
            return self.magnet_dict[label]
        else:
            raise self.MagnetIndexError(
                "Hole of type " + str(type(self)) + " has no magnet " + label
            )

    # Inlined from Methods.Slot.Hole.get_magnet_dict
    def get_magnet_dict(self):
        """Return a dictionary with all the magnets of the Hole

        Parameters
        ----------
        self : Hole
            A Hole object

        Returns
        -------
        magnet_dict : {Magnet}
            Dictionary of magnet (key = magnet_X, value= Magnet or None)
        """

        if hasattr(self, "magnet_dict"):
            return self.magnet_dict
        else:
            ii = 0
            magnet_dict = {}
            while hasattr(self, "magnet_" + str(ii)):
                magnet_dict["magnet_" + str(ii)] = getattr(self, "magnet_" + str(ii))
                ii += 1
            return magnet_dict

    # Inlined from Methods.Slot.Hole.get_R_id
    def get_R_id(self):
        """Return the "Radial" index for label (index in lam.hole or lam.axial_vent)

        Parameters
        ----------
        self : Hole
            A Hole object

        Returns
        -------
        R_id : int
            "Radial" index of the hole in the lamination
        surf_type : str
            Label to use for the surface type (HoleV or Vent)
        """

        if self.parent is None:  # Compatibility For plotting
            return (0, HOLEV_LAB)
        elif (
            hasattr(self.parent, "get_hole_list")
            and self in self.parent.get_hole_list()
        ):
            return (self.parent.get_hole_list().index(self), HOLEV_LAB)
        elif self.parent.axial_vent is not None and self in self.parent.axial_vent:
            return (self.parent.axial_vent.index(self), VENT_LAB)
        else:
            raise Exception("Error, impossible to get Hole R-id")

    # Inlined from Methods.Slot.Hole.get_Rbo
    def get_Rbo(self):
        """Return the parent lamination bore radius

        Parameters
        ----------
        self : Hole
            A Hole object

        Returns
        -------
        Rbo: float
            The parent lamination bore radius [m]

        """

        if self.parent is not None:
            return self.parent.get_Rbo()
        else:
            raise ParentMissingError("Error: The hole is not inside a Lamination")

    # Inlined from Methods.Slot.Hole.get_Rext
    def get_Rext(self):
        """Return the parent lamination exterior radius

        Parameters
        ----------
        self : Hole
            A Hole object

        Returns
        -------
        Rext: float
            The parent lamination exterior radius [m]

        """

        if self.parent is not None:
            return self.parent.Rext
        else:
            raise ParentMissingError("Error: The hole is not inside a Lamination")

    # Inlined from Methods.Slot.Hole.has_magnet
    def has_magnet(self):
        """Return if the Hole has magnets

        Parameters
        ----------
        self : Hole
            A Hole object

        Returns
        -------
        has_magnet : bool
            False

        """

        return False

    # Inlined from Methods.Slot.Hole.plot
    def plot(
        self,
        fig=None,
        ax=None,
        title=None,
        display_magnet=True,
        is_add_arrow=False,
        is_add_ref=False,
        is_show_fig=True,
        is_all_hole=False,
    ):
        """Plot the Hole in a matplotlib fig

        Parameters
        ----------
        self : Hole
            A Hole object
        fig :
            if None, open a new fig and plot, else add to the current
            one (Default value = None)
        title: str
            Figure title
        display_magnet : bool
            if True, plot the magnet inside the hole, if there is any (Default value = True)
        is_add_arrow : bool
            To add an arrow for the magnetization
        is_add_ref : bool
            True to add the reference points of the surfaces
        is_all_hole : bool
            True to plot the Zh holes

        Returns
        -------
        fig : Matplotlib.figure.Figure
            Figure containing the plot
        ax : Matplotlib.axes.Axes object
            Axis containing the plot
        """

        display = fig is None
        if display:
            color = "k"
        else:
            color = "w"

        surf_hole = self.build_geometry()
        if is_all_hole:
            # Duplicate the hole surfaces
            surf_hole = transform_hole_surf(
                hole_surf_list=surf_hole, Zh=self.Zh, sym=1, alpha=0, delta=0
            )

        patches = []
        for surf in surf_hole:
            label_dict = decode_label(surf.label)
            if HOLEM_LAB in label_dict["surf_type"] and display_magnet:
                patches.extend(surf.get_patches(color=self.MAGNET_COLOR))
            else:
                patches.extend(surf.get_patches(color=color))

        # Display the result
        (fig, ax, patch_leg, label_leg) = init_fig(fig, ax)
        ax.set_xlabel("(m)")
        ax.set_ylabel("(m)")
        if title is None:
            ax.set_title("Hole")
        else:
            ax.set_title(title)
        # Add all the hole (and magnet) to fig
        for patch in patches:
            ax.add_patch(patch)

        # Magnetization
        if is_add_arrow:
            H = self.comp_height()
            mag_dict = self.comp_magnetization_dict()
            for magnet_name, mag_dir in mag_dict.items():
                # Get the correct surface
                mag_surf = None
                mag_id = int(magnet_name.split("_")[-1])
                for surf in surf_hole:
                    label_dict = decode_label(surf.label)
                    if (
                        HOLEM_LAB in label_dict["surf_type"]
                        and label_dict["T_id"] == mag_id
                    ):
                        mag_surf = surf
                        break
                # Create arrow coordinates
                Z1 = mag_surf.point_ref
                Z2 = mag_surf.point_ref + H / 5 * np.exp(1j * mag_dir)
                ax.annotate(
                    text="",
                    xy=(Z2.real, Z2.imag),
                    xytext=(Z1.real, Z1.imag),
                    arrowprops=dict(
                        arrowstyle="->", linewidth=1, color=self.ARROW_COLOR
                    ),
                )

        # Add reference point
        if is_add_ref:
            for surf in self.surf_list:
                ax.plot(surf.point_ref.real, surf.point_ref.imag, "rx")

        # Axis Setup
        ax.axis("equal")
        try:
            Lim = self.get_Rbo() * 1.2
            ax.set_xlim(-Lim, Lim)
            ax.set_ylim(-Lim, Lim)
        except ParentMissingError:
            pass

        if display_magnet and HOLEM_LAB in [surf.label for surf in surf_hole]:
            patch_leg.append(Patch(color=self.MAGNET_COLOR))
            label_leg.append("Magnet")
            ax.legend(patch_leg, label_leg)
        if is_show_fig:
            fig.show()
        return fig, ax

    # Inlined from Methods.Slot.Hole.set_magnet_by_id
    def set_magnet_by_id(self, index, magnet):
        """Set the magnet at the corresponding index
        Raise error if the hole doesn't have a magnet for the corresponding index

        Parameters
        ----------
        self : Hole
            A Hole object
        index : int
            Index of the magnet to return
        magnet : Magnet
            Magnet object to set (or None)
        """

        label = "magnet_" + str(index)
        if hasattr(self, label):
            setattr(self, label, magnet)
        elif hasattr(self, "magnet_dict") and label in self.magnet_dict:
            self.magnet_dict[label] = magnet
        else:
            raise self.MagnetIndexError(
                "Hole of type " + str(type(self)) + " has no magnet " + label
            )

    class MagnetIndexError(Exception):
        """Raise when trying to access a non existing magnet"""
