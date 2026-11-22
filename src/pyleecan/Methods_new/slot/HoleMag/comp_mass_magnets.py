from ....classes_common.parents import container_or_parent
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def comp_mass_magnets(self, lam: Lamination | None = None) -> float:
    """Compute the mass of the hole magnets (some of them may be missing)

    Parameters
    ----------
    self : HoleMag
        A HoleMag object
    lam : Lamination
        Lamination of the hole (default: the parent of the hole)

    Returns
    -------
    Mmag: float
        mass of the magnets [kg]
    """
    lam = container_or_parent(self, lam, "lam")

    M = 0
    mag_list = self.get_magnet_list()
    for ii, mag in enumerate(mag_list):
        if mag is not None:
            Smag = self.comp_surface_magnet_id(ii, lam=lam)
            if mag.Lmag is None:
                Lmag = lam.L1
            else:
                Lmag = mag.Lmag
            # Check material definition
            if mag.mat_type.struct.rho is None:
                raise Exception(
                    "Error: For magnet material "
                    + str(mag.mat_type.name)
                    + " struct.rho is not set"
                )
            M += Smag * Lmag * mag.mat_type.struct.rho

    return M
