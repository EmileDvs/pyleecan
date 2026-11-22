from ....classes_common.parents import container_or_parent
from ....classes_common.errors import ParentMissingError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def get_Ryoke(self, lam: Lamination | None = None) -> float:
    """Return the parent lamination yoke radius
    (to make lam.notch[ii].notch_shape match lam.slot parent)

    Parameters
    ----------
    self : Notch
        A Notch object
    lam : Lamination, optional
        Lamination holding the notch (default: the parent)

    Returns
    -------
    Ryoke: float
        The parent lamination yoke radius [m]

    """
    lam = container_or_parent(self, lam, "lam")

    if lam is not None:
        return lam.get_Ryoke()
    else:
        raise ParentMissingError("Error: The notch is not inside a Lamination")
