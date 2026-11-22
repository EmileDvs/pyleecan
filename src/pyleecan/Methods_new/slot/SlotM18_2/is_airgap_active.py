from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def is_airgap_active(self, lam: Lamination | Notch | None = None) -> bool:
    """Return True if a part or the full active surface is in the airgap

    Parameters
    ----------
    self : SlotM18_2
        A SlotM18_2 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    is_airgap_active : bool
        True if a part or the full active surface is in the airgap
    """

    return True
