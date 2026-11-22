import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def comp_mass_magnet(self, lam: Lamination | None = None) -> float:
    """Compute the mass of the magnet (if any)

    Parameters
    ----------
    self : HoleMLSRPM
        A HoleMLSRPM object
    lam : Lamination, optional
        Lamination holding the hole (default: the parent)

    Returns
    -------
    Mmag: float
        mass of the magnet [kg]

    """

    # Simplify the calculate of the magnet surface
    V_magnet = self.comp_volume_magnet(lam=lam)

    if self.magnet_0:
        return V_magnet * self.magnet_0.mat_type.struct.rho
    else:
        return 0
