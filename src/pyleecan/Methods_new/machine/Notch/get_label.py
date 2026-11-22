from ....classes_common.parents import container_or_parent
from ....classes_common.errors import ParentMissingError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def get_label(self, is_add_id: bool = True, lam: Lamination | None = None) -> str:
    """Return the label of the lamination (Stator-0 for instance)

    Parameters
    ----------
    self : Notch
        a Notch object
    is_add_id : bool
        True to add the "-X" part
    lam : Lamination, optional
        Lamination holding the notch (default: the parent)

    Returns
    -------
    label : str
        Label of the lamination

    """
    lam = container_or_parent(self, lam, "lam")

    if lam is not None:
        return lam.get_label()
    else:
        raise ParentMissingError("Error: The notch is not inside a Lamination")
