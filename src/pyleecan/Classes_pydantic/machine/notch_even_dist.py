# Experimental pydantic model generated from Generator/ClassesRef/Machine/NotchEvenDist.csv
"""Generated experimental pydantic model; do not edit by hand."""

from typing import TYPE_CHECKING, ClassVar

import numpy as np
from pydantic import Field

from ...Functions_pydantic.utils.labels import KEY_LAB, YSNL_LAB, YSNR_LAB
from ..slot.hole import Hole
from ..slot.slot import Slot
from .notch import Notch

if TYPE_CHECKING:
    from .lamination import Lamination


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

    alpha: float = Field(default=0, json_schema_extra={"unit": "rad"})
    """angular positon of the first notch (0 is middle of first tooth)"""
    notch_shape: Slot = Field(default_factory=lambda: Slot())
    """Shape of the Notch"""

    _package: ClassVar[str] = "Machine"
    """Name of the package of the legacy class module"""

    # Inlined from Methods.Machine.NotchEvenDist.build_geometry_key
    def build_geometry_key(
        self,
        index: int = 0,
        sym: int = 1,
        alpha: float = 0,
        delta: complex = 0,
        lam: Lamination | None = None,
        lam_label: str | None = None,
    ) -> list:
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
        lam : Lamination, optional
            Lamination holding the notch (default: the parent)
        lam_label : str, optional
            Label of the lamination (default: the label of the notch, which
            reads the machine holding the lamination)

        Returns
        -------
        surf_list : list
            list of surfaces needed to draw the keys

        """

        surf_list = []

        # Get the original surface
        if lam_label is None:
            lam_label = self.get_label(lam=lam)
        Nsurf = self.notch_shape.get_surface_active(lam=self, lam_label=lam_label)
        Nsurf.label = lam_label + "_" + KEY_LAB + "_R" + str(index) + "-T0-S0"
        Nsurf.rotate(angle=self.alpha)
        # Label definition
        BC_prop_right = lam_label + "_" + YSNR_LAB
        BC_prop_left = lam_label + "_" + YSNL_LAB
        # Generate all the surfaces (handle cut on sym axis)
        surf_list.extend(
            Hole.transform_hole_surf(
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
    def comp_periodicity_spatial(self) -> tuple[int | None, bool]:
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
    def comp_surface(self) -> float:
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

        return self.notch_shape.Zs * self.notch_shape.comp_surface(lam=self)

    # Inlined from Methods.Machine.NotchEvenDist.get_key_Ox_radius
    def get_key_Ox_radius(self, lam: Lamination | None = None) -> float | None:
        """Return the Key max/min radius on Ox to close the sliding band in FEMM

        Parameters
        ----------
        self : NotchEvenDist
            A NotchEvenDist object
        lam : Lamination, optional
            Lamination holding the notch (default: the parent)

        Returns
        -------
        ROx : Float
            Radius to use to close  the sliding band [m] (None=no intersection)
        """

        # Get all surfaces
        surf_list = self.build_geometry_key(sym=1, lam=lam)

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
        elif self.is_outwards(lam=lam):  # Outer lamination
            return min(Rright)
        else:
            return max(Rright)

    # Inlined from Methods.Machine.NotchEvenDist.get_notch_desc_list
    def get_notch_desc_list(self, sym: int = 1) -> list:
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
        op = self.notch_shape.comp_angle_opening(lam=self)
        Zs = self.notch_shape.Zs
        # No need to rotate more than a notch pitch
        alpha = self.alpha % (2 * np.pi / Zs)

        for ii in range(Zs // sym):
            notch_dict = {}
            notch_dict["begin_angle"] = 2 * np.pi / Zs * ii + alpha - op / 2
            notch_dict["end_angle"] = 2 * np.pi / Zs * ii + alpha + op / 2
            notch_dict["obj"] = self.notch_shape
            notch_dict["lines"] = self.notch_shape.build_geometry(lam=self)
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
            notch_dict["lines"] = self.notch_shape.build_geometry(lam=self)
            # Apply rotation
            for line in notch_dict["lines"]:
                line.rotate((notch_dict["begin_angle"] + notch_dict["end_angle"]) / 2)
            notch_dict["label"] = "Notch"
            notch_list.append(notch_dict)

        return notch_list
