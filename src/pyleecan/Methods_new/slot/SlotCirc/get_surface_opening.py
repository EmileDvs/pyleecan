from ....Classes_new.geometry.surf_line import SurfLine
from ....Functions_new.labels import SOP_LAB, DRAW_PROP_LAB


def get_surface_opening(self, alpha: float = 0, delta: complex = 0) -> list:
    """Return the list of surfaces defining the opening area of the Slot

    Parameters
    ----------
    self : SlotCirc
        A SlotCirc object
    alpha : float
        float number for rotation (Default value = 0) [rad]
    delta : complex
        complex number for translation (Default value = 0)

    Returns
    -------
    surf_list : list
        list of surfaces objects
    """

    # No opening surface in SlotCirc
    return []
