# Experimental dataclass generated from Generator/ClassesRef/Machine/NotchEvenDist.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field

import numpy as np

from ..Functions_new.Geometry.transform_hole_surf import transform_hole_surf
from ..Functions_new.labels import KEY_LAB, YSNL_LAB, YSNR_LAB
from .notch import Notch
from .slot import Slot


@dataclass(eq=False)
class NotchEvenDist(Notch):
    """Class for evenly distributed notches (according to Zs)

    Attributes
    ----------
    alpha : float
        angular positon of the first notch (0 is middle of first tooth)
        Unit: rad; Default: 0
    notch_shape : Slot or None
        Shape of the Notch
        Default: Slot()
    """

    alpha: float = 0
    """angular positon of the first notch (0 is middle of first tooth)"""
    notch_shape: Slot | None = field(
        default_factory=lambda: Slot(), metadata={"default_class": "Slot"}
    )
    """Shape of the Notch"""

    # Inlined from Methods.Machine.NotchEvenDist.build_geometry_key
    def build_geometry_key(self, index=0, sym=1, alpha=0, delta=0):
        """Build the geometry of the keys inside the notch

        Parameters
        ----------
        self : NotchEvenDist
            The NotchEvenDist to build the key surfaces from
        index : int
            Index of the Notch in the list
        sym : int
            Symmetry factor (1= full machine, 2= half of the machine...)
        alpha : float
            Angle for rotation [rad]
        delta : complex
            Complex value for translation

        Returns
        -------
        surf_list : list
            list of surfaces needed to draw the keys

        """

        surf_list = []

        # Get the original surface
        Nsurf = self.notch_shape.get_surface_active()
        Nsurf.label = self.get_label() + "_" + KEY_LAB + "_R" + str(index) + "-T0-S0"
        Nsurf.rotate(angle=self.alpha)
        # Label definition
        BC_prop_right = self.get_label() + "_" + YSNR_LAB
        BC_prop_left = self.get_label() + "_" + YSNL_LAB
        # Generate all the surfaces (handle cut on sym axis)
        surf_list.extend(
            transform_hole_surf(
                hole_surf_list=[Nsurf],
                Zh=self.notch_shape.Zs,
                sym=sym,
                alpha=0,
                delta=0,
                is_split=True,
                BC_prop_right=BC_prop_right,
                BC_prop_left=BC_prop_left,
            )
        )

        # apply the transformation
        for surf in surf_list:
            if alpha != 0:
                surf.rotate(alpha)
            if delta != 0:
                surf.translate(delta)

        return surf_list

    # Inlined from Methods.Machine.NotchEvenDist.comp_periodicity_spatial
    def comp_periodicity_spatial(self):
        """Compute the periodicity factor of the notch

        Parameters
        ----------
        self : NotchEvenDist
            A NotchEvenDist object

        Returns
        -------
        per_a : int
            Number of spatial periodicities of the notch
        is_antiper_a : bool
            True if an spatial anti-periodicity is possible after the periodicities
        """

        return self.notch_shape.Zs, False

    # Inlined from Methods.Machine.NotchEvenDist.comp_surface
    def comp_surface(self):
        """Compute the surface of ALL THE NOTCHES

        Parameters
        ----------
        self : NotchEvenDist
            A NotchEvenDist object

        Returns
        -------
        Snotch : float
            surface of ALL THE NOTCHES
        """

        return self.notch_shape.Zs * self.notch_shape.comp_surface()

    # Inlined from Methods.Machine.NotchEvenDist.get_key_Ox_radius
    def get_key_Ox_radius(self):
        """Return the Key max/min radius on Ox to close the sliding band in FEMM

        Parameters
        ----------
        self : NotchEvenDist
            A NotchEvenDist object

        Returns
        -------
        ROx : Float
            Radius to use to close  the sliding band [m] (None=no intersection)
        """

        # Get all surfaces
        surf_list = self.build_geometry_key(sym=1)

        # Cut to find a surface on Ox
        Z_list = []
        for surf in surf_list:
            Z_list.extend(surf.intersect_line(0, 100))

        # No intersection => Return default radius
        if len(Z_list) == 0:
            return None

        # Get the min/max intersection on the right of Ox only
        Rright = [Z.real for Z in Z_list if Z.real > 0]
        if len(Rright) == 0:
            return None
        elif self.is_outwards():  # Outer lamination
            return min(Rright)
        else:
            return max(Rright)

    # Inlined from Methods.Machine.NotchEvenDist.get_notch_desc_list
    def get_notch_desc_list(self, sym=1):
        """Returns an ordered description of the notches

        Parameters
        ----------
        self : NotchEvenDist
            A NotchEvenDist object
        sym: int
            Number of symmetry

        Returns
        -------
        notch_desc : list
            trigo ordered list of dictionary with key:
                "begin_angle" : float [rad]
                "end_angle" : float [rad]
                "obj" : Slot (for notch_shape) / None for Radius
                "lines : lines corresponding to the radius part
                "label" : Radius/Notch/Slot
        """

        notch_list = []
        op = self.notch_shape.comp_angle_opening()
        Zs = self.notch_shape.Zs
        # No need to rotate more than a notch pitch
        alpha = self.alpha % (2 * np.pi / Zs)

        for ii in range(Zs // sym):
            notch_dict = {}
            notch_dict["begin_angle"] = 2 * np.pi / Zs * ii + alpha - op / 2
            notch_dict["end_angle"] = 2 * np.pi / Zs * ii + alpha + op / 2
            notch_dict["obj"] = self.notch_shape
            notch_dict["lines"] = self.notch_shape.build_geometry()
            # Apply rotation
            for line in notch_dict["lines"]:
                line.rotate((notch_dict["begin_angle"] + notch_dict["end_angle"]) / 2)
            notch_dict["label"] = "Notch"
            notch_list.append(notch_dict)

        # If first notch is on Ox, then sym+1 notch are required (half on both yoke side)
        if notch_list[0]["begin_angle"] < 0 and sym != 1:
            notch_dict = {}
            notch_dict["begin_angle"] = 2 * np.pi / Zs * (ii + 1) + alpha - op / 2
            notch_dict["end_angle"] = 2 * np.pi / Zs * (ii + 1) + alpha + op / 2
            notch_dict["obj"] = self.notch_shape
            notch_dict["lines"] = self.notch_shape.build_geometry()
            # Apply rotation
            for line in notch_dict["lines"]:
                line.rotate((notch_dict["begin_angle"] + notch_dict["end_angle"]) / 2)
            notch_dict["label"] = "Notch"
            notch_list.append(notch_dict)

        return notch_list
