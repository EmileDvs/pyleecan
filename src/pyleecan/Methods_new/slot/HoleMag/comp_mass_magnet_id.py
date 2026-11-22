from ....classes_common.parents import container_or_parent
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def comp_mass_magnet_id(self, index: int, lam: Lamination | None = None) -> float:
    """Compute the mass of the hole magnet of the corresponding index

    Parameters
    ----------
    self : HoleMag
        A HoleMag object
    index : int
        Index of the magnet to compute the surface
    lam : Lamination
        Lamination of the hole (default: the parent of the hole)

    Returns
    -------
    Mmag: float
        Mass of the Magnet [m**2]
    """
    lam = container_or_parent(self, lam, "lam")

    mag_list = self.get_magnet_list()
    if mag_list[index] is None:
        return 0
    else:
        if mag_list[index].Lmag is None:
            Lmag = lam.L1
        else:
            Lmag = mag_list[index].Lmag
        return self.comp_surface_magnet_id(index) * Lmag
