from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def comp_surface(self, lam: Lamination | None = None) -> float:
    """Returns the area of the shape

    Parameters
    ----------
    self : Bore
        A Bore object
    lam : Lamination, optional
        Lamination holding the bore (default: the parent)

    Returns
    -------
    Sbore : float
        Area of the bore
    """

    return self.get_surface(lam=lam).comp_surface()
