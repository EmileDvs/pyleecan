from ....classes_common.check import check_var
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def _set_W3(self, value: float, lam: Lamination | Notch | None = None) -> None:
    """setter of W3

    Parameters
    ----------
    self : SlotW11_2
        A SlotW11_2 object
    value : float
        value of W3
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)
    """

    check_var("W3", value, "float", Vmin=0)
    self.W3 = value

    # Compute W1 and W2 to match W3 tooth constraint
    try:
        self._comp_W(lam=lam)
    except Exception:
        pass
