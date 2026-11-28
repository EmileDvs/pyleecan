from ....classes_common.parents import container_or_parent
from ....classes_common.errors import ParentMissingError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def get_name_lam(self, lam: Lamination | None = None, lam_label: str | None = None) -> str:
    """Return the name of the parent lamination

    Parameters
    ----------
    self : Slot
        A Slot object
    lam : Lamination
        Lamination of the slot (default: the parent of the slot)
    lam_label : str, optional
        Label of the lamination (default: lam.get_label(), which reads
        the machine holding the lamination)

    Returns
    -------
    name: string
        The name of the parent lamination

    """
    if lam_label is not None:
        return lam_label
    lam = container_or_parent(self, lam, "lam")

    if lam is not None:
        return lam.get_label()
    else:
        return "NoLam"
