from ....classes_common.parents import container_or_parent
from ....classes_common.errors import ParentMissingError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def get_Rbo(self, lam: Lamination | None = None) -> float:
    """Return the parent lamination bore radius

    Parameters
    ----------
    self : Hole
        A Hole object
    lam : Lamination
        Lamination of the hole (default: the parent of the hole)

    Returns
    -------
    Rbo: float
        The parent lamination bore radius [m]

    """
    lam = container_or_parent(self, lam, "lam")

    if lam is not None:
        return lam.get_Rbo()
    else:
        raise ParentMissingError("Error: The hole is not inside a Lamination")
