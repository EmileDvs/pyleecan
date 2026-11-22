import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def comp_volume_magnet(self, lam: Lamination | None = None) -> float:
    """Compute the volume of the magnet (if any)

    Parameters
    ----------
    self : HoleMLSRPM
        A HoleMLSRPM object
    lam : Lamination, optional
        Lamination holding the hole (default: the parent)

    Returns
    -------
    Vmag: float
        Volume of the magnet [m**3]

    """
    S_magnet = self.comp_surface_magnet(lam=lam)

    if self.magnet_0:
        return S_magnet * self.magnet_0.Lmag
    else:
        return 0
