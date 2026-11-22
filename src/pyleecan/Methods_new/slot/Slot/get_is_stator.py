from ....classes_common.parents import container_or_parent
from ....classes_common.errors import ParentMissingError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def get_is_stator(self, lam: Lamination | Notch | None = None) -> bool:
    """Return True if the parent lamination is stator and False if is a rotor

    Parameters
    ----------
    self : Slot
        A Slot object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    is_stator: bool
        True if the Lamination is a stator and False if not

    """
    lam = container_or_parent(self, lam, "lam")

    if lam is not None:
        return lam.is_stator
    else:
        raise ParentMissingError("Error: The slot is not inside a Lamination")
