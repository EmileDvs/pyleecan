from ....Functions_new.utils.labels import KEY_LAB, YSNR_LAB, YSNL_LAB

import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def build_geometry_key(self, index: int = 0, sym: int = 1, alpha: float = 0, delta: complex = 0, lam: Lamination | None = None, lam_label: str | None = None) -> list:
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

    from ....Classes_new.slot.hole import Hole
    surf_list = list()

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
