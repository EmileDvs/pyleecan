from ....classes_common.parents import container_or_parent
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def comp_volume_magnets(self, lam: Lamination | None = None) -> float:
    """Compute the volume of the hole magnets (some of them may be missing)

    Parameters
    ----------
    self : HoleMag
        A HoleMag object
    lam : Lamination
        Lamination of the hole (default: the parent of the hole)

    Returns
    -------
    Vmag: float
        volume of the magnets [m**3]
    """
    lam = container_or_parent(self, lam, "lam")

    V = 0
    mag_list = self.get_magnet_list()
    for ii, mag in enumerate(mag_list):
        if mag is not None:
            Smag = self.comp_surface_magnet_id(ii, lam=lam)
            if mag.Lmag is None:
                Lmag = lam.L1
            else:
                Lmag = mag.Lmag
            V += Smag * Lmag

    return V
