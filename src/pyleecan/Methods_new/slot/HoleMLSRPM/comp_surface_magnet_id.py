from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def comp_surface_magnet_id(self, index: int, lam: Lamination | None = None) -> float:
    """Compute the surface of the hole magnet of the corresponding index

    Parameters
    ----------
    self : HoleMLSRPM
        A HoleMLSRPM object
    index : int
        Index of the magnet to compute the surface (the hole has one magnet)
    lam : Lamination, optional
        Lamination holding the hole (default: the parent)

    Returns
    -------
    Smag: float
        Surface of the Magnet [m**2]
    """

    if index == 0 and self.magnet_0:
        return self.comp_surface_magnet(lam=lam)
    return 0
