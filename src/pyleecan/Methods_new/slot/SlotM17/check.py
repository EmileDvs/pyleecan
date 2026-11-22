from ....classes_common.parents import container_or_parent
import numpy as np

from ..Slot import SlotCheckError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def check(self, lam: Lamination | None = None) -> None:
    """Check that the SlotM17 object is correct

    Parameters
    ----------
    self : SlotM17
        A SlotM17 object
    lam : Lamination
        Lamination of the slot (default: the parent of the slot)

    Returns
    -------
    None
    """
    lam = container_or_parent(self, lam, "lam")
    if lam is None:
        raise SlotCheckError("SlotM17 must be inside a lamination")
    if self.Zs != 2:
        raise SlotCheckError("SlotM17 must have p=1")
    if not lam.is_internal:
        raise SlotCheckError("SlotM17 must be inside an internal lamination")
