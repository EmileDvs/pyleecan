from ....classes_common.parents import container_or_parent
from ....classes_common.errors import ParentMissingError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def get_Rext(self, lam: Lamination | None = None) -> float:
    """Return the parent lamination exterior radius

    Parameters
    ----------
    self : Hole
        A Hole object
    lam : Lamination
        Lamination of the hole (default: the parent of the hole)

    Returns
    -------
    Rext: float
        The parent lamination exterior radius [m]

    """
    lam = container_or_parent(self, lam, "lam")

    if lam is not None:
        return lam.Rext
    else:
        raise ParentMissingError("Error: The hole is not inside a Lamination")
