from ....classes_common.parents import container_or_parent
from ....classes_common.errors import ParentMissingError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def is_outwards(self, lam: Lamination | None = None) -> bool:
    """Return if the notch is outwards (on an external lamination) or inwards
    (on an internal lamination).
    (to make lam.notch[ii].notch_shape match lam.slot parent)

    Parameters
    ----------
    self : Notch
        A Notch object
    lam : Lamination, optional
        Lamination holding the notch (default: the parent)

    Returns
    -------
    is_outwards: bool
        True if the Lamination is not internal and false if not. For yoke notch,
        result is negated.
    """
    lam = container_or_parent(self, lam, "lam")
    if lam is not None:
        return lam.is_outwards()
    else:
        raise ParentMissingError("Error: The notch is not inside a Lamination")
