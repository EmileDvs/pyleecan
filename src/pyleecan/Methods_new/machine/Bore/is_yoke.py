from ....classes_common.parents import container_or_parent
from ....classes_common.errors import ParentMissingError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def is_yoke(self, lam: Lamination | None = None) -> bool:
    """Return if the Shape is for the Bore or Yoke radius

    Parameters
    ----------
    self : Bore
        A Bore object
    lam : Lamination, optional
        Lamination holding the bore (default: the parent)

    Returns
    -------
    is_yoke : bool
        True if the shape is on the yoke
    """
    lam = container_or_parent(self, lam, "lam")

    if lam is not None:
        return self is lam.yoke
    else:
        raise ParentMissingError("Error: The Bore object is not inside a Lamination")
