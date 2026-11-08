# Experimental dataclass generated from Generator/ClassesRef/Slot/HoleUD.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass
from typing import ClassVar

import numpy as np

from ..Functions.labels import HOLEM_LAB, HOLEV_LAB, LAM_LAB
from ._error import SlotCheckError
from .hole_mag import HoleMag
from .magnet import Magnet
from .surface import Surface


@dataclass(eq=False)
class HoleUD(HoleMag):
    """User defined hole from list of surface

    Attributes
    ----------
    surf_list : [Surface] or None
        List of surface to draw the Hole. Surfaces must be ordered in trigo order, label must contain HoleMagnet for Magnet and Hole for holes
        Default: None
    magnet_dict : {Magnet} or None
        dictionary with the magnet for the Hole (None to remove magnet, key should be magnet_X)
        Default: None
    name : str or None
        Name of the hole (for save)
        Default: None
    """

    IS_SYMMETRICAL: ClassVar = 1
    surf_list: list[Surface] | None = None
    """List of surface to draw the Hole. Surfaces must be ordered in trigo order, label must contain HoleMagnet for Magnet and Hole for holes"""
    magnet_dict: dict[str, Magnet] | None = None
    """dictionary with the magnet for the Hole (None to remove magnet, key should be magnet_X)"""
    name: str | None = None
    """Name of the hole (for save)"""

    # Inlined from Methods.Slot.HoleUD.build_geometry
    def build_geometry(self, alpha=0, delta=0, is_simplified=False):
        """Compute the curve (Segment) needed to plot the Hole.
        The ending point of a curve is the starting point of the next curve in
        the list

        Parameters
        ----------
        self : HoleUD
            A HoleUD object
        alpha : float
            Angle to rotate the slot (Default value = 0) [rad]
        delta : complex
            Complex to translate the slot (Default value = 0)
        is_simplified : bool
            True to avoid line superposition (not used)

        Returns
        -------
        surf_list: list
            List of SurfLine needed to draw the Hole
        """

        surf_list = [surf.copy() for surf in self.surf_list]

        # Get correct label for surfaces
        if self.parent is not None:
            lam_label = self.parent.get_label()
        else:
            lam_label = LAM_LAB
        R_id, surf_type = self.get_R_id()
        vent_label = lam_label + "_" + surf_type + "_R" + str(R_id) + "-T"
        mag_label = lam_label + "_" + HOLEM_LAB + "_R" + str(R_id) + "-T"

        # Update surface labels
        hole_id = 0
        mag_id = 0
        for surf in surf_list:
            if HOLEM_LAB in surf.label:
                key = "magnet_" + str(mag_id)
                if key in self.magnet_dict and self.magnet_dict[key] is not None:
                    surf.label = mag_label + str(mag_id) + "-S0"
                    mag_id += 1
                else:  # Magnet disabled or not defined
                    surf.label = vent_label + str(hole_id) + "-S0"
                    hole_id += 1
            elif HOLEV_LAB in surf.label:
                surf.label = vent_label + str(hole_id) + "-S0"
                hole_id += 1

        # Apply the transformations
        # Modulo on Alpha0 for sym
        Alpha0 = self.Alpha0 % (2 * np.pi / self.Zh)
        for surf in surf_list:
            surf.rotate(alpha + Alpha0)
            surf.translate(delta)

        return surf_list

    # Inlined from Methods.Slot.HoleUD.check
    def check(self):
        """Check that the HoleUD is correctly defined"""
        if self.surf_list is None:
            self.surf_list = []
        if self.magnet_dict is None:
            self.magnet_dict = {}
        if len(self.surf_list) == 0:
            raise SlotCheckError("HoleUD must have at least one surface")
        for key in self.magnet_dict:
            if key[:7] != "magnet_":
                raise SlotCheckError(
                    "HoleUD magnet_dict must use key like 'magnet_X' with X the index of the magnet. Found: "
                    + key
                )

    # Inlined from Methods.Slot.HoleUD.comp_surface_magnet_id
    def comp_surface_magnet_id(self, index):
        """Compute the surface of the hole magnet of the corresponding index

        Parameters
        ----------
        self : HoleUD
            A HoleUD object
        index : int
            Index of the magnet to compute the surface

        Returns
        -------
        Smag: float
            Surface of the Magnet [m**2]
        """

        if self.magnet_dict is None:
            self.magnet_dict = {}

        label = "magnet_" + str(index)
        if label in self.magnet_dict:
            if self.magnet_dict[label] is None:  # Magnet disabled
                return 0
            else:
                # Find the corresponding surface
                mag_id = 0
                for surf in self.surf_list:
                    if HOLEM_LAB in surf.label and mag_id == index:
                        return surf.comp_surface()
                    elif HOLEM_LAB in surf.label:
                        mag_id += 1
                return 0

    # Inlined from Methods.Slot.HoleUD.has_magnet
    def has_magnet(self):
        """Return if the Hole has magnets

        Parameters
        ----------
        self : HoleUD
            A HoleUD object

        Returns
        -------
        has_magnet : bool
            True if the magnets are not None
        """

        has_mag = False
        if self.magnet_dict is None:
            self.magnet_dict = {}
            return False
        for value in self.magnet_dict.values():
            if value is not None:
                has_mag = True
        return has_mag

    # Inlined from Methods.Slot.HoleUD.remove_magnet
    def remove_magnet(self):
        """Remove the magnet (set to None) of the Hole

        Parameters
        ----------
        self : HoleUD
            a HoleUD object
        """

        if self.magnet_dict is None:
            self.magnet_dict = {}
        for key in self.magnet_dict.keys():
            self.magnet_dict[key] = None
