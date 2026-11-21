from ....Classes_new.geometry.surf_line import SurfLine
from ....Functions_new.labels import SOP_LAB, DRAW_PROP_LAB
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def get_surface_opening(self, alpha: float = 0, delta: complex = 0, lam: Lamination | Notch | None = None) -> list:
    """Return the list of surfaces defining the opening area of the Slot

    Parameters
    ----------
    self : SlotW24
        A SlotW24 object
    alpha : float
        float number for rotation (Default value = 0) [rad]
    delta : complex
        complex number for translation (Default value = 0)
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    surf_list : list
        list of surfaces objects
    """

    # No opening surface in SlotW14
    return []
