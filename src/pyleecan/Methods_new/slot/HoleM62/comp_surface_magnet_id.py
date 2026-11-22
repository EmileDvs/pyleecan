from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def comp_surface_magnet_id(self, index: int, lam: Lamination | None = None) -> float:
    """Compute the surface of the hole magnet of the corresponding index

    Parameters
    ----------
    self : HoleM62
        A HoleM62 object
    index : int
        Index of the magnet to compute the surface
    lam : Lamination, optional
        Lamination holding the hole (default: the parent)

    Returns
    -------
    Smag: float
        Surface of the Magnet [m**2]
    """

    if index != 0:
        raise Exception("Only one magnet for HoleM62")
    if self.magnet_0 is not None:
        return self.comp_surface(lam=lam)  # Full magnet, no air
    return 0
