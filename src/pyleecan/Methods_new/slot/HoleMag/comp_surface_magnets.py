from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def comp_surface_magnets(self, lam: Lamination | None = None) -> float:
    """Compute the surface of all the magnet(s)

    Parameters
    ----------
    self : HoleMag
        A HoleMag object
    lam : Lamination, optional
        Lamination holding the hole (default: the parent)

    Returns
    -------
    Smag: float
        Surface of all the Magnet(s) [m**2]
    """

    mag_list = self.get_magnet_list()
    Smag = 0
    for ii in range(len(mag_list)):
        Smag += self.comp_surface_magnet_id(ii, lam=lam)
    return Smag
