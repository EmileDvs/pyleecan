from ....classes_common.parents import container_or_parent
from ....Functions_new.utils.labels import WEDGE_LAB
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def get_surface_wedges(self, alpha: float = 0, delta: complex = 0, lam: Lamination | Notch | None = None) -> list:
    """Return the list of surfaces defining the wedges area of the Slot

    Parameters
    ----------
    self : Slot
        A Slot object
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
    lam = container_or_parent(self, lam, "lam")

    if hasattr(self, "wedge_type"):
        wedge_type = self.wedge_type
    else:
        wedge_type = 0

    if self.wedge_mat is None:
        return []  # No wedges

    # By default Wedge is the full opening surface
    if wedge_type == 0:
        surf_list = self.get_surface_opening(lam=lam)

    elif wedge_type == 1:
        surf_list = self.get_surface_wedge()

    else:
        raise NotImplementedError

    if lam is not None:
        # Adapt label
        lam_lab = lam.get_label()
        for surf in surf_list:
            surf.label = lam_lab + "_" + WEDGE_LAB + "_R0-T0-S0"

    # Apply transformation
    for surf in surf_list:
        surf.rotate(alpha)
        surf.translate(delta)

    return surf_list
