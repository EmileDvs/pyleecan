from ....classes_common.parents import container_or_parent
from ....classes_common.errors import ParentMissingError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def get_Rbo(self, lam: Lamination | Notch | None = None) -> float:
    """Return the parent lamination bore radius

    Parameters
    ----------
    self : Slot
        A Slot object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    Rbo: float
        The parent lamination bore radius [m]

    """
    lam = container_or_parent(self, lam, "lam")

    if lam is not None:
        if self.is_bore in [True, None]:
            return lam.get_Rbo()
        else:
            return lam.get_Ryoke()
    else:
        raise ParentMissingError("Error: The slot is not inside a Lamination")
