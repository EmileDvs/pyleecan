from ....classes_common.parents import container_or_parent
from ....Methods import ParentMissingError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def is_outwards(self, lam: Lamination | Notch | None = None) -> bool:
    """Return if the slot is outwards (on an external lamination) or inwards
    (on an internal lamination)

    Parameters
    ----------
    self : Slot
        A Slot object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    is_outwards: bool
        True if the Lamination is not internal and false if not
    """
    lam = container_or_parent(self, lam, "lam")
    if lam is not None:
        if self.is_bore in [True, None]:
            return lam.is_outwards()
        else:
            return not lam.is_outwards()
    else:
        raise ParentMissingError(
            "Error: The slot is not inside a Lamination or a Notch"
        )
